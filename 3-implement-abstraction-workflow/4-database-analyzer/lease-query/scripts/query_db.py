#!/usr/bin/env python3
"""query_db.py -- load Database.xlsx into joined pandas DataFrames.

Use this from a Python snippet inside the skill:

    from query_db import load, with_dates, slug_map
    db = load("Database.xlsx")
    full = with_dates(db["leases_full"])    # adds months_to_expiry, etc.
    slugs = slug_map(db, "_lease_pages")    # lease_id -> page-folder name

Or as a CLI for quick checks:

    python query_db.py --db Database.xlsx --info
    python query_db.py --db Database.xlsx --slug-map
"""
import argparse
import os
import re
from datetime import date

import pandas as pd

PROPERTY_TYPE_LABELS = {
    "OFF": "Office",
    "MED": "Medical office",
    "IND": "Industrial",
    "RET": "Retail / restaurant",
    "COW": "Coworking",
    "LAB": "Life-sciences lab",
    "DC":  "Data center",
    "GND": "Ground / land lease",
}

SHEETS = ("Tenants", "Landlords", "Properties", "Leases", "RenewalOptions")


def _read_sheet(path, sheet):
    # Header is row 1; rows 2-4 are constraint/type/description metadata.
    df = pd.read_excel(
        path, sheet_name=sheet, header=0,
        skiprows=lambda r: r in (1, 2, 3),
    )
    return df.dropna(how="all")


def load(path="Database.xlsx"):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    tenants    = _read_sheet(path, "Tenants")
    landlords  = _read_sheet(path, "Landlords")
    properties = _read_sheet(path, "Properties")
    leases     = _read_sheet(path, "Leases")
    options    = _read_sheet(path, "RenewalOptions")

    # Coerce date columns to Python date (not Timestamp) for clean arithmetic.
    for col in ("commencement_date", "expiration_date"):
        if col in leases.columns:
            leases[col] = pd.to_datetime(leases[col]).dt.date

    leases_full = (
        leases
        .merge(tenants,    on="tenant_id",   how="left")
        .merge(landlords,  on="landlord_id", how="left")
        .merge(properties, on="property_id", how="left")
    )

    return {
        "tenants": tenants,
        "landlords": landlords,
        "properties": properties,
        "leases": leases,
        "options": options,
        "leases_full": leases_full,
    }


def with_dates(leases_df, today=None):
    """Add months_to_expiry to a leases (or leases_full) DataFrame.

    Whole-month convention: 18 months from May 25 means Nov 25 +12mo = Nov 25,
    +6 = Nov 25 of next year. Using year/month math, not days/30.44, avoids
    off-by-one near month boundaries.
    """
    today = today or date.today()
    df = leases_df.copy()

    def _months_between(d):
        if d is None or pd.isna(d):
            return None
        return (d.year - today.year) * 12 + (d.month - today.month)

    df["months_to_expiry"] = df["expiration_date"].apply(_months_between)
    return df


def with_notice_windows(leases_full_df, options_df, today=None):
    """Join leases_full to RenewalOptions and compute notice-window dates.

    Returns one row per (lease, option). Leases without options are dropped.
    """
    today = today or date.today()
    merged = options_df.merge(
        leases_full_df[["lease_id", "tenant_name", "expiration_date"]],
        on="lease_id", how="left",
    )

    def _shift(d, months):
        if d is None or pd.isna(d) or months is None or pd.isna(months):
            return None
        y, m = d.year, d.month - int(months)
        while m <= 0:
            m += 12
            y -= 1
        # Last day of month if d.day > days_in_month — pandas handles this:
        return pd.Timestamp(year=y, month=m, day=min(d.day, 28)).date()

    merged["notice_window_open"]  = [_shift(d, n) for d, n in zip(merged["expiration_date"], merged["notice_max_months"])]
    merged["notice_window_close"] = [_shift(d, n) for d, n in zip(merged["expiration_date"], merged["notice_min_months"])]
    merged["notice_window_is_open"] = [
        (o is not None and c is not None and o <= today <= c)
        for o, c in zip(merged["notice_window_open"], merged["notice_window_close"])
    ]
    return merged


def slug_map(db, pages_dir="_lease_pages"):
    """Map lease_id -> folder slug under _lease_pages/ by tenant-name match.

    Robust to extra trailing words in the tenant name (LLC, PLLC, Inc, etc.).
    Picks the available folder that shares the longest leading-word prefix
    with the lowercased tenant name.
    """
    if not os.path.isdir(pages_dir):
        return {}
    avail = [
        d for d in os.listdir(pages_dir)
        if os.path.isdir(os.path.join(pages_dir, d))
    ]
    out = {}
    for _, r in db["leases_full"].iterrows():
        tenant_words = re.findall(r"[A-Za-z0-9]+", str(r["tenant_name"]).lower())
        best, best_score = None, 0
        for s in avail:
            slug_words = re.findall(r"[A-Za-z0-9]+", s.lower())
            score = 0
            for a, b in zip(tenant_words, slug_words):
                if a == b:
                    score += 1
                else:
                    break
            if score > best_score:
                best, best_score = s, score
        if best:
            out[int(r["lease_id"])] = best
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="Database.xlsx")
    ap.add_argument("--info", action="store_true", help="row counts per sheet")
    ap.add_argument("--slug-map", action="store_true",
                    help="lease_id -> page-folder slug")
    ap.add_argument("--pages-dir", default="_lease_pages",
                    help="path to the _lease_pages folder")
    args = ap.parse_args()

    db = load(args.db)
    if args.info:
        for k, v in db.items():
            print(f"  {k:14s} rows={len(v)}")
    if args.slug_map:
        m = slug_map(db, args.pages_dir)
        for lid in sorted(m):
            tenant = db["leases_full"].loc[
                db["leases_full"]["lease_id"] == lid, "tenant_name"
            ].iloc[0]
            print(f"  lease_id={lid:3d}  {tenant:45s}  ->  _lease_pages/{m[lid]}/")
    if not (args.info or args.slug_map):
        ap.print_help()


if __name__ == "__main__":
    main()
