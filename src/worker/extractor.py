# Arquivo: src/worker/extractor.py
import re
from typing import Any

_CPF = re.compile(r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b')
_CNPJ = re.compile(r'\b\d{2}\.?\d{3}\.?\d{3}[/\\]?\d{4}-?\d{2}\b')
_DATE = re.compile(r'\b\d{2}[/.\-]\d{2}[/.\-]\d{4}\b|\b\d{4}-\d{2}-\d{2}\b')
_PHONE = re.compile(r'\(?\d{2}\)?\s?9?\d{4}[\-\s]?\d{4}\b')
_EMAIL = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')
_CEP = re.compile(r'\b\d{5}-\d{3}\b')
_CURRENCY = re.compile(r'R\$\s?\d{1,3}(?:\.\d{3})*(?:,\d{2})?')


def extract_structured_data(text: str) -> dict[str, Any]:
    return {
        "cpfs": sorted(set(_CPF.findall(text))),
        "cnpjs": sorted(set(_CNPJ.findall(text))),
        "dates": sorted(set(_DATE.findall(text))),
        "phones": sorted(set(_PHONE.findall(text))),
        "emails": sorted(set(_EMAIL.findall(text))),
        "ceps": sorted(set(_CEP.findall(text))),
        "valores": sorted(set(_CURRENCY.findall(text))),
    }
