# rag/vector_store.py

from typing import List, Dict, Any
import logging

from db.qdrant_client import QdrantDB

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Thin abstraction over Qdrant.
    Embeddings are intentionally not implemented yet.
    """

    def __init__(self):
        self.db = QdrantDB()

    def is_ready(self) -> bool:
        """
        Returns True if vector store backend is reachable.
        Does NOT imply embeddings exist.
        """
        return self.db.health_check()

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filters: Dict[str, Any] | None = None,
    ) -> List[Dict[str, Any]]:
        """
        Placeholder vector search.
        Will be implemented once embeddings are added.
        """
        logger.warning("Vector search called but embeddings are not implemented yet")
        return []

    def upsert(
        self,
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]],
        ids: List[str] | None = None,
    ) -> None:
        """
        Placeholder upsert.
        Will be implemented during ingestion phase.
        """
        logger.warning("Vector upsert called but embeddings are not implemented yet")
