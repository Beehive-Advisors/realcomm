#!/usr/bin/env python3
"""
extract_pdf.py -- Dump a lease .pdf to plain text for abstraction.

PDFs are harder than .docx: there is no document object model, so "paragraphs"
and "tables" have to be recovered from the page layout. This script uses
pdfplumber to emit, per page:
  * the page's flowing text (PAGE n), and
  * every table pdfplumber can detect on that page (TABLE p<page>.<n>),
    rendered as pipe-delimited rows.

Because PDF table detection is heuristic, ALWAYS read both the PAGE text and
the TABLE blocks and cross-check them against each other. Cells can wrap across
lines (newlines inside a cell are shown literally), columns can merge or split,
and a table that was clean in Word can come through ragged after conversion.

Scanned / image-only PDFs have no extractable text. If a page yields little or
no text this script flags it; such a file must be OCR'd first (see the
`anthropic-skills:pdf` skill / `ocrmypdf`) before abstraction.

Usage:
    python extract_pdf.py "/path/to/Some_Lease.pdf"
    python extract_pdf.py "/path/to/Some_Lease.pdf" --out lease.txt

Requires pdfplumber (pip install pdfplumber --break-system-packages).
"""
import argparse
import sys

try:
    import pdfplumber
except ImportError:
    sys.exit("pdfplumber is required: pip install pdfplumber --break-system-packages")

# A page with fewer than this many characters of extractable text is treated as
# possibly scanned / image-only and flagged for OCR.
MIN_CHARS_PER_PAGE = 25


def render_table(rows):
    out = []
    for r in rows:
        cells = ["" if c is None else str(c).strip() for c in r]
        if any(cells):
            out.append(" | ".join(cells))
    return out


def extract(path: str) -> str:
    out = []
    low_text_pages = []

    with pdfplumber.open(path) as pdf:
        n_pages = len(pdf.pages)
        total_tables = 0

        # First pass for the summary header.
        page_payloads = []
        for i, page in enumerate(pdf.pages, start=1):
            text = (page.extract_text() or "").strip()
            tables = page.extract_tables() or []
            total_tables += len(tables)
            if len(text) < MIN_CHARS_PER_PAGE and not tables:
                low_text_pages.append(i)
            page_payloads.append((i, text, tables))

        out.append("==================== SUMMARY ====================")
        out.append(f"pages: {n_pages}")
        out.append(f"tables detected: {total_tables}")
        if low_text_pages:
            out.append(
                "WARNING: little/no extractable text on page(s) "
                + ", ".join(map(str, low_text_pages))
                + " -- this PDF may be scanned/image-only. OCR it before abstracting."
            )
        out.append("")

        for i, text, tables in page_payloads:
            out.append(f"==================== PAGE {i} ====================")
            if text:
                out.append(text)
            else:
                out.append("(no extractable text on this page)")
            for ti, tbl in enumerate(tables):
                out.append("")
                out.append(f"-------------------- TABLE {i}.{ti} --------------------")
                out.extend(render_table(tbl))
            out.append("")

    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Extract text + tables from a lease .pdf")
    ap.add_argument("pdf_path", help="Path to the lease .pdf")
    ap.add_argument("--out", help="Optional output .txt path; prints to stdout if omitted")
    args = ap.parse_args()

    text = extract(args.pdf_path)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Wrote {len(text):,} chars to {args.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
