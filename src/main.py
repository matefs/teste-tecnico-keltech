import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.infrastructure.rabbitmq.connection import close_rabbitmq_connection
from src.infrastructure.rabbitmq.consumer import start_ocr_consumer

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    consumer_task = asyncio.create_task(start_ocr_consumer())
    yield
    consumer_task.cancel()
    await close_rabbitmq_connection()


app = FastAPI(title="Keltech Document Management", lifespan=lifespan)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
