# Arquivo: src/worker/main.py
import asyncio
import json
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import aio_pika
from aio_pika.abc import AbstractIncomingMessage
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config.settings import settings
from src.worker.extractor import extract_structured_data
from src.worker.ocr_service import initialize_ocr_engine, run_ocr

QUEUE_NAME = "Documentos_para_OCR"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [ocr_worker] %(name)s: %(message)s",
)
logger = logging.getLogger("ocr_worker")

_engine = create_async_engine(settings.DATABASE_URL, echo=False)
_session_factory = async_sessionmaker(_engine, expire_on_commit=False)
_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="ocr")


async def _update_status(session: AsyncSession, document_id: str, status: str) -> None:
    await session.execute(
        text("UPDATE documents SET status = :status WHERE id = :id::uuid"),
        {"status": status, "id": document_id},
    )
    await session.commit()


async def _save_content(
    session: AsyncSession,
    document_id: str,
    raw_text: str,
    extracted_data: dict,
    confidence_score: float,
    processing_time_seconds: float,
) -> None:
    await session.execute(
        text("""
            INSERT INTO document_contents
                (id, document_id, raw_text, extracted_data, confidence_score, processing_time_seconds, created_at)
            VALUES
                (:id::uuid, :document_id::uuid, :raw_text, :extracted_data::jsonb,
                 :confidence_score, :processing_time_seconds, :created_at)
        """),
        {
            "id": str(uuid.uuid4()),
            "document_id": document_id,
            "raw_text": raw_text,
            "extracted_data": json.dumps(extracted_data),
            "confidence_score": confidence_score,
            "processing_time_seconds": processing_time_seconds,
            "created_at": datetime.now(timezone.utc),
        },
    )
    await session.commit()


async def _process_message(message: AbstractIncomingMessage) -> None:
    async with message.process(requeue=False):
        payload = json.loads(message.body.decode())
        document_id: str = payload["document_id"]
        file_path_str: str = payload["file_path"]
        mime_type: str = payload["mime_type"]

        started_at = datetime.now(timezone.utc)
        logger.info("Iniciando | document_id=%s file=%s mime=%s", document_id, file_path_str, mime_type)

        try:
            async with _session_factory() as session:
                await _update_status(session, document_id, "processing")
            logger.info("Status -> processing | document_id=%s", document_id)

            file_path = Path(file_path_str)
            if not file_path.exists():
                raise FileNotFoundError(f"Arquivo não encontrado: {file_path_str}")
            logger.info("Arquivo localizado (%.1f KB) | document_id=%s", file_path.stat().st_size / 1024, document_id)

            logger.info("Executando OCR em thread | document_id=%s", document_id)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(_executor, run_ocr, file_path, mime_type)
            logger.info(
                "OCR concluído | document_id=%s confiança=%.3f páginas=%d tempo=%.2fs",
                document_id, result["confidence_score"], result["page_count"], result["processing_time_seconds"],
            )

            extracted_data = extract_structured_data(result["raw_text"])
            logger.info("Dados extraídos | document_id=%s cpfs=%d datas=%d", document_id, len(extracted_data.get("cpfs", [])), len(extracted_data.get("dates", [])))

            async with _session_factory() as session:
                await _save_content(
                    session,
                    document_id=document_id,
                    raw_text=result["raw_text"],
                    extracted_data=extracted_data,
                    confidence_score=result["confidence_score"],
                    processing_time_seconds=result["processing_time_seconds"],
                )
                await _update_status(session, document_id, "done")

            try:
                file_path.unlink()
                logger.info("Arquivo removido | path=%s", file_path_str)
            except OSError as unlink_error:
                logger.warning("Falha ao remover arquivo | path=%s erro=%s", file_path_str, unlink_error)

            duration = (datetime.now(timezone.utc) - started_at).total_seconds()
            logger.info("Finalizado | document_id=%s status=done duração_total=%.2fs", document_id, duration)

        except Exception as error:
            duration = (datetime.now(timezone.utc) - started_at).total_seconds()
            logger.error(
                "FALHA | document_id=%s duração=%.2fs erro=%s",
                document_id, duration, error, exc_info=True,
            )
            try:
                async with _session_factory() as session:
                    await _update_status(session, document_id, "error")
                logger.info("Status -> error | document_id=%s", document_id)
            except Exception as db_error:
                logger.error("Falha ao gravar status=error | document_id=%s erro=%s", document_id, db_error)


async def main() -> None:
    logger.info("=" * 60)
    logger.info("OCR Worker iniciando")
    logger.info("=" * 60)

    logger.info("Pré-carregando motor PaddleOCR (aguarde, pode baixar modelos na primeira vez)...")
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(_executor, initialize_ocr_engine)
        logger.info("Motor OCR pronto.")
    except Exception as ocr_init_error:
        logger.error("Falha ao inicializar PaddleOCR: %s", ocr_init_error, exc_info=True)
        logger.error("Documentos serão marcados como 'error' até que o OCR seja corrigido.")

    logger.info("Conectando ao RabbitMQ...")
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)
    queue = await channel.declare_queue(QUEUE_NAME, durable=True)

    await queue.consume(_process_message)
    logger.info("Consumindo fila=%s | aguardando mensagens...", QUEUE_NAME)
    logger.info("=" * 60)
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
