import chromadb
from langchain_huggingface import HuggingFaceEmbeddings
from typing import List
from src.rag.chunking import DocumentChunk


class AgriAgentVectorStore:
    def __init__(self, persist_directory: str = "data/chroma_db"):
        self.persist_directory = persist_directory
        # bge-small-en-v1.5 is lightweight, strong retrieval benchmarks, CPU friendly
        self.embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")

        # Initialize chroma client
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        self.collection = self.client.get_or_create_collection(name="agri_knowledge")

    def add_documents(self, chunks: List[DocumentChunk]):
        """
        Embeds and stores document chunks in Chroma DB.
        """
        if not chunks:
            return

        texts = [chunk.content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]

        # We need IDs for Chroma
        ids = [f"{m.get('source', 'unknown')}_chunk_{m.get('chunk_index', i)}" for i, m in enumerate(metadatas)]

        # Embed using the HuggingFace model
        embeddings = self.embedding_model.embed_documents(texts)

        self.collection.add(embeddings=embeddings, documents=texts, metadatas=metadatas, ids=ids)
        print(f"Added {len(chunks)} chunks to vector store.")

    def search(self, query: str, n_results: int = 3):
        """
        Searches the vector store for the most relevant chunks.
        """
        query_embedding = self.embedding_model.embed_query(query)

        results = self.collection.query(query_embeddings=[query_embedding], n_results=n_results)

        return results


if __name__ == "__main__":
    # Test
    store = AgriAgentVectorStore()
    from src.rag.chunking import DocumentChunk

    test_chunks = [
        DocumentChunk(
            content="[GLOBAL CONTEXT]\nCotton growing tests\n\n[CONTENT]\nWilting point for cotton in loamy soil ranges from 12% to 15% moisture.",
            metadata={"source": "test", "chunk_index": 0},
        )
    ]
    store.add_documents(test_chunks)

    res = store.search("What moisture level causes wilting in loamy soil?")
    print("Search result:", res["documents"][0])
