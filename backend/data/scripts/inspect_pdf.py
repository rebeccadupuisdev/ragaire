import argparse
import json
from pathlib import Path

import fitz  # pymupdf

BOOKS_CONFIG = Path(__file__).parent / "books.json"


def load_pdf_path(name_or_path: str) -> str:
    """Resolve a book name (from books.json) or a direct file path."""
    if name_or_path.endswith(".pdf"):
        return name_or_path

    with open(BOOKS_CONFIG) as f:
        books = json.load(f)

    if name_or_path not in books:
        known = ", ".join(books.keys())
        raise SystemExit(f"Unknown book '{name_or_path}'. Known books: {known}")

    return books[name_or_path]["pdf"]


def inspect(pdf_path: str) -> None:
    doc = fitz.open(pdf_path)
    font_sizes: dict[float, int] = {}

    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block["type"] != 0:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    size = round(span["size"], 1)
                    font_sizes[size] = font_sizes.get(size, 0) + 1

    doc.close()

    print(f"Font sizes in: {pdf_path}\n")
    for size, count in sorted(font_sizes.items(), reverse=True):
        bar = "█" * min(count // 100, 40)
        print(f"  {size:5.1f}pt — {count:6} spans  {bar}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Inspect font sizes in a PDF. Pass a book name from books.json or a direct PDF path."
    )
    parser.add_argument("book", help="Book name (from books.json) or path to a PDF file")
    args = parser.parse_args()
    inspect(load_pdf_path(args.book))
