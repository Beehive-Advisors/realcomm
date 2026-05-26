#!/usr/bin/env python3
"""page_data_uri.py -- turn a lease page PNG into a base64 data URI.

Widget iframes can't load local files (CSP only allows a few CDNs), so to
*show* an exhibit page inside a visual widget the bytes must be embedded
inline. This helper downscales + JPEG-compresses the PNG so the resulting
data URI stays small enough to ship in a widget code block.

Usage:
    # CLI (writes the data URI to stdout):
    python page_data_uri.py _lease_pages/Summit_Grid/page-08.png
    python page_data_uri.py _lease_pages/Summit_Grid/page-08.png --max-width 800 --quality 75

    # As a library:
    from page_data_uri import to_data_uri
    uri = to_data_uri("_lease_pages/Summit_Grid/page-08.png")
    # Drop into widget HTML: <img src="{uri}" />

Output sizes (rule of thumb at default 900px / q78):
- text-heavy exhibit page  ~ 40-70 KB
- diagram-heavy exhibit    ~ 80-140 KB
A widget can comfortably carry 1-3 inlined pages. For more, prefer thumbnails
plus a markdown link to the page file.
"""
import argparse
import base64
import io
import os
import sys

from PIL import Image


def to_data_uri(path: str, max_width: int = 900, quality: int = 78) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    im = Image.open(path)
    w, h = im.size
    if w > max_width:
        scale = max_width / w
        im = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    buf = io.BytesIO()
    im.convert("RGB").save(buf, format="JPEG", quality=quality, optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return "data:image/jpeg;base64," + b64


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="Page PNG to encode (e.g. _lease_pages/Summit_Grid/page-08.png)")
    ap.add_argument("--max-width", type=int, default=900,
                    help="Downscale wider images to this width (px). Default 900.")
    ap.add_argument("--quality", type=int, default=78,
                    help="JPEG quality 1-95. Default 78.")
    ap.add_argument("--size-only", action="store_true",
                    help="Print the resulting size in KB and exit (no data URI).")
    args = ap.parse_args()

    uri = to_data_uri(args.path, args.max_width, args.quality)
    if args.size_only:
        # The "size" of interest is the base64 payload size that will land in
        # the widget code -- not the binary JPEG.
        payload = len(uri) - len("data:image/jpeg;base64,")
        print(f"{payload // 1024} KB (base64)")
    else:
        sys.stdout.write(uri)


if __name__ == "__main__":
    main()
