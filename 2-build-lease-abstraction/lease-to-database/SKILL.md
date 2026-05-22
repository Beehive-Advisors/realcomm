---
name: lease-to-database
description: >-
  Abstract a commercial lease document into the realcomm relational database.
  Use this skill whenever the user wants to extract, abstract, or load a lease
  (.docx) into Database.xlsx — e.g. "abstract this lease", "add this lease to
  the database", "extract the lease into the schema", "load a named lease into
  the database", or points at a file in the Leases folder. The skill reads the
  lease (paragraphs + tables), maps it to the abstraction schema, shows the
  parsed records in chat for the user to APPROVE, and only then appends them to
  Database.xlsx with correct primary/foreign keys and de-duplication.
---

# Lease → Database

Turn a commercial lease (.docx) into rows across the five normalized tables in
`Database.xlsx` (`Tenants`, `Landlords`, `Properties`, `Leases`,
`RenewalOptions`), following the abstraction schema in
`Completed - Schema.xlsx`.

The split of labor: **you (the agent) do the reading and judgment**; the two
scripts handle deterministic text extraction and database plumbing
(keys, foreign keys, de-dup, enum/date validation).

## Files

```
lease-to-database/
  SKILL.md                       <- this file
  scripts/extract_text.py        <- docx -> plain text (paragraphs + tables)
  scripts/load_record.py         <- approved JSON record -> Database.xlsx
  reference/schema_mapping.md     <- field-by-field mapping + enum codes (READ THIS)
  reference/example_record.json   <- a complete worked record (Ironhide lease)
```

Default workbook locations in this project:
- Database: `../Database.xlsx` (i.e. `2-lease-abstraction-workflow/Database.xlsx`)
- Schema:   `../Completed - Schema.xlsx`
- Leases:   `../Leases/*.docx`

## Workflow — follow in order

### 1. Identify the lease and read the mapping
Confirm which `.docx` to abstract. Read `reference/schema_mapping.md` so you
have the enum codes and the de-dup / notice-window conventions in mind.

### 2. Extract the text
```bash
python scripts/extract_text.py "../Leases/YourLease.docx" --out /tmp/lease.txt
```
Read the output. **The structured facts live in the tables** — especially the
Article 1 "Key Defined Terms" grid, the Base Rent schedule, the renewal
article, and the Tenant Contact exhibit. Read the renewal article (usually
Article 27) in the prose for the notice window and conditions.

### 3. Build the record (JSON)
Produce a single JSON object matching `reference/example_record.json`:
`tenant`, `landlord`, `property`, `lease`, and a `renewal_options` array (one
object per option; `[]` if the lease has none). Apply the enum codes and the
notice-window convention from the mapping reference. Convert dates to ISO
`YYYY-MM-DD`. Derive `escalation_pct` from the rent schedule if it isn't stated
outright, and record it as the **percent value itself** (e.g. `2.5` for 2.5%,
not `0.025`). Record `base_rent` as the **first full (non-abated) rate** and say
in `base_rent_frequency` whether it is ANNUAL or MONTHLY.

### 4. Present for approval IN CHAT — do not write yet
Show the user the parsed records as readable tables (one per destination
sheet), plus a one-line note of any judgment calls (e.g. "recorded annual base
rent", "escalation derived from schedule", "notice window 18→15 months"). Ask
the user to confirm or correct. **Wait for explicit approval before touching
the database.** If they request changes, edit the JSON and re-show.

You can also run a no-write preview to confirm key/FK assignment:
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

**Styling is preserved automatically.** The loader *loads your existing
workbook and appends* to it — it never rebuilds the file — so all formatting
(header fills, fonts, column widths, frozen panes) is kept. Never recreate the
workbook from scratch; that throws the styling away.

**Mount resilience.** Reads and writes go through retry-with-verify helpers
(`load_workbook_robust` / `save_workbook_robust`): the file is copied to local
disk, edited there, then copied back and re-opened to confirm it landed. This
survives a flaky/virtualized mount that intermittently drops the file. If every
retry fails the loader exits and keeps the edited copy locally so no work is
lost.

## Rules and gotchas

- **Approval gate is mandatory.** Never write to `Database.xlsx` before the
  user has approved the parsed records in chat.
- **4 header rows.** Data begins on row 5 of every sheet; the loader handles
  this — never hand-edit rows 1–4.
- **De-dup.** The same landlord (e.g. Beehive Realty Trust) recurs across
  leases. The loader reuses the existing `landlord_id` rather than duplicating.
  Don't pre-assign IDs in the JSON — the loader assigns them.
- **Enums are validated.** `property_type`, `size_unit`, `lease_type`,
  `base_rent_frequency`, `security_deposit_type`, `renewal_rent_basis` must use
  the exact codes in the mapping reference, or the loader aborts.
- **NNN vs GRS.** If the tenant pays its proportionate share of
  taxes/insurance/CAM on top of base rent, it's `NNN`; a single all-in rent is
  `GRS`.
- **No renewal option** → `renewal_options: []`.
- **Dependencies:** `pip install python-docx openpyxl --break-system-packages`.
- **Git:** writing files is fine, but per the repo's CLAUDE.md never run git
  write commands from the sandbox — hand the user the commit/push commands.

## Worked example

`reference/example_record.json` is the fully abstracted **Ironhide Cold
Logistics** industrial lease: a 120-month NNN whole-building cold-storage lease,
$641,625 letter-of-credit deposit, ~2.5% annual escalation, and **two**
5-year Fair-Market-Rent renewal options with an 18→15-month notice window. It
exercises all five tables and is the reference for how a finished record should
look.
