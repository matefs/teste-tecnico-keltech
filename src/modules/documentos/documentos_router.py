# Arquivo: src/modules/documentos/documentos_router.py
from fastapi import APIRouter

from src.modules.documentos.documentos_controller import upload_document
from src.modules.documentos.documentos_schemas import DocumentUploadResponse

router = APIRouter(prefix="/documentos", tags=["Documentos"])

router.add_api_route(
    "/",
    upload_document,
    methods=["POST"],
    status_code=201,
    response_model=DocumentUploadResponse,
    summary="Upload de documento para OCR",
    description="Recebe um arquivo PDF ou PNG, salva em volume Docker e enfileira para processamento OCR.",
)
