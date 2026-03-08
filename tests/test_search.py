import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.rag.vector_store import AgriAgentVectorStore


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_search.py <query>")
        print('Example: python test_search.py "What is the optimal irrigation strategy?"')
        return

    query = " ".join(sys.argv[1:])
    print(f"Initializing Vector Store...")
    store = AgriAgentVectorStore(persist_directory="data/chroma_db")

    print(f"Searching for: '{query}'\n")
    results = store.search(query, n_results=3)

    if not results or not results.get("documents") or not results["documents"][0]:
        print("No results found.")
        return

    for i, (doc, metadata) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
        print("=" * 60)
        print(f"RESULT {i+1} (Source: {metadata.get('source', 'Unknown')})")
        print("=" * 60)
        # Limit to 500 characters so terminal doesn't flood
        print(doc[:800] + "\n...\n")


if __name__ == "__main__":
    main()
