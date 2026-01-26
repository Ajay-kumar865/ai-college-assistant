from typing import Optional, List, Dict
import logging

from retriever.BM25.BM25_index import BM25Index
from rag.vector_store import VectorStore
from rag.config import RETRIEVAL_MODE, RetrievalMode

logger = logging.getLogger(__name__)

DATA_DIR = "storage/raw/bootstrap"
BM25_INDEX_PATH = "storage/BM25/bm25.pkl"


class RAGRetriever:
    def __init__(self):
        self.bm25 = BM25Index(data_dir=DATA_DIR, index_path=BM25_INDEX_PATH)
        self.vector_store = None  # 🔒 lazy initialization
        self._load_bm25()

    def _load_bm25(self):
        try:
            self.bm25.load()
        except FileNotFoundError:
            raise RuntimeError(
                "BM25 index not found. Build the index before running retrieval."
            )

    def retrieve(self, query: str, top_k: int = 3):
        if RETRIEVAL_MODE == RetrievalMode.BM25:
            context, sources = self._bm25_retrieve(query, top_k)
            return {
                "context": context,
                "sources": sources,
            }

        elif RETRIEVAL_MODE == RetrievalMode.VECTOR:
            return self._vector_retrieve(query, top_k)

        elif RETRIEVAL_MODE == RetrievalMode.HYBRID:
            return self._hybrid_retrieve(query, top_k)

        else:
            raise ValueError(f"Unknown retrieval mode: {RETRIEVAL_MODE}")

    # -------- Retrieval strategies -------- #

    def _bm25_retrieve(self, query: str, top_k: int):
        results = self.bm25.search(query, top_k=top_k)

        context = self._format_results(results, source="BM25")
        sources = list({r.get("source") for r in results if r.get("source")})

        return context, sources

        return self._format_results(results, source="BM25")

    def _vector_retrieve(self, query: str, top_k: int) -> str:
        if self.vector_store is None:
            self.vector_store = VectorStore()  # initialized ONLY when needed

        results = self.vector_store.search(query, top_k)
        return self._format_results(results, source="VECTOR")

    def _hybrid_retrieve(self, query: str, top_k: int) -> str:
        bm25_ctx = self._bm25_retrieve(query, top_k)

        if self.vector_store is None:
            self.vector_store = VectorStore()

        vector_ctx = self._vector_retrieve(query, top_k)

        return bm25_ctx + "\n\n" + vector_ctx

    # -------- Formatting -------- #

    def _format_results(self, results: List[Dict], source: str) -> str:
        if not results:
            return ""

        chunks = []
        for r in results:
            chunks.append(f"[{source} | {r.get('source')}]\n{r.get('document')}")

        return "\n\n".join(chunks)


# Singleton accessor
_retriever: Optional[RAGRetriever] = None


def retrieve(query: str, top_k: int = 3) -> str:
    global _retriever

    if _retriever is None:
        _retriever = RAGRetriever()

    return _retriever.retrieve(query, top_k)
