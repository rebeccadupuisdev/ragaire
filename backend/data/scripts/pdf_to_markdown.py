import argparse
import json
import re
from pathlib import Path

import fitz  # pymupdf

BOOKS_CONFIG = Path(__file__).parent / "books.json"

FLAG_BOLD = 16
FLAG_ITALIC = 2


def load_book_config(name_or_path: str, output: str | None, skip_below: float, h1: float, h2: float) -> dict:
    """Return a config dict from books.json (by name) or from CLI args (by path)."""
    if not name_or_path.endswith(".pdf"):
        with open(BOOKS_CONFIG) as f:
            books = json.load(f)
        if name_or_path not in books:
            known = ", ".join(books.keys())
            raise SystemExit(f"Unknown book '{name_or_path}'. Known books: {known}")
        return books[name_or_path]

    if output is None:
        raise SystemExit("--output is required when passing a PDF path directly.")

    return {
        "pdf": name_or_path,
        "output": output,
        "skip_below": skip_below,
        "h1": h1,
        "h2": h2,
    }


def size_to_heading(size: float, h1: float, h2: float) -> int | None:
    """Return heading level (1-2) for a font size, or None for body text.

    Thresholds are passed in so the script works across books with
    different base font sizes (discovered via inspect_pdf.py).
    """
    if size >= h1:
        return 1
    if size >= h2:
        return 2
    return None


def apply_inline_formatting(text: str, flags: int) -> str:
    bold = flags & FLAG_BOLD
    italic = flags & FLAG_ITALIC
    if bold and italic:
        return f"***{text}***"
    if bold:
        return f"**{text}**"
    if italic:
        return f"*{text}*"
    return text


def spans_to_line_text(spans: list) -> str:
    """Merge all spans in a line into a single formatted string."""
    parts = []
    for span in spans:
        text = span["text"]
        if not text.strip():
            parts.append(text)
            continue
        parts.append(apply_inline_formatting(text, span["flags"]))
    return "".join(parts)


def process_block(block: dict, skip_below: float, h1: float, h2: float) -> list[str]:
    """Convert a text block into a list of output lines."""
    output_lines = []

    for line in block["lines"]:
        if not line["spans"]:
            continue

        dominant_span = max(line["spans"], key=lambda s: s["size"])
        size = round(dominant_span["size"], 1)

        if size < skip_below:
            continue

        line_text = spans_to_line_text(line["spans"]).strip()
        if not line_text:
            continue

        heading_level = size_to_heading(size, h1, h2)

        if heading_level is not None:
            prefix = "#" * heading_level
            output_lines.append(f"{prefix} {line_text}")
        else:
            output_lines.append(line_text)

    return output_lines


def clean_output(lines: list[str]) -> str:
    """Join lines, collapse excessive blank lines, normalise spacing."""
    result = []
    prev_blank = False

    for line in lines:
        # Drop standalone page numbers and numbered-list artifacts (e.g. "27" or "27.")
        if re.fullmatch(r"\d+\.?", line.strip()):
            continue

        if re.fullmatch(r"[.\s]+", line.strip()) and line.strip():
            continue

        is_blank = line.strip() == ""
        if is_blank:
            if not prev_blank:
                result.append("")
            prev_blank = True
        else:
            result.append(line)
            prev_blank = False

    text = "\n".join(result)
    text = re.sub(r"(?<!\n)\n(#{1,3} )", r"\n\n\1", text)
    text = re.sub(r"\*{1,3}(.{1,2})\*{1,3}", r"\1", text)

    return text.strip()


def convert(cfg: dict) -> None:
    doc = fitz.open(cfg["pdf"])
    all_lines = []

    skip_below = cfg["skip_below"]
    h1 = cfg["h1"]
    h2 = cfg["h2"]

    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block["type"] != 0:
                continue
            block_lines = process_block(block, skip_below, h1, h2)
            if block_lines:
                all_lines.extend(block_lines)
                all_lines.append("")

    doc.close()

    output = clean_output(all_lines)

    with open(cfg["output"], "w", encoding="utf-8") as f:
        f.write(output)

    print(f"Done. Written to {cfg['output']}")
    print(f"Total characters: {len(output):,}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Convert a PDF to a Markdown-formatted .txt for RAG ingestion.\n"
            "Pass a book name from books.json, or a direct PDF path with --output."
        )
    )
    parser.add_argument("book", help="Book name (from books.json) or path to a PDF file")
    parser.add_argument("--output", help="Output .txt path (required when passing a PDF path directly)")
    parser.add_argument("--skip-below", type=float, default=12.0,
                        help="Skip spans smaller than this pt size (default: 12.0)")
    parser.add_argument("--h1", type=float, default=22.0,
                        help="Minimum pt size for # H1 headings (default: 22.0)")
    parser.add_argument("--h2", type=float, default=18.5,
                        help="Minimum pt size for ## H2 headings (default: 18.5)")

    args = parser.parse_args()
    cfg = load_book_config(args.book, args.output, args.skip_below, args.h1, args.h2)
    convert(cfg)
