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


class DocumentListItem(BaseModel):
    id: UUID
    status: DocumentStatus
    original_filename: str
    mime_type: str
    file_size: int
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    items: list[DocumentListItem]


class DocumentStatsResponse(BaseModel):
    total: int
    por_status: dict[str, int]


class DocumentContentResponse(BaseModel):
    id: UUID
    document_id: UUID
    raw_text: str | None
    extracted_data: dict | None
    confidence_score: float | None
    processing_time_seconds: float | None
    created_at: datetime

    model_config = {"from_attributes": True}
