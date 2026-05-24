#!/usr/bin/env python3
"""
render_pdf.py -- Rasterize a lease .pdf to per-page PNGs for VISION reading.

This skill is vision-first: the agent abstracts a lease by *looking at* the
pages (the Read tool ingests PNGs natively), not by parsing recovered text.
Seeing the actual layout means the Article 1 "Key Defined Terms" grid, the
base-rent schedule, and contact exhibits read as real tables -- no heuristic
table detection, no OCR step (a rendered page reads the same whether the PDF
is born-digital or scanned).

Usage:
    python render_pdf.py "/path/to/Some_Lease.pdf" --outdir "../_lease_pages"
    python render_pdf.py "/path/to/Some_Lease.pdf" --dpi 200 --first 1 --last 4

Render into a HOST-VISIBLE folder (a subfolder of the project, e.g.
`../_lease_pages`), NOT the sandbox `/tmp` -- the Read tool can only see the
connected working folder. Delete that folder when done.

Requires poppler-utils (provides pdftoppm): apt-get install -y poppler-utils.
No Python packages required -- stdlib only.
"""
import argparse
import glob
import os
import shutil
import subprocess
import sys
import tempfile


def main():
    ap = argparse.ArgumentParser(description="Rasterize a lease PDF to PNGs for vision reading")
    ap.add_argument("pdf_path")
    ap.add_argument("--outdir", help="Directory for PNGs (default: a temp dir, path printed)")
    ap.add_argument("--dpi", type=int, default=150, help="Render resolution (default 150; bump to 200 if a page is illegible)")
    ap.add_argument("--first", type=int, help="First page to render")
    ap.add_argument("--last", type=int, help="Last page to render")
    args = ap.parse_args()

    if shutil.which("pdftoppm") is None:
        sys.exit("pdftoppm not found. Install poppler-utils: apt-get install -y poppler-utils")
    if not os.path.exists(args.pdf_path):
        sys.exit(f"No such file: {args.pdf_path}")

    outdir = args.outdir or tempfile.mkdtemp(prefix="leasepng_")
    os.makedirs(outdir, exist_ok=True)
    stem = os.path.join(outdir, "page")

    cmd = ["pdftoppm", "-png", "-r", str(args.dpi)]
    if args.first:
        cmd += ["-f", str(args.first)]
    if args.last:
        cmd += ["-l", str(args.last)]
    cmd += [args.pdf_path, stem]
    subprocess.run(cmd, check=True)

    pngs = sorted(glob.glob(stem + "*.png"))
    print(f"Rendered {len(pngs)} page(s) at {args.dpi} dpi -> {outdir}")
    for p in pngs:
        print(f"  {p}")
    print("\nNext: Read these PNGs (all of them for a short lease), abstract from "
          "what you see, build the JSON, then run load_record.py. Re-render at "
          "--dpi 200 if any page is hard to read.")


if __name__ == "__main__":
    main()
