# Arquivo: src/worker/ocr_service.py
import logging
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_ocr_engine = None


def initialize_ocr_engine() -> None:
    _get_ocr_engine()


def _get_ocr_engine():
    global _ocr_engine
    if _ocr_engine is None:
        from paddleocr import PaddleOCR
        logger.info("Inicializando PaddleOCR (primeira execução pode demorar para baixar modelos)...")
        _ocr_engine = PaddleOCR(use_angle_cls=True, lang="pt", show_log=False)
        logger.info("PaddleOCR inicializado.")
    return _ocr_engine


def _ocr_image_bytes(image_bytes: bytes) -> tuple[str, float]:
    import cv2
    import numpy as np

    ocr = _get_ocr_engine()
    array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_COLOR)

    results = ocr.ocr(image, cls=True)

    texts: list[str] = []
    confidences: list[float] = []
    for line in results or []:
        for item in line or []:
            texts.append(item[1][0])
            confidences.append(float(item[1][1]))

    raw_text = "\n".join(texts)
    mean_confidence = sum(confidences) / len(confidences) if confidences else 0.0
    return raw_text, mean_confidence


def _process_pdf(file_path: Path) -> tuple[str, float, int]:
    import fitz

    doc = fitz.open(str(file_path))
    page_texts: list[str] = []
    page_confidences: list[float] = []

    for page in doc:
        pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
        text, confidence = _ocr_image_bytes(pix.tobytes("png"))
        page_texts.append(text)
        page_confidences.append(confidence)

    raw_text = "\n\n--- Página ---\n\n".join(page_texts)
    mean_confidence = sum(page_confidences) / len(page_confidences) if page_confidences else 0.0
    return raw_text, mean_confidence, doc.page_count


def _process_png(file_path: Path) -> tuple[str, float, int]:
    raw_text, confidence = _ocr_image_bytes(file_path.read_bytes())
    return raw_text, confidence, 1


def run_ocr(file_path: Path, mime_type: str) -> dict[str, Any]:
    start = time.monotonic()

    if mime_type == "application/pdf":
        raw_text, confidence, pages = _process_pdf(file_path)
    else:
        raw_text, confidence, pages = _process_png(file_path)

    return {
        "raw_text": raw_text,
        "confidence_score": round(confidence, 4),
        "processing_time_seconds": round(time.monotonic() - start, 3),
        "page_count": pages,
    }
