import json
from pathlib import Path
from rag.qdrant_db import QdrantDB

DATA_PATH = Path("storage/ingestion/documents.jsonl")


def main():

    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Data file not found: {DATA_PATH}")

    docs = []

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                docs.append(json.loads(line))

    if not docs:
        print("No documents found.")
        return

    print(f"Loaded {len(docs)} documents")

    qdrant = QdrantDB()
    qdrant.upsert_documents(docs)

    print("✅ Upload to Qdrant completed")


if __name__ == "__main__":
    main()