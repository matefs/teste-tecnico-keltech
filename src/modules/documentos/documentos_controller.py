# Arquivo: src/modules/documentos/documentos_controller.py
from typing import Annotated

from fastapi import Depends, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.connection import get_db_session
from src.modules.documentos.documentos_repository import DocumentRepository
from src.modules.documentos.documentos_schemas import (
    DocumentListResponse,
    DocumentStatsResponse,
    DocumentUploadResponse,
)
from src.modules.documentos.documentos_service import DocumentQueryService, DocumentUploadService


def get_document_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> DocumentRepository:
    return DocumentRepository(session)


def get_document_upload_service(
    repository: Annotated[DocumentRepository, Depends(get_document_repository)],
) -> DocumentUploadService:
    return DocumentUploadService(repository)


def get_document_query_service(
    repository: Annotated[DocumentRepository, Depends(get_document_repository)],
) -> DocumentQueryService:
    return DocumentQueryService(repository)


async def upload_document(
    file: UploadFile,
    service: Annotated[DocumentUploadService, Depends(get_document_upload_service)],
) -> DocumentUploadResponse:
    return await service.upload_document(file)


async def get_document_stats(
    service: Annotated[DocumentQueryService, Depends(get_document_query_service)],
) -> DocumentStatsResponse:
    return await service.get_stats()


async def list_documents(
    service: Annotated[DocumentQueryService, Depends(get_document_query_service)],
    page: Annotated[int, Query(ge=1, description="Número da página")] = 1,
    per_page: Annotated[int, Query(ge=1, le=100, description="Itens por página")] = 20,
) -> DocumentListResponse:
    return await service.list_documents(page=page, per_page=per_page)
