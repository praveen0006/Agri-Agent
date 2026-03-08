import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.document_parser import parse_pdf_to_markdown


def main():
    pdf_path = "data/papers/mock_cotton_research.pdf"
    print(f"Parsing: {pdf_path}")

    md_output = parse_pdf_to_markdown(pdf_path)
    print("\n--- Parsed Markdown Output ---")
    print(md_output)
    print("------------------------------")


if __name__ == "__main__":
    main()
