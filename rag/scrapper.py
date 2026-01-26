# rag/scraper.py

import requests
from bs4 import BeautifulSoup
from pathlib import Path

RAW_DATA_DIR = Path("data/raw")
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Educational Project)"
}

def scrape_page(url: str, filename: str):
    response = response = requests.get(
    url,
    headers=HEADERS,
    timeout=10,
    verify=False
)

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove scripts, styles, and noscript tags
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    clean_text = "\n".join(
        line.strip() for line in text.splitlines() if line.strip()
    )

    file_path = RAW_DATA_DIR / filename
    file_path.write_text(clean_text, encoding="utf-8")

    print(f"Saved: {file_path}")

if __name__ == "__main__":
    scrape_page(
        "https://gjuonline.ac.in/gjust/student/",
        "hostel_info.txt"
    )
