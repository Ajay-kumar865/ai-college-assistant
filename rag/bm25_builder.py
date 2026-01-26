import json
from pathlib import Path
from retriever.BM25.BM25_index import BM25Index

# ---- absolute project root ----
BASE_DIR = Path(__file__).resolve().parents[1]

SRC_FILE = BASE_DIR / "storage" / "ingestion" / "documents.jsonl"
DATA_DIR = BASE_DIR / "storage" / "raw" / "bootstrap"
BM25_INDEX_PATH = str(BASE_DIR / "storage" / "BM25" / "bm25.pkl")


def build_bm25():
    if not SRC_FILE.exists():
        raise RuntimeError("documents.jsonl not found")

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # ---- write txt files ----
    for p in DATA_DIR.glob("*.txt"):
        p.unlink()  # clear old files to avoid confusion

    with SRC_FILE.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            obj = json.loads(line)
            text = obj.get("text", "").strip()
            if text:
                (DATA_DIR / f"doc_{i}.txt").write_text(text, encoding="utf-8")

    # ---- build bm25 ----
    bm25 = BM25Index(
        data_dir=str(DATA_DIR),
        index_path=BM25_INDEX_PATH,
    )

    bm25.load_documents()

    # 🔒 HARD ASSERT (THIS IS THE KEY)
    if not bm25.documents:
        raise RuntimeError(
            f"BM25 loaded ZERO documents from {DATA_DIR}. "
            f"Files present: {list(DATA_DIR.glob('*.txt'))}"
        )

    bm25.build()
    bm25.save()


if __name__ == "__main__":
    build_bm25()
