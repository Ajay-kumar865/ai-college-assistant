import fitz  # PyMuPDF
from pathlib import Path


def extract_pdf_text(path: Path) -> str:
    doc = fitz.open(path)
    pages = []

    for page in doc:
        pages.append(page.get_text())

    return " ".join(pages)
