# Arquivo: src/modules/documentos/documentos_repository.py
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.models import Document


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
