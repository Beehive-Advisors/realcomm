---
name: lease-query
description: >-
  Answer questions about a portfolio of commercial leases by combining a
  normalized lease database (Database.xlsx with 5 sheets: Tenants, Landlords,
  Properties, Leases, RenewalOptions) and the rendered page images of the
  original lease PDFs (_lease_pages/SLUG/page-NN.png). Use this skill
  whenever the user asks about lease expirations, renewal options, notice
  windows, rent rolls, escalations, security deposits, WALT, NNN vs gross
  exposure, tenant or asset-class concentration, OR asks to see an exhibit
  (site plan, signage criteria, floorplan, parking ratios, cage configuration,
  exclusive-use clauses, sign criteria). Triggers include "which leases",
  "what leases", "how many leases", "rent roll", "expirations", "options",
  "WALT", "renewal notice", "exhibit", "site plan", "signage", "parking",
  "floorplan", "exclusive", "cage", "loading dock".
---

# Lease query

## What's in this workspace

- `Database.xlsx` — five sheets, four header rows, real data on row 5+.
  See `reference/schema.md` for the columns and enums.
- `leases/PDF/*.pdf` — source documents.
- `_lease_pages/<slug>/page-NN.png` — pre-rendered page images for
  vision reading. Slug is the first one-or-two words of the tenant name,
  e.g. `Saltflats_Tacos`, `Summit_Grid`, `Aspen_Hollow_Ophthalmology`.

## How to answer

**Data questions** (anything the DB can answer alone — expirations,
options, rent roll, WALT, escalation, concentration, NNN/GRS mix):
load the sheets with pandas, filter / aggregate, and return the answer
as a markdown table in chat. Prepend a one-line context note with the
cutoff date used, e.g. "As of 2026-05-25, 3 leases match." Round money
to whole dollars; render dates as `YYYY-MM-DD`.

```python
import pandas as pd
def load_db(path="Database.xlsx"):
    out = {}
    for s in ("Tenants","Landlords","Properties","Leases","RenewalOptions"):
        out[s.lower()] = (pd.read_excel(path, sheet_name=s, header=0,
                          skiprows=lambda r: r in (1,2,3))
                          .dropna(how="all"))
    # Coerce date columns (Excel may hand them back as strings)
    for c in ("commencement_date","expiration_date"):
        if c in out["leases"].columns:
            out["leases"][c] = pd.to_datetime(out["leases"][c]).dt.date
    out["leases_full"] = (out["leases"]
        .merge(out["tenants"],   on="tenant_id",   how="left")
        .merge(out["landlords"], on="landlord_id", how="left")
        .merge(out["properties"], on="property_id", how="left"))
    return out
```

**Document questions** (anything that requires looking at an exhibit,
site plan, signage rules, floorplan, cage layout, etc. — i.e. not
captured in the 19-field schema): use the `Read` tool directly on
`_lease_pages/<slug>/page-NN.png`. The page renders inline in chat —
that IS the answer. Identify in your prose which lease and which page,
then add a 2–4 sentence summary of what's notable.

Don't know which page has the exhibit? `Read` `page-02.png` or `page-03.png`
first (table of contents); exhibits usually live in the last third of the
PDF.

**Mixed questions**: filter the DB to get the qualifying lease list, then
`Read` the relevant page(s) of each matching lease.

## Rules

- Always use `date.today()` for "next N months" filters; state the date.
- Read-only skill. To add a new lease, run `lease-pdf-to-database` (or
  `lease-to-database` for `.docx`).
- If `_lease_pages/<slug>/` is missing for a lease in the DB, render it:
  `pdftoppm -png -r 150 leases/PDF/<file>.pdf _lease_pages/<slug>/page`.

## Dependencies

`pip install openpyxl pandas --break-system-packages`. Poppler only needed
if a page folder is missing.
