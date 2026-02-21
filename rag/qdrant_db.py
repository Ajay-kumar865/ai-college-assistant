import logging
import uuid
from typing import List, Dict
_COLLECTION_NAME = "university_docs"
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

_COLLECTION_NAME = "university_docs"
_VECTOR_SIZE = 384   # all-MiniLM-L6-v2


class QdrantDB:
    def __init__(self, host: str = "localhost", port: int = 6333):
        # connect
        self.client = QdrantClient(host=host, port=port)

        # embedding model (loads once)
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

        # ensure collection
        self._ensure_collection()

    # ---------------------------
    # CREATE COLLECTION IF NEEDED
    # ---------------------------
    def _ensure_collection(self):
        collections = self.client.get_collections().collections

        if not any(c.name == _COLLECTION_NAME for c in collections):
            self.client.create_collection(
                collection_name=_COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=_VECTOR_SIZE,
                    distance=Distance.COSINE,
                ),
            )
            logger.info("Qdrant collection created")
        else:
            logger.info("Qdrant collection already exists")

    # ---------------------------
    # HEALTH CHECK
    # ---------------------------
    def health_check(self) -> bool:
        try:
            self.client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return False
    def search(self, query: str, limit: int = 5):

        q_vector = self.embedder.encode(query).tolist()

        results = self.client.query_points(
            collection_name=_COLLECTION_NAME,
            query=q_vector,
            limit=limit
        )

        return [point.payload for point in results.points]

        
    # ---------------------------
    # UPSERT DOCUMENTS
    # ---------------------------
    def upsert_documents(self, docs: list, batch_size: int = 64):

        total = len(docs)
        logger.info(f"Uploading {total} documents to Qdrant")

        for i in range(0, total, batch_size):
            batch = docs[i:i + batch_size]

            texts = [d["text"] for d in batch]
            embeddings = self.embedder.encode(texts)

            points = []

            for doc, vec in zip(batch, embeddings):
                points.append({
                    "id": str(uuid.uuid4()),
                    "vector": vec.tolist(),
                    "payload": {
                        "text": doc["text"],
                        "url": doc.get("url", "")
                    }
                })

            self.client.upsert(
                collection_name=_COLLECTION_NAME,
                points=points
            )

            logger.info(f"Uploaded batch {i + len(batch)} / {total}")


# ---------------------------
# QUICK LOCAL TEST
# ---------------------------
if __name__ == "__main__":

    qdb = QdrantDB()

    print("Health:", qdb.health_check())

    sample_docs = [
        {
            "text": "Hostel application process for first year students",
            "url": "hostel"
        },
        {
            "text": "Admission procedure for engineering courses",
            "url": "admission"
        }
    ]

    qdb.upsert_documents(sample_docs)

    res = qdb.search("how to apply hostel")

    for r in res:
        print(r)