import json

import pika

conn = pika.BlockingConnection(pika.URLParameters("amqp://keltech:keltech@localhost:5672/"))
ch = conn.channel()
ch.queue_declare(queue="Documentos_para_OCR", durable=True)

mensagens = [
    {"document_id": "58c0d7f0-5964-4f7d-9905-87320b5572b9", "file_path": "uploads/2026/05/659eda65-f3b4-4e91-896f-0c1a089e7668.pdf", "mime_type": "application/pdf"},
    {"document_id": "ddd69210-4eb7-47d4-aa3e-3d2e1a43c970", "file_path": "uploads/2026/05/08bf34f8-a065-4748-a892-117736d63ade.png", "mime_type": "image/png"},
    {"document_id": "1845ddca-a12e-4811-af8b-8360f354a302", "file_path": "uploads/2026/05/4d89e727-25d8-45b2-9c76-1e1381dc0966.png", "mime_type": "image/png"},
    {"document_id": "179e8411-0112-418c-b78e-5624429b8d67", "file_path": "uploads/2026/05/e0d35155-b4d9-4757-bbbb-dcab76c07326.png", "mime_type": "image/png"},
    {"document_id": "a9badae0-9f47-40f2-be1d-3fd130502c6d", "file_path": "uploads/2026/05/c7544298-27b4-4e61-9001-3019e7c5d054.png", "mime_type": "image/png"},
    {"document_id": "e1d5a41c-3b47-4d18-bf6b-ddab65f81f76", "file_path": "uploads/2026/05/f2a92b14-05b6-4a25-b5ee-3d4151cdbcfb.png", "mime_type": "image/png"},
    {"document_id": "a07d2121-4633-4d59-a191-ec7262372c44", "file_path": "uploads/2026/05/4692c8ea-77d1-4667-a0a5-e90b98d9c89c.png", "mime_type": "image/png"},
]

for msg in mensagens:
    ch.basic_publish(
        exchange="",
        routing_key="Documentos_para_OCR",
        body=json.dumps(msg).encode(),
        properties=pika.BasicProperties(delivery_mode=2),
    )
    print(f"Publicado: {msg['document_id']}")

conn.close()
print("Done — 7 mensagens na fila.")
