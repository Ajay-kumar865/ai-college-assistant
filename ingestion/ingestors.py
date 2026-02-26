import requests
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from ingestion.processors.html_processor import process_html
from ingestion.processors.pdf_processor import process_pdf


def ingest_item(item: str | dict):

    item_url = item if isinstance(item, str) else item.get("url", "")

    if is_url(item_url):

        try:
            response = requests.get(item_url, timeout=20)
            response.raise_for_status()

            content_type = response.headers.get("content-type", "").lower()

            # PDF
            if "application/pdf" in content_type or item_url.lower().endswith(".pdf"):

                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(response.content)
                    tmp_path = tmp.name

                metadata = {
                    "source": "pdf",
                    "url": item_url,
                }
                if isinstance(item, dict):
                    metadata["discovered_links"] = item.get("discovered_links", [])
                return process_pdf(Path(tmp_path)), metadata

            # HTML
            if "text/html" in content_type:
                text = process_html(item_url)
                metadata = {
                    "source": "html",
                    "url": item_url,
                }
                if isinstance(item, dict):
                    metadata["discovered_links"] = item.get("discovered_links", [])
                return text, metadata

            return "", {}

        except Exception as e:
            print(f"Failed to ingest {item_url}: {e}")
            return "", {}

    raise ValueError(f"Unsupported ingestion item: {item}")


def is_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return bool(parsed.scheme and parsed.netloc)
    except Exception:
        return False
