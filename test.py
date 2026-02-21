from rag.qdrant_db import QdrantDB

print("Creating Qdrant client...")
q = QdrantDB()
print("Connected.")

print("Running search...")
res = q.search("hostel admission")

print(f"Got {len(res)} results")

for r in res:
    print(r["text"][:200])