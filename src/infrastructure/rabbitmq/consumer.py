import asyncio
import json
import logging

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from src.infrastructure.rabbitmq.connection import get_rabbitmq_connection

QUEUE_NAME = "Documentos_para_OCR"

logger = logging.getLogger(__name__)


async def _process_ocr_message(message: AbstractIncomingMessage) -> None:
    async with message.process(requeue=True):
        payload = json.loads(message.body.decode())

        document_id = payload["document_id"]
        file_path = payload["file_path"]
        mime_type = payload["mime_type"]

        logger.info("Processando OCR | document_id=%s file=%s", document_id, file_path)

        # TODO: injetar OCR service e chamar aqui
        # await ocr_service.process(document_id, file_path, mime_type)


async def start_ocr_consumer() -> None:
    connection = await get_rabbitmq_connection()

    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)

    queue = await channel.declare_queue(QUEUE_NAME, durable=True)

    logger.info("Consumidor iniciado | fila=%s", QUEUE_NAME)

    await queue.consume(_process_ocr_message)
    await asyncio.Future()  # mantém o consumer rodando
