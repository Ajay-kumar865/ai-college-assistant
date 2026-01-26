from pathlib import Path
from ingestion.extract_doc import extract_doc_text


def process_docx(path: Path) -> str:
    return extract_doc_text(path)
