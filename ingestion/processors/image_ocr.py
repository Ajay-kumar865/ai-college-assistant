from pathlib import Path
from ingestion.extract_text import extract_image_text


def process_image(path: Path) -> str:
    return extract_image_text(path)
