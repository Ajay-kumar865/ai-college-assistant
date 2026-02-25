from ingestion.crawler.url_manager import URLManager
from ingestion.crawler.robots_handler import RobotsHandler
import requests
from requests.exceptions import Timeout, RequestException
from urllib.parse import urlparse
import time
import os


SEED_URLS = [
    "https://gjust.ac.in"
]

TIMEOUT_FILE = "timeout_urls.txt"
REQUEST_TIMEOUT = 15


# ==============================
# Timeout URL Handling
# ==============================

def load_failed_urls():
    if not os.path.exists(TIMEOUT_FILE):
        return set()

    with open(TIMEOUT_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())


def append_failed_url(url):
    with open(TIMEOUT_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\n")


# ==============================
# Main Crawl Function
# ==============================

def crawl_site(max_pages: int = 500) -> list[str]:

    domain = urlparse(SEED_URLS[0]).netloc
    url_manager = URLManager(domain)
    robots = RobotsHandler()

    failed_urls = load_failed_urls()

    # Add seed URLs if queue empty
    if not url_manager.has_next():
        for url in SEED_URLS:
            if url not in failed_urls:
                url_manager.add_url(url)

    collected = []
    processed_count = 0

    # 🔥 Use session (faster, connection pooling)
    session = requests.Session()

    while url_manager.has_next() and processed_count < max_pages:

        url = url_manager.get_next()

        if url in failed_urls:
            continue

        if not robots.allowed(url):
            continue

        try:
            response = session.get(url, timeout=REQUEST_TIMEOUT)

            if response.status_code != 200:
                continue

            content_type = response.headers.get("content-type", "").lower()

            print(f"Crawling ({processed_count+1}/{max_pages}): {url}")

            # HTML
            if "text/html" in content_type:
                url_manager.extract_links(response.text, base_url=url)
                collected.append(url)
                processed_count += 1

            # PDF
            elif "application/pdf" in content_type or url.lower().endswith(".pdf"):
                collected.append(url)
                processed_count += 1

            # Save state every 50 pages (less disk pressure)
            if processed_count % 50 == 0:
                url_manager.save_state()
                print("State saved.")

            time.sleep(0.5)

        except Timeout:
            print(f"Timeout occurred: {url}")
            failed_urls.add(url)
            append_failed_url(url)

        except RequestException as e:
            print(f"Request failed: {url} | {e}")
            failed_urls.add(url)
            append_failed_url(url)

        except Exception as e:
            print(f"Unexpected error crawling {url}: {e}")
            failed_urls.add(url)
            append_failed_url(url)

    # Final save (only once)
    if processed_count % 50 != 0:
        url_manager.save_state()

    session.close()

    if not url_manager.has_next():
        print("\nCrawl Complete: Entire Website Crawled.")
    else:
        print("\nCrawl Complete: Max page limit reached.")

    print(f"Total Pages Crawled This Run: {processed_count}")
    print("Exiting crawl_site() cleanly.")

    return collected
