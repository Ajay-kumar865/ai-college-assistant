import requests
from ingestion.extract_html import extract_html_text


def process_html(url: str) -> str:
    response = requests.get(url, timeout=15)
    response.raise_for_status()

    html = response.text
    return extract_html_text(html)
