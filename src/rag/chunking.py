from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List


class DocumentChunk:
    def __init__(self, content: str, metadata: dict = None):
        self.content = content
        self.metadata = metadata or {}

    def __repr__(self):
        return f"<DocumentChunk(metadata={self.metadata})>\n{self.content[:100]}..."


def chunk_document_with_context(
    markdown_text: str, global_context: str, source_name: str, chunk_size: int = 500, chunk_overlap: int = 50
) -> List[DocumentChunk]:
    """
    Splits markdown text into chunks and prepends the global context to each chunk.
    This helps the retriever understand the overall topic even for small chunks.
    """

    # We use character splitter here because the inputs are already markdown from pymupdf4llm
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap, separators=["\n\n", "\n", " ", ""]
    )

    raw_chunks = splitter.split_text(markdown_text)

    formatted_chunks = []

    for i, chunk in enumerate(raw_chunks):
        # Format required by PRD
        formatted_content = f"[GLOBAL CONTEXT]\n{global_context}\n\n[CONTENT]\n{chunk}"

        metadata = {"source": source_name, "chunk_index": i}

        formatted_chunks.append(DocumentChunk(content=formatted_content, metadata=metadata))

    return formatted_chunks


if __name__ == "__main__":
    # Test script
    sample_md = "# Introduction\n\nWilting point for cotton in loamy soil ranges from 12% to 15% moisture."
    context = "Paper studying irrigation scheduling for cotton in semi-arid soils."
    chunks = chunk_document_with_context(sample_md, context, "sample_paper.pdf")
    for c in chunks:
        print(c.content)
