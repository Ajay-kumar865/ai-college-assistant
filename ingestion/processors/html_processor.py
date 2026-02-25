import requests
from bs4 import BeautifulSoup


def process_html(url: str):

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        if "text/html" not in response.headers.get("content-type", ""):
            return ""

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove scripts & styles
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

        return text

    except Exception as e:
        print(f"Failed to process HTML {url}: {e}")
        return ""
