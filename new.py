from rag.retriever import retrieve

print(retrieve("hostel", top_k=2))
print(retrieve("admission", top_k=2))
