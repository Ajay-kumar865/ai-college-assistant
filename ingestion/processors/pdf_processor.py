from pathlib import Path
from ingestion.extract_pdf import extract_pdf_text


def process_pdf(path: Path) -> str:
    return extract_pdf_text(path)
