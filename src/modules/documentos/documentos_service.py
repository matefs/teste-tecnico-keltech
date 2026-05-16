# Arquivo: src/modules/documentos/documentos_service.py
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException, UploadFile

from src.config.settings import settings
from src.infrastructure.rabbitmq.publisher import publish_document_for_ocr
from src.modules.documentos.documentos_repository import DocumentRepository
from src.infrastructure.database.models import DocumentContent
from src.modules.documentos.documentos_schemas import (
    DocumentContentResponse,
    DocumentListItem,
    DocumentListResponse,
    DocumentStatsResponse,
    DocumentStatus,
    DocumentUploadResponse,
)

_MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024
_PDF_MAGIC = b"%PDF"
_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
_ALLOWED_EXTENSIONS = {".pdf", ".png"}


def _detect_mime_type_from_content(content: bytes) -> str:
    if content[:4] == _PDF_MAGIC:
        return "application/pdf"
    if content[:8] == _PNG_MAGIC:
        return "image/png"
    raise HTTPException(
        status_code=415,
        detail="Conteúdo inválido. O arquivo não é um PDF nem um PNG.",
    )


def _build_upload_path(original_filename: str) -> tuple[Path, str]:
    today = datetime.now(timezone.utc)
    suffix = Path(original_filename).suffix.lower()
    unique_name = f"{uuid.uuid4()}{suffix}"

    relative_path = Path(settings.UPLOADS_DIR) / str(today.year) / f"{today.month:02d}" / unique_name
    relative_path.parent.mkdir(parents=True, exist_ok=True)

    return relative_path, str(relative_path)


class DocumentUploadService:
    def __init__(self, repository: DocumentRepository) -> None:
        self._repository = repository

    async def upload_document(self, file: UploadFile) -> DocumentUploadResponse:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Nenhum arquivo enviado.")

        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in _ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=415,
                detail="Extensão não permitida. Apenas .pdf e .png são aceitos.",
            )

        content = await file.read()

        if len(content) == 0:
            raise HTTPException(status_code=400, detail="O arquivo enviado está vazio.")

        if len(content) > _MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail="Arquivo excede o limite máximo de 25 MB.",
            )

        mime_type = _detect_mime_type_from_content(content)

        absolute_path, relative_path = _build_upload_path(file.filename)
        absolute_path.write_bytes(content)

        document = await self._repository.create_document(
            original_filename=file.filename,
            file_path=relative_path,
            mime_type=mime_type,
            file_size=len(content),
        )

        await publish_document_for_ocr(
            document_id=document.id,
            file_path=relative_path,
            mime_type=mime_type,
        )

        return DocumentUploadResponse.model_validate(document)


class DocumentQueryService:
    def __init__(self, repository: DocumentRepository) -> None:
        self._repository = repository

    async def get_stats(self) -> DocumentStatsResponse:
        total = await self._repository.get_total_count()
        counts_by_status = await self._repository.count_by_status()

        por_status = {status.value: counts_by_status.get(status.value, 0) for status in DocumentStatus}

        return DocumentStatsResponse(total=total, por_status=por_status)

    async def get_document_content(self, document_id: uuid.UUID) -> DocumentContent | None:
        return await self._repository.get_document_content(document_id)

    async def list_documents(self, page: int, per_page: int) -> DocumentListResponse:
        offset = (page - 1) * per_page
        total = await self._repository.get_total_count()
        documents = await self._repository.list_documents(limit=per_page, offset=offset)

        return DocumentListResponse(
            total=total,
            page=page,
            per_page=per_page,
            items=[DocumentListItem.model_validate(doc) for doc in documents],
        )
