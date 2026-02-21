from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import logging

logger = logging.getLogger(__name__)

_COLLECTION_NAME = "university_docs"


class QdrantDB:
    def __init__(self, host: str = "localhost", port: int = 6333):
        self.client = QdrantClient(host=host, port=port)
        self._ensure_collection()

    def _ensure_collection(self):
        collections = self.client.get_collections().collections
        if not any(c.name == _COLLECTION_NAME for c in collections):
            self.client.create_collection(
                collection_name=_COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=384,  # placeholder (MiniLM size later)
                    distance=Distance.COSINE,
                ),
            )
            logger.info("Qdrant collection created")
        else:
            logger.info("Qdrant collection already exists")

    def health_check(self) -> bool:
        try:
            self.client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return False
