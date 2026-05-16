# Arquivo: src/modules/documentos/documentos_schemas.py
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class DocumentStatus(StrEnum):
    QUEUED = "queued"
    PROCESSING = "processing"
    DONE = "done"
    ERROR = "error"


class DocumentUploadResponse(BaseModel):
    id: UUID
    status: DocumentStatus
    original_filename: str
    file_path: str
    mime_type: str
    file_size: int
    created_at: datetime

    model_config = {"from_attributes": True}
