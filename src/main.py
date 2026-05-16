# Arquivo: src/main.py
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src.infrastructure.database.connection import engine
from src.infrastructure.database.models import Base
from src.modules.documentos.documentos_router import router as documentos_router

logging.basicConfig(level=logging.INFO)

FRONTEND_DIST_DIR = Path(__file__).resolve().parent / "frontend" / "dist"
FRONTEND_ASSETS_DIR = FRONTEND_DIST_DIR / "assets"


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield


app = FastAPI(title="Keltech Document Management", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
