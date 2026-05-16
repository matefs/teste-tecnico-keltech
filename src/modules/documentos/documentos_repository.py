# Arquivo: src/modules/documentos/documentos_repository.py
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.models import Document, DocumentContent


class DocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_document(
        self,
        original_filename: str,
        file_path: str,
        mime_type: str,
        file_size: int,
    ) -> Document:
        document = Document(
            id=uuid.uuid4(),
            original_filename=original_filename,
            file_path=file_path,
            mime_type=mime_type,
            file_size=file_size,
            status="queued",
            created_at=datetime.now(timezone.utc),
        )
        self._session.add(document)
        await self._session.commit()
        await self._session.refresh(document)
        return document

    async def get_total_count(self) -> int:
        result = await self._session.execute(select(func.count(Document.id)))
        return result.scalar_one()

    async def count_by_status(self) -> dict[str, int]:
        result = await self._session.execute(
            select(Document.status, func.count(Document.id)).group_by(Document.status)
        )
        return {status: count for status, count in result.all()}

    async def list_documents(self, limit: int, offset: int) -> list[Document]:
        result = await self._session.execute(
            select(Document).order_by(Document.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def get_document_content(self, document_id: uuid.UUID) -> DocumentContent | None:
        result = await self._session.execute(
            select(DocumentContent).where(DocumentContent.document_id == document_id)
        )
        return result.scalar_one_or_none()
