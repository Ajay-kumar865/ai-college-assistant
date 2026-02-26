from typing import Optional, List, Dict

from retriever.BM25.BM25_index import BM25Index
from rag.config import RETRIEVAL_MODE, RetrievalMode
from rag.qdrant_db import QdrantDB


DATA_DIR = "storage/raw/bootstrap"
BM25_INDEX_PATH = "storage/BM25/bm25.pkl"


class RAGRetriever:
    def __init__(self):
        self.bm25 = BM25Index(data_dir=DATA_DIR, index_path=BM25_INDEX_PATH)
        self.vector_store = QdrantDB()
        self._load_bm25()

    def _load_bm25(self):
        try:
            self.bm25.load()
        except FileNotFoundError as exc:
            raise RuntimeError(
                "BM25 index not found. Build the index before running retrieval."
            ) from exc

    def retrieve(self, query: str, top_k: int = 3) -> Dict[str, List[str] | str]:
        if RETRIEVAL_MODE == RetrievalMode.BM25:
            return self._bm25_retrieve(query, top_k)

        if RETRIEVAL_MODE == RetrievalMode.VECTOR:
            return self._vector_retrieve(query, top_k)

        if RETRIEVAL_MODE == RetrievalMode.HYBRID:
            return self._hybrid_retrieve(query, top_k)

        raise ValueError(f"Unknown retrieval mode: {RETRIEVAL_MODE}")

    # -------- Retrieval strategies -------- #
    def _bm25_retrieve(self, query: str, top_k: int) -> Dict[str, List[str] | str]:
        results = self.bm25.search(query, top_k=top_k)
        context = self._format_results(results, source="BM25")
        sources = [r.get("source") for r in results if r.get("source")]

        return {
            "context": context,
            "sources": sources,
        }

    def _vector_retrieve(self, query: str, top_k: int) -> Dict[str, List[str] | str]:
        results = self.vector_store.search(query, limit=top_k)

        normalized = [
            {
                "document": r.get("text", ""),
                "source": r.get("url", ""),
            }
            for r in results
        ]

        context = self._format_results(normalized, source="VECTOR")
        sources = [r.get("source") for r in normalized if r.get("source")]

        return {
            "context": context,
            "sources": sources,
        }

    def _hybrid_retrieve(self, query: str, top_k: int) -> Dict[str, List[str] | str]:
        bm25_result = self._bm25_retrieve(query, top_k)
        vector_result = self._vector_retrieve(query, top_k)

        context = bm25_result["context"] + "\n\n" + vector_result["context"]
        sources = list(set(bm25_result["sources"] + vector_result["sources"]))

        return {
            "context": context,
            "sources": sources,
        }

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


def retrieve(query: str, top_k: int = 3):
    global _retriever

    if _retriever is None:
        _retriever = RAGRetriever()

    return _retriever.retrieve(query, top_k)
