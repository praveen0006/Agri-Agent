import os
import sys

# Ensure we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.rag.document_parser import parse_pdf_to_markdown
from src.rag.chunking import chunk_document_with_context
from src.rag.vector_store import AgriAgentVectorStore


def ingest_papers(papers_dir="data/papers", db_dir="data/chroma_db"):
    """
    Reads all PDF files in the specify directory, parses them into markdown,
    chunks them with appropriate global context, and stores them in Chroma.
    """
    if not os.path.exists(papers_dir):
        print(f"Directory {papers_dir} does not exist. Create it and add PDFs.")
        return

    pdf_files = [f for f in os.listdir(papers_dir) if f.endswith(".pdf")]

    if not pdf_files:
        print(f"No PDFs found in {papers_dir}.")
        return

    print(f"Found {len(pdf_files)} PDFs in {papers_dir}. Initializing Vector Store...")
    store = AgriAgentVectorStore(persist_directory=db_dir)

    for filename in pdf_files:
        filepath = os.path.join(papers_dir, filename)
        print(f"\nProcessing: {filename}...")

        try:
            # 1. Parse PDF to Markdown
            print("  - Extracting text & tables...")
            md_text = parse_pdf_to_markdown(filepath)

            # 2. You can dynamically generate or ask for this context.
            # For automation, we use the filename as a basic context proxy.
            clean_name = filename.replace(".pdf", "").replace("_", " ")
            global_context = f"Research paper regarding {clean_name}"

            # 3. Chunk
            print("  - Chunking document...")
            chunks = chunk_document_with_context(
                markdown_text=md_text, global_context=global_context, source_name=filename
            )

            # 4. Store
            print("  - Storing in Vector Database...")
            store.add_documents(chunks)
            print(f"  -> Successfully ingested {filename}.")

        except Exception as e:
            print(f"  -> Error processing {filename}: {e}")

    print("\nIngestion complete! All papers are now available to the Agent.")


def ingest_single_paper(filepath, db_dir="data/chroma_db"):
    """Ingests a single PDF file into the vector store."""
    store = AgriAgentVectorStore(persist_directory=db_dir)
    filename = os.path.basename(filepath)

    # 1. Parse
    md_text = parse_pdf_to_markdown(filepath)

    # 2. Context
    clean_name = filename.replace(".pdf", "").replace("_", " ")
    global_context = f"Research paper regarding {clean_name}"

    # 3. Chunk
    chunks = chunk_document_with_context(markdown_text=md_text, global_context=global_context, source_name=filename)

    # 4. Store
    store.add_documents(chunks)
    return len(chunks)


if __name__ == "__main__":
    ingest_papers()
