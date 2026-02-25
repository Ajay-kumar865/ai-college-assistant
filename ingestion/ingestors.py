import requests
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from ingestion.processors.html_processor import process_html
from ingestion.processors.pdf_processor import process_pdf


def ingest_item(item: str):

    if is_url(item):

        try:
            response = requests.get(item, timeout=20)
            response.raise_for_status()

            content_type = response.headers.get("content-type", "").lower()

            # PDF
            if "application/pdf" in content_type or item.lower().endswith(".pdf"):

                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(response.content)
                    tmp_path = tmp.name

                return process_pdf(Path(tmp_path)), {
                    "source": "pdf",
                    "url": item,
                }

            # HTML
            if "text/html" in content_type:
                text = process_html(item)
                return text, {
                    "source": "html",
                    "url": item,
                }

            return "", {}

        except Exception as e:
            print(f"Failed to ingest {item}: {e}")
            return "", {}

    raise ValueError(f"Unsupported ingestion item: {item}")


def is_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return bool(parsed.scheme and parsed.netloc)
    except Exception:
        return False
