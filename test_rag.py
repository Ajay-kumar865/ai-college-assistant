from rag.qdrant_db import QdrantDB

def debug_retrieval():
    qdrant = QdrantDB()
    results = qdrant.search("Who is the Vice Chancellor of Guru Jambheshwar University?", limit=5)
    print("Found chunks:")
    for r in results:
        print("-" * 40)
        print("Score:", r.get('score'))
        print("Text:", r.get('text')[:300])

if __name__ == "__main__":
    debug_retrieval()
