import urllib.request
import xml.etree.ElementTree as ET
import sys
import os

# Ensure we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.rag.document_parser import parse_pdf_to_markdown


def main():
    print("Searching arXiv for latest IoT Irrigation research paper...")
    url = "http://export.arxiv.org/api/query?search_query=all:irrigation+AND+all:iot&start=0&max_results=1"

    try:
        response = urllib.request.urlopen(url).read()
        root = ET.fromstring(response)

        pdf_url = None
        title = None

        # Parse Atom XML formatted response
        namespace = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in root.findall("atom:entry", namespace):
            title = entry.find("atom:title", namespace).text.replace("\n", " ")
            for link in entry.findall("atom:link", namespace):
                if link.attrib.get("title") == "pdf":
                    pdf_url = link.attrib.get("href")
                    break

        if not pdf_url:
            print("Could not find a paper.")
            return

        print(f"Success! Found paper: {title}")
        pdf_url = pdf_url + ".pdf"

        pdf_path = "data/papers/arxiv_sample.pdf"
        print(f"Downloading PDF from {pdf_url} (this may take a few seconds)...")

        req = urllib.request.Request(pdf_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as r, open(pdf_path, "wb") as f:
            f.write(r.read())

        print("Download complete. Parsing the PDF with PyMuPDF4LLM and pymupdf_layout...")

        # The parser runs the extraction
        md_output = parse_pdf_to_markdown(pdf_path)

        print("\n" + "=" * 50)
        print("--- Parsed Markdown Snapshot (First 2500 characters) ---")
        print("=" * 50 + "\n")
        print(md_output[:2500])
        print("\n...\n[Output Truncated - Full extraction successful]")
        print("=" * 50)

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
