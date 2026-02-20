import json
from pathlib import Path

from ingestion.crawler.crawl_site import crawl_site
from ingestion.ingestors import ingest_item
from ingestion.textcleaner import clean_text


PROCESSED_FILE = Path("storage/ingestion/processed_urls.json")
OUTPUT_FILE = Path("storage/ingestion/documents.jsonl")

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)


def load_processed():
    if not PROCESSED_FILE.exists():
        return set()

    try:
        content = PROCESSED_FILE.read_text().strip()
        if not content:
            return set()
        return set(json.loads(content))
    except json.JSONDecodeError:
        print("⚠ processed_urls.json is empty or corrupted. Resetting...")
        return set()



def save_processed(processed):
    PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROCESSED_FILE.write_text(json.dumps(list(processed)))


def run():
    processed_urls = load_processed()

    # Crawl 500 pages per run
    items = crawl_site(max_pages=500)

    with OUTPUT_FILE.open("a", encoding="utf-8") as f:

        for item in items:

            if item in processed_urls:
                continue

            try:
                raw_text, metadata = ingest_item(item)

                if not raw_text:
                    continue

                text = clean_text(raw_text)

                if not text:
                    continue

                record = {
                    "text": text,
                    **metadata,
                }

                f.write(json.dumps(record, ensure_ascii=False) + "\n")

                processed_urls.add(item)
                save_processed(processed_urls)

            except Exception as e:
                print(f"Error ingesting {item}: {e}")
                continue


if __name__ == "__main__":
    run()
