from bs4 import BeautifulSoup


def extract_html_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # REMOVE ONLY NON-CONTENT TAGS
    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)
    return text
