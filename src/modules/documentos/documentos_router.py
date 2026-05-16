# Arquivo: src/modules/documentos/documentos_router.py
from fastapi import APIRouter

from src.modules.documentos.documentos_controller import (
    get_document_content,
    get_document_stats,
    list_documents,
    upload_document,
)
from src.modules.documentos.documentos_schemas import (
    DocumentContentResponse,
    DocumentListResponse,
    DocumentStatsResponse,
    DocumentUploadResponse,
)

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

router.add_api_route(
    "/stats",
    get_document_stats,
    methods=["GET"],
    response_model=DocumentStatsResponse,
    summary="Totais por etapa de processamento",
    description="Retorna o total de documentos enviados e a contagem por status.",
)

router.add_api_route(
    "/",
    list_documents,
    methods=["GET"],
    response_model=DocumentListResponse,
    summary="Listar documentos",
    description="Lista todos os documentos enviados com paginação. Ordenados do mais recente ao mais antigo.",
)

router.add_api_route(
    "/{document_id}/conteudo",
    get_document_content,
    methods=["GET"],
    response_model=DocumentContentResponse,
    summary="Resultado OCR do documento",
    description="Retorna o texto extraído, dados estruturados (CPFs, datas, etc.) e métricas do processamento OCR.",
)
