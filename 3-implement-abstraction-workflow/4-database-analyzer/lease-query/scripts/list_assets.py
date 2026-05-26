#!/usr/bin/env python3
"""list_assets.py -- inventory of source PDFs and pre-rendered page folders.

Run this first at the start of a session to see what page images are already
on disk vs which PDFs need rendering before a visual query can answer.

    python list_assets.py
    python list_assets.py --root ../../    # from inside scripts/
"""
import argparse
import glob
import os
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="project root (where Database.xlsx lives)")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    pages_dir = os.path.join(root, "_lease_pages")
    pdf_dir   = os.path.join(root, "leases", "PDF")

    if not os.path.isdir(pdf_dir):
        print(f"  (no leases/PDF folder at {pdf_dir})", file=sys.stderr)
    else:
        pdfs = sorted(os.path.basename(f) for f in glob.glob(os.path.join(pdf_dir, "*.pdf")))
        print(f"Source PDFs ({len(pdfs)}):")
        for f in pdfs:
            print(f"  {f}")

    print()
    if not os.path.isdir(pages_dir):
        print(f"  (no _lease_pages folder at {pages_dir} -- nothing rendered yet)")
        return
    slugs = sorted(d for d in os.listdir(pages_dir)
                   if os.path.isdir(os.path.join(pages_dir, d)))
    print(f"Pre-rendered page folders ({len(slugs)}):")
    for s in slugs:
        n = len(glob.glob(os.path.join(pages_dir, s, "page-*.png")))
        print(f"  {s:30s}  ({n} pages)")


if __name__ == "__main__":
    main()
