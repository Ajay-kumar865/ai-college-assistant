from pathlib import Path
from urllib.parse import urlparse

from ingestion.processors.html_processor import process_html
from ingestion.processors.pdf_processor import process_pdf
from ingestion.processors.docx_processor import process_docx
from ingestion.processors.image_ocr import process_image


def ingest_item(item: str):
    if is_url(item):
        text = process_html(item)
        return text, {
            "source": "html",
            "url": item,
        }

    path = Path(item)

    if path.suffix.lower() == ".pdf":
        return process_pdf(path), {"source": "pdf", "path": str(path)}

    if path.suffix.lower() in [".docx", ".doc"]:
        return process_docx(path), {"source": "docx", "path": str(path)}

    if path.suffix.lower() in [".png", ".jpg", ".jpeg"]:
        return process_image(path), {"source": "image", "path": str(path)}

    raise ValueError(f"Unsupported ingestion item: {item}")


def is_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return bool(parsed.scheme and parsed.netloc)
    except Exception:
        return False
