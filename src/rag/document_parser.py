import os
import pymupdf4llm


def parse_pdf_to_markdown(file_path: str) -> str:
    """
    Parses a PDF file into a Markdown string using PyMuPDF4LLM.
    This preserves tables, formulas, and section structures.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found at {file_path}")

    md_text = pymupdf4llm.to_markdown(file_path)
    return md_text


if __name__ == "__main__":
    # Simple test assuming there is a dummy.pdf
    pass
