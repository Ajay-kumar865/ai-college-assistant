import json
from pathlib import Path

from ingestion.crawler.crawl_site import crawl_site
from ingestion.ingestors import ingest_item
from ingestion.textcleaner import clean_text

OUTPUT_FILE = Path("storage/ingestion/documents.jsonl")
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)


def run():
    items = crawl_site()

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        for item in items:
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

            except Exception:
                continue


if __name__ == "__main__":
    run()
