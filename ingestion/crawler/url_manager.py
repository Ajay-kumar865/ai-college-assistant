from urllib.parse import urljoin, urlparse, urlunparse
from bs4 import BeautifulSoup
import json
from pathlib import Path
from collections import deque


STATE_FILE = Path("storage/ingestion/crawl_state.json")


class URLManager:
    def __init__(self, allowed_domain: str):
        self.allowed_domain = allowed_domain
        self.queue = deque()
        self.visited = set()
        self.load_state()

    def normalize_url(self, url: str) -> str:
        parsed = urlparse(url)
        cleaned = parsed._replace(fragment="", query="")
        normalized = urlunparse(cleaned).rstrip("/")
        return normalized

    def save_state(self):
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with STATE_FILE.open("w", encoding="utf-8") as f:
            json.dump({
                "queue": list(self.queue),
                "visited": list(self.visited),
            }, f)

    def load_state(self):
        if STATE_FILE.exists():
            with STATE_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
                self.queue = deque(data.get("queue", []))
                self.visited = set(data.get("visited", []))

    def _is_allowed_url(self, url: str) -> bool:
        parsed = urlparse(url)

        # Allow only same domain
        if parsed.netloc != self.allowed_domain:
            return False

        # Ignore useless file types
        blocked_ext = [
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".css",
            ".js",
            ".zip",
            ".rar",
            ".svg",
            ".mp4",
        ]
        if any(url.lower().endswith(ext) for ext in blocked_ext):
            return False

        return True

    def add_url(self, url: str):
        url = self.normalize_url(url)

        if not self._is_allowed_url(url):
            return

        if url not in self.visited and url not in self.queue:
            self.queue.append(url)

    def has_next(self) -> bool:
        return len(self.queue) > 0

    def get_next(self) -> str:
        url = self.queue.popleft()
        self.visited.add(url)
        return url

    def extract_links(self, html: str, base_url: str) -> list[str]:
        soup = BeautifulSoup(html, "html.parser")
        discovered: list[str] = []

        for tag in soup.find_all("a", href=True):
            href = tag["href"]
            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)

            if parsed.scheme in ("http", "https"):
                normalized = self.normalize_url(full_url)
                if self._is_allowed_url(normalized):
                    discovered.append(normalized)
                    self.add_url(normalized)

        # Preserve order, de-duplicate
        return list(dict.fromkeys(discovered))
