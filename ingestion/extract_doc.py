from docx import Document
from pathlib import Path


def extract_doc_text(path: Path) -> str:
    doc = Document(path)
    return " ".join(p.text for p in doc.paragraphs)
