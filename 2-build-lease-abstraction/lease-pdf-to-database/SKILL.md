---
name: lease-pdf-to-database
description: >-
  Abstract a commercial lease PDF into the realcomm relational database. Use
  this skill whenever the user wants to extract, abstract, or load a lease
  (.pdf) into Database.xlsx — e.g. "abstract this PDF lease", "add this lease
  PDF to the database", "extract the lease PDF into the schema", "load a named
  lease PDF into the database", or points at a .pdf in the Leases folder. The
  skill reads the PDF pages as images (vision), maps them to the abstraction
  schema, renders an interactive visual summary of the abstracted lease(s)
  (with a toggle to switch between them when several are processed) for the
  user to APPROVE, and only then appends them to Database.xlsx with correct
  primary/foreign keys and de-duplication. For .docx leases use
  lease-to-database instead.
---

# Lease PDF → Database

Turn a commercial lease **PDF** into rows across the five normalized tables in
`Database.xlsx` (`Tenants`, `Landlords`, `Properties`, `Leases`,
`RenewalOptions`), following the abstraction schema in
`Completed - Schema.xlsx`.

The split of labor: **you (the agent) do the reading and judgment by LOOKING at
the pages**; a small render script turns the PDF into page images, and the
loader handles database plumbing (keys, foreign keys, de-dup, enum/date
validation).

> **Why vision-first, and why a separate skill from `lease-to-database`?**
> A `.docx` has a real document model — paragraphs and tables are objects, so
> text extraction is exact and the sibling skill parses it directly. A PDF has
> none of that: there is no reliable table model, and a *scanned* PDF has no
> text layer at all. Rather than fight heuristic table-recovery (and bolt on
> OCR for scans), this skill renders each page to an image and **reads it with
> vision** — the Article 1 grid, the rent schedule, and contact exhibits come
> through as the real tables they are, and a scanned page reads exactly like a
> born-digital one. The downstream record shape and the loader are intentionally
> identical to `lease-to-database` — both feed one shared `Database.xlsx`.

## Files

