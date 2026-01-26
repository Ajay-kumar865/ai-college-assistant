from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


class URLManager:
    def __init__(self):
        self.queue = []
        self.visited = set()

    def add_url(self, url: str):
        if url not in self.visited and url not in self.queue:
            self.queue.append(url)

    def has_next(self) -> bool:
        return len(self.queue) > 0

    def get_next(self) -> str:
        url = self.queue.pop(0)
        self.visited.add(url)
        return url

    def extract_links(self, html: str, base_url: str):
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup.find_all("a", href=True):
            href = tag["href"]
            full_url = urljoin(base_url, href)

            parsed = urlparse(full_url)
            if parsed.scheme in ("http", "https"):
                self.add_url(full_url)
