import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.chunking import chunk_document_with_context
from src.rag.vector_store import AgriAgentVectorStore


def main():
    print("Initializing Vector Store...")
    store = AgriAgentVectorStore(persist_directory="data/test_chroma_db")

    # Mock Document
    sample_paper = """# Cotton Irrigation Study
    
## Abstract
This paper discusses the irrigation scheduling for cotton in semi-arid soils, focusing on loamy soil characteristics.

## Field Capacity
The field capacity of cotton soil is generally observed to be around 22% to 25% volumetric water content for loamy types. If the moisture exceeds this, water may be lost to deep percolation.

## Wilting Point
It is critical to avoid water stress during the flowering stage. The wilting point for cotton in loamy soil ranges from 12% to 15% moisture. Below this, the plant experiences severe stress and potential yield loss.
"""

    global_context = "Paper studying irrigation scheduling for cotton in semi-arid soils."

    print("Chunking document...")
    chunks = chunk_document_with_context(
        markdown_text=sample_paper, global_context=global_context, source_name="cotton_irrigation_study.md"
    )

    for c in chunks:
        print(f"--- Chunk ---\n{c.content}\n---")

    print("\nAdding to vector store...")
    store.add_documents(chunks)

    print("\n--- Test Queries ---")
    queries = ["What is the field capacity of cotton soil?", "What moisture level causes wilting in loamy soil?"]

    for q in queries:
        print(f"\nQuery: {q}")
        res = store.search(q, n_results=1)
        if res and res["documents"] and res["documents"][0]:
            print(f"Top result:\n{res['documents'][0][0]}")
        else:
            print("No results found.")


if __name__ == "__main__":
    main()