```
lease-pdf-to-database/
  SKILL.md                       <- this file
  scripts/render_pdf.py          <- pdf -> per-page PNGs + a navigation index
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

### 2. Render the PDF to page images
```bash
python scripts/render_pdf.py "../YourLease.pdf" --outdir "../_lease_pages"
```
This rasterizes every page to a PNG and prints the list of files. (Requires
poppler-utils: `apt-get install -y poppler-utils`.)

> **Render to a host-visible folder, NOT `/tmp`.** The Read tool (step 3) reads
> files the *user* can see — the connected working folder — while the shell
> runs in a separate sandbox whose `/tmp` the Read tool cannot reach. Render
> into a subfolder of the project (e.g. `../_lease_pages`, alongside
> `Database.xlsx`) so the PNGs are visible to Read. Delete that folder when
> you're done.

### 3. READ the pages with vision
Use the **Read tool** on the PNGs — this is the core of the skill. Look at the
pages; do not parse text.

- Focus on the **Article 1 "Key Defined Terms" grid** (parties, premises, dates,
  term, rent) and the **base-rent schedule** — they hold most of the structured
  facts and read cleanly as tables when you see them.
- Read the **renewal/option article** in the page prose for the notice window
  and conditions; an Article 1 grid only summarizes it. If there is no renewal
  option, record `renewal_options: []`.
- For a short lease (≤ ~15 pages) just view them all. For a long lease, skim for
  the pages above, then view any others you need. Delete the `_lease_pages`
  folder once the record is built.
- Scanned/image-only PDFs: no special handling. The page still renders to a PNG
  and you read it the same way. If a page is blank/illegible, re-render at
  `--dpi 200`.

### 4. Build the record (JSON)
Produce a single JSON object matching `reference/example_record.json`:
`tenant`, `landlord`, `property`, `lease`, and a `renewal_options` array (one
object per option; `[]` if none). **Record only the fields defined in
`Completed - Schema.xlsx`** — the 19 fields listed in `schema_mapping.md`. Do
not add contacts, entity types, notes, or other fields the schema does not
define. Apply the enum codes and the notice-window convention from the mapping
reference. Convert dates to ISO `YYYY-MM-DD`. Derive `escalation_pct` from the
rent schedule if not stated outright, and record it as the **percent value
itself** (e.g. `2.5`, not `0.025`). Record `base_rent` as the **first full
(non-abated) rate**, as an **annual** figure (the schema has no frequency
field; convert a monthly or per-SF quote to annual).

### 5. Visualize the abstract(s) for approval — DO NOT WRITE YET
Before touching the database, render an interactive visual summary of what you
abstracted so the user can review and APPROVE it at a glance. Use the
visualization/widget capability (an inline HTML widget) — do not just restate
the tables in prose. **This visual is the approval gate.**

Build one "lease abstract" view per lease processed, laid out as a clean card:
- a header with the lease name, asset-type badge, and lease-type (NNN/GRS) badge;
- the parties (tenant and landlord names);
- the property (address, type, size);
- key economic terms (commencement, expiration, term, base rent, escalation %,
  security deposit + type, permitted use); and
- the renewal options (sequence, term, rent basis, notice window).

**Toggling:** track every lease abstracted in the current session. If only one
lease was processed, show that single view. If two or more were processed,
render a selector (tabs or a dropdown) at the top so the user can toggle between
each lease's abstract, with all data held client-side in the widget (no extra
round-trips). Round any displayed currency/percent values.

Alongside the widget, add a one-line note of any judgment calls (e.g. "recorded
annual base rent", "escalation derived from schedule", "notice window 18→15
months", "no security deposit — leasehold financing substitutes"). **Wait for
explicit approval before touching the database.** If the user requests changes,
edit the JSON and re-render the visual.

Optional no-write preview of key/FK assignment:
```bash
python scripts/load_record.py --db "../Database.xlsx" --record /tmp/record.json --dry-run
```

### 6. Load into Database.xlsx
Once the user approves the visual, save the record to `/tmp/record.json` and run:
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
  has approved the interactive visual summary of the parsed records.
- **Read the pages, don't parse them.** The image is the source of truth; the
  `pdftotext` index is only a navigation aid and a tie-breaker for an ambiguous
  glyph.
- **Scanned PDFs need no OCR.** A rendered page reads the same whether or not it
  has a text layer. If a page is blank/illegible, re-render at `--dpi 200`.
- **4 header rows.** Data begins on row 5 of every sheet; the loader handles
  this — never hand-edit rows 1–4.
- **De-dup.** Recurring landlords/properties/tenants are matched by
  name/address and their existing key reused. Don't pre-assign IDs in the JSON.
- **Schema is the source of truth.** `Completed - Schema.xlsx` defines the 19
  fields; record exactly those — no contacts, entity types, or notes. The loader
  only writes columns that exist in `Database.xlsx`, so stray fields are silently
  dropped; don't rely on that, just follow the schema.
- **Enums are validated.** `property_type`, `size_unit`, `lease_type`,
  `security_deposit_type`, `renewal_rent_basis` must use the exact codes in the
  mapping reference, or the loader aborts.
- **NNN vs GRS.** Tenant pays its share of taxes/insurance/CAM on top of base
  rent → `NNN`; single all-in rent → `GRS`.
- **No renewal option** → `renewal_options: []`.
- **Dependencies:** `poppler-utils` for `render_pdf.py` (provides `pdftoppm`);
  `pip install openpyxl --break-system-packages` for the loader. No
  `pdfplumber`/`ocrmypdf` needed.
- **Git:** writing files is fine, but per the repo's CLAUDE.md never run git
  write commands from the sandbox — hand the user the commit/push commands.

## Worked example

`reference/example_record.json` is the fully abstracted **Ironhide Cold
Logistics** industrial lease: a 120-month NNN whole-building cold-storage lease,
$641,625 letter-of-credit deposit, ~2.5% annual escalation, and **two** 5-year
Fair-Market-Rent renewal options with an 18→15-month notice window. It exercises
all five tables and is the reference for how a finished record should look.
