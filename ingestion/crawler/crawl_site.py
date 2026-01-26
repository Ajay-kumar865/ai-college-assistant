from ingestion.crawler.url_manager import URLManager
from ingestion.crawler.robots_handler import RobotsHandler
import requests


SEED_URLS = [
    "https://example.com",
    # "https://gjust.ac.in"
]


def crawl_site(max_pages: int = 2) -> list[str]:
    """
    Returns a list of URLs to ingest.
    """
    url_manager = URLManager()
    robots = RobotsHandler()

    for url in SEED_URLS:
        url_manager.add_url(url)

    collected = []

    while url_manager.has_next() and len(collected) < max_pages:
        url = url_manager.get_next()

        # IMPORTANT: always allow SEED_URLS
        if url not in SEED_URLS and not robots.allowed(url):
            continue

        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                continue

            content_type = response.headers.get("content-type", "").lower()

            if "text/html" in content_type:
                collected.append(url)
                url_manager.extract_links(response.text, base_url=url)

            elif "application/pdf" in content_type:
                collected.append(url)

        except Exception:
            continue

    return collected
