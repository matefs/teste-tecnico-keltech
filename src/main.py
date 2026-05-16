# Arquivo: src/main.py
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.infrastructure.database.connection import engine
from src.infrastructure.database.models import Base
from src.infrastructure.rabbitmq.connection import close_rabbitmq_connection
from src.infrastructure.rabbitmq.consumer import start_ocr_consumer
from src.modules.documentos.documentos_router import router as documentos_router

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    consumer_task = asyncio.create_task(start_ocr_consumer())
    yield
    consumer_task.cancel()
    await close_rabbitmq_connection()


app = FastAPI(title="Keltech Document Management", lifespan=lifespan)

app.include_router(documentos_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
