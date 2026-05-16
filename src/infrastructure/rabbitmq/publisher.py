import json
from uuid import UUID

import aio_pika

from src.infrastructure.rabbitmq.connection import get_rabbitmq_connection

QUEUE_NAME = "Documentos_para_OCR"


async def publish_document_for_ocr(document_id: UUID, file_path: str, mime_type: str) -> None:
    connection = await get_rabbitmq_connection()

    async with connection.channel() as channel:
        queue = await channel.declare_queue(QUEUE_NAME, durable=True)

        payload = json.dumps(
            {
                "document_id": str(document_id),
                "file_path": file_path,
                "mime_type": mime_type,
            }
        ).encode()

        await channel.default_exchange.publish(
            aio_pika.Message(
                body=payload,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=queue.name,
        )
