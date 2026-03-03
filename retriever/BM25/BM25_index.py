import os
import pickle
from typing import List, Dict
from rank_bm25 import BM25Okapi


class BM25Index:
    def __init__(self, data_dir: str, index_path: str):
        self.data_dir = data_dir
        self.index_path = index_path
        self.documents: List[str] = []
        self.doc_names: List[str] = []
        self.bm25: BM25Okapi | None = None

    def _tokenize(self, text: str) -> List[str]:
        return text.lower().split()

    def load_documents(self) -> None:
        files = os.listdir(self.data_dir)

        for file in files:
            if file.endswith(".txt"):
                path = os.path.join(self.data_dir, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        self.documents.append(content)
                        self.doc_names.append(file)

    def build(self) -> None:
        if not self.documents:
            raise ValueError("No documents loaded for BM25 indexing")

        from langchain_text_splitters import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )

        chunked_docs = []
        chunked_names = []

        for doc, name in zip(self.documents, self.doc_names):
            chunks = splitter.split_text(doc)
            for c in chunks:
                chunked_docs.append(c)
                # Keep track of the source file for the chunk
                chunked_names.append(name)

        # Replace original large docs with chunked versions
        self.documents = chunked_docs
        self.doc_names = chunked_names

        tokenized_docs = [self._tokenize(doc) for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized_docs)

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        with open(self.index_path, "wb") as f:
            pickle.dump(
                {
                    "bm25": self.bm25,
                    "documents": self.documents,
                    "doc_names": self.doc_names,
                },
                f,
            )

    def load(self) -> None:
        with open(self.index_path, "rb") as f:
            data = pickle.load(f)
            self.bm25 = data["bm25"]
            self.documents = data["documents"]
            self.doc_names = data["doc_names"]

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        if not self.bm25:
            raise RuntimeError("BM25 index is not loaded")

        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)

        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]

        results = []
        for idx, score in ranked:
            results.append(
                {
                    "document": self.documents[idx],
                    "source": self.doc_names[idx],
                    "score": float(score),
                }
            )

        return results
