from PIL import Image
import pytesseract
from pathlib import Path


def extract_image_text(path: Path) -> str:
    image = Image.open(path)
    return pytesseract.image_to_string(image)
