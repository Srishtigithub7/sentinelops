from pathlib import Path
import re

import faiss
from sentence_transformers import SentenceTransformer


class KnowledgeRetriever:
    """
    Simple local RAG retrieval engine for SentinelOps.

    It:
    1. Loads operational knowledge
    2. Splits documents into chunks
    3. Creates embeddings
    4. Stores embeddings in FAISS
    5. Retrieves the most relevant chunks for an incident
    """

    def __init__(self, knowledge_dir: str):

        self.knowledge_dir = Path(knowledge_dir)

        # Small, fast local embedding model.
        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        self.chunks = []
        self.index = None

    def load_documents(self):
        """Load Markdown knowledge documents."""

        documents = []

        for file_path in self.knowledge_dir.glob("*.md"):

            text = file_path.read_text(
                encoding="utf-8"
            )

            documents.append(
                {
                    "source": file_path.name,
                    "text": text
                }
            )

        return documents

    def split_document(
        self,
        text: str,
        source: str
    ):
        """
        Split a document using Markdown headings.
        """

        sections = re.split(
            r"\n(?=## )",
            text
        )

        chunks = []

        for section in sections:

            section = section.strip()

            if not section:
                continue

            chunks.append(
                {
                    "text": section,
                    "source": source
                }
            )

        return chunks

    def build_index(self):
        """Create the FAISS vector index."""

        documents = self.load_documents()

        self.chunks = []

        for document in documents:

            document_chunks = self.split_document(
                document["text"],
                document["source"]
            )

            self.chunks.extend(
                document_chunks
            )

        if not self.chunks:
            raise ValueError(
                "No knowledge documents found."
            )

        texts = [
            chunk["text"]
            for chunk in self.chunks
        ]

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True
        )

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(
            dimension
        )

        self.index.add(
            embeddings
        )

    def search(
        self,
        query: str,
        top_k: int = 3
    ):
        """
        Retrieve the most relevant knowledge chunks.
        """

        if self.index is None:
            self.build_index()

        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True
        )

        scores, indices = self.index.search(
            query_embedding,
            min(top_k, len(self.chunks))
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0]
        ):

            chunk = self.chunks[index]

            results.append(
                {
                    "score": float(score),
                    "source": chunk["source"],
                    "text": chunk["text"]
                }
            )

        return results


if __name__ == "__main__":

    knowledge_path = (
        "data/runbooks"
    )

    retriever = KnowledgeRetriever(
        knowledge_path
    )

    query = (
        "Database connection pool is exhausted "
        "and API requests are returning 503 errors"
    )

    print()
    print("=" * 60)
    print("           SENTINELOPS KNOWLEDGE RETRIEVAL")
    print("=" * 60)

    results = retriever.search(
        query,
        top_k=3
    )

    print()

    for number, result in enumerate(
        results,
        start=1
    ):

        print(
            f"[{number}] "
            f"Similarity: {result['score']:.3f}"
        )

        print(
            f"Source: {result['source']}"
        )

        print()

        print(result["text"])

        print()
        print("-" * 60)