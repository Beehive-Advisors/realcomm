---
name: lease-pdf-to-database
description: >-
  Abstract a commercial lease PDF into the realcomm relational database. Use
  this skill whenever the user wants to extract, abstract, or load a lease
  (.pdf) into Database.xlsx — e.g. "abstract this PDF lease", "add this lease
  PDF to the database", "extract the lease PDF into the schema", "load a named
  lease PDF into the database", or points at a .pdf in the Leases folder. The
  skill extracts text + tables from the PDF (handling scanned PDFs via OCR),
  maps them to the abstraction schema, shows the parsed records in chat for the
  user to APPROVE, and only then appends them to Database.xlsx with correct
  primary/foreign keys and de-duplication. For .docx leases use
  lease-to-database instead.
---

# Lease PDF → Database

Turn a commercial lease **PDF** into rows across the five normalized tables in
`Database.xlsx` (`Tenants`, `Landlords`, `Properties`, `Leases`,
`RenewalOptions`), following the abstraction schema in
`Completed - Schema.xlsx`.

The split of labor: **you (the agent) do the reading and judgment**; the two
scripts handle deterministic text/table extraction and database plumbing
(keys, foreign keys, de-dup, enum/date validation).

> **Why a separate skill from `lease-to-database`?** A `.docx` has a real
> document model — paragraphs and tables are objects, so extraction is exact. A
> PDF has none of that: text and tables must be *recovered* from page layout,
> table detection is heuristic, cells wrap mid-value, and a scanned PDF has no
> text at all until it is OCR'd. The extraction step and its gotchas are
> genuinely different, so the workflow is rebuilt around the PDF. The
> downstream record shape and the loader are intentionally the same as
> `lease-to-database` — both feed one shared `Database.xlsx`.

## Files

```
lease-pdf-to-database/
  SKILL.md                       <- this file
  scripts/extract_pdf.py         <- pdf -> plain text (per-page text + tables)
  scripts/load_record.py         <- approved JSON record -> Database.xlsx
  reference/schema_mapping.md     <- field-by-field mapping + enum codes (READ THIS)
  reference/example_record.json   <- a complete worked record (Ironhide lease)
```

Default workbook locations in this project:
- Database: `../Database.xlsx`
- Schema:   `../Completed - Schema.xlsx`
- Leases:   the `.pdf` the user points at (e.g. `../*.pdf` or a Leases folder)

## Workflow — follow in order

### 1. Identify the lease and read the mapping
Confirm which `.pdf` to abstract. Read `reference/schema_mapping.md` so you have
the enum codes and the de-dup / notice-window conventions in mind.

### 2. Extract the text
```bash
python scripts/extract_pdf.py "../YourLease.pdf" --out /tmp/lease.txt
```
Read the output top to bottom.

- The script prints a **SUMMARY** first (page count, tables detected, and a
  scanned-PDF warning if any page has little/no extractable text).
- **If the SUMMARY warns the PDF is scanned/image-only**, stop and OCR it first
  — use the `anthropic-skills:pdf` skill or `ocrmypdf in.pdf out.pdf` — then
  re-run extraction on the OCR'd copy. Do not abstract from an empty extraction.
- The structured facts live in the **TABLE p.n** blocks — especially the
  Article 1 "Key Defined Terms" grid, the Base Rent schedule, and any contact
  exhibit — but PDF table detection is imperfect, so **also read the PAGE text**
  and cross-check. Watch for cells wrapped across lines (newlines appear inside
  a value), merged/split columns, and numbers split from their labels.
- Read the renewal article (usually Article 27) in the PAGE prose for the
  notice window and conditions; the Article 1 grid only summarizes it.

### 3. Build the record (JSON)
Produce a single JSON object matching `reference/example_record.json`:
`tenant`, `landlord`, `property`, `lease`, and a `renewal_options` array (one
object per option; `[]` if none). Apply the enum codes and the notice-window
convention from the mapping reference. Convert dates to ISO `YYYY-MM-DD`. Derive
`escalation_pct` from the rent schedule if not stated outright, and record it as
the **percent value itself** (e.g. `2.5`, not `0.025`). Record `base_rent` as
the **first full (non-abated) rate** and state in `base_rent_frequency` whether
it is ANNUAL or MONTHLY.

### 4. Present for approval IN CHAT — do not write yet
Show the user the parsed records as readable tables (one per destination
sheet), plus a one-line note of any judgment calls (e.g. "recorded annual base
rent", "escalation derived from schedule", "notice window 18→15 months", "table
on p.1 came through ragged; values confirmed against page text"). **Wait for
explicit approval before touching the database.** If they request changes, edit
the JSON and re-show.

Optional no-write preview of key/FK assignment:
```bash
python scripts/load_record.py --db "../Database.xlsx" --record /tmp/record.json --dry-run
```

### 5. Load into Database.xlsx
Once approved, save the record to `/tmp/record.json` and run:
```bash
python scripts/load_record.py --db "../Database.xlsx" --record /tmp/record.json
```
The loader validates enums/dates, reuses existing Tenant/Landlord/Property rows
where they already exist (de-dup), assigns the next primary keys, wires the
lease's foreign keys, appends one row per renewal option, and saves in place.
Report back the assigned `lease_id` and the tenant/landlord/property IDs.

**Styling is preserved automatically** — the loader loads your existing workbook
and appends to it; it never rebuilds the file. **Mount resilience:** reads and
writes go through retry-with-verify helpers, surviving a flaky/virtualized mount.

## Rules and gotchas

- **Approval gate is mandatory.** Never write to `Database.xlsx` before the user
  has approved the parsed records in chat.
- **Scanned PDFs need OCR first.** No text = nothing to abstract. OCR, then re-extract.
- **Trust tables, but verify against page text.** PDF table extraction is
  heuristic; the page prose is the tie-breaker when a cell looks merged/split.
- **4 header rows.** Data begins on row 5 of every sheet; the loader handles
  this — never hand-edit rows 1–4.
- **De-dup.** Recurring landlords/properties/tenants are matched by
  name/address and their existing key reused. Don't pre-assign IDs in the JSON.
- **Enums are validated.** `property_type`, `size_unit`, `lease_type`,
  `base_rent_frequency`, `security_deposit_type`, `renewal_rent_basis` must use
  the exact codes in the mapping reference, or the loader aborts.
- **NNN vs GRS.** Tenant pays its share of taxes/insurance/CAM on top of base
  rent → `NNN`; single all-in rent → `GRS`.
- **No renewal option** → `renewal_options: []`.
- **Dependencies:** `pip install pdfplumber openpyxl --break-system-packages`
  (and `ocrmypdf` for scanned PDFs).
- **Git:** writing files is fine, but per the repo's CLAUDE.md never run git
  write commands from the sandbox — hand the user the commit/push commands.

## Worked example

`reference/example_record.json` is the fully abstracted **Ironhide Cold
Logistics** industrial lease: a 120-month NNN whole-building cold-storage lease,
$641,625 letter-of-credit deposit, ~2.5% annual escalation, and **two** 5-year
Fair-Market-Rent renewal options with an 18→15-month notice window. It exercises
all five tables and is the reference for how a finished record should look.
