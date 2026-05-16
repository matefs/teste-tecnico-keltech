# Arquivo: src/main.py
import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src.infrastructure.database.connection import engine
from src.infrastructure.database.models import Base
from src.infrastructure.rabbitmq.connection import close_rabbitmq_connection
from src.infrastructure.rabbitmq.consumer import start_ocr_consumer
from src.modules.documentos.documentos_router import router as documentos_router

logging.basicConfig(level=logging.INFO)

FRONTEND_DIST_DIR = Path(__file__).resolve().parent / "frontend" / "dist"
FRONTEND_ASSETS_DIR = FRONTEND_DIST_DIR / "assets"


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    consumer_task = asyncio.create_task(start_ocr_consumer())
    try:
        yield
    finally:
        consumer_task.cancel()
        await close_rabbitmq_connection()


app = FastAPI(title="Keltech Document Management", lifespan=lifespan)

app.include_router(documentos_router)

if FRONTEND_ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_ASSETS_DIR), name="frontend-assets")


@app.get("/", include_in_schema=False)
async def serve_frontend_root():
    index_path = FRONTEND_DIST_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return JSONResponse({"status": "ok"})


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}


@app.get("/{full_path:path}", include_in_schema=False)
async def serve_frontend_routes(full_path: str):
    if full_path.startswith(("documentos", "health", "docs", "openapi.json", "redoc")):
        return JSONResponse({"detail": "Not Found"}, status_code=404)

    index_path = FRONTEND_DIST_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return JSONResponse({"detail": "Frontend build not available"}, status_code=404)
