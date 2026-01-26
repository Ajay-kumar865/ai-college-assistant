# rag/config.py

from enum import Enum


class RetrievalMode(str, Enum):
    BM25 = "bm25"
    VECTOR = "vector"
    HYBRID = "hybrid"


# 🔒 Default: DO NOT CHANGE until embeddings exist
RETRIEVAL_MODE = RetrievalMode.BM25
