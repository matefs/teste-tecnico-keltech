# Arquivo: src/modules/documentos/documentos_controller.py
from typing import Annotated

from fastapi import Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.connection import get_db_session
from src.modules.documentos.documentos_repository import DocumentRepository
from src.modules.documentos.documentos_schemas import DocumentUploadResponse
from src.modules.documentos.documentos_service import DocumentUploadService


def get_document_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> DocumentRepository:
    return DocumentRepository(session)


def get_document_upload_service(
    repository: Annotated[DocumentRepository, Depends(get_document_repository)],
) -> DocumentUploadService:
    return DocumentUploadService(repository)


async def upload_document(
    file: UploadFile,
    service: Annotated[DocumentUploadService, Depends(get_document_upload_service)],
) -> DocumentUploadResponse:
    return await service.upload_document(file)
