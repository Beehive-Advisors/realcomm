# Lease abstraction — instructions

## Setup (instructor, once)

1. Install the skill: open `lease-pdf-to-database.skill`, click **Save skill**, restart the app/session.
2. Confirm `Database.xlsx` exists in this folder. Header-only (no data rows) is fine for a fresh class.
3. Install poppler in the sandbox if it isn't already: `apt-get install -y poppler-utils`.

## Workflow (student, per lease)

1. Put the lease PDF in this folder.
2. Tell the assistant: **"Abstract `<filename>.pdf` into the database."**
3. The assistant renders the pages, reads them with vision, and shows an approval card.
4. Check parties, address, dates, term, base rent, deposit, renewal options.
5. Click **Approve & write** (or **Make changes first** and say what to correct).
6. Note the `lease_id` reported on load.

## What gets recorded (19 schema fields)

| Sheet | Fields |
|---|---|
| Tenants | `tenant_name` |
| Landlords | `landlord_name` |
| Properties | `premises_address`, `property_type` (OFF/MED/IND/RET/COW/LAB/DC/GND), `size`, `size_unit` (RSF/ACRE) |
| Leases | `commencement_date`, `expiration_date`, `term_months`, `lease_type` (NNN/GRS), `base_rent`, `escalation_pct`, `security_deposit_amount`, `security_deposit_type` (Cash/CL/NONE), `permitted_use` |
| RenewalOptions | one row per option: `option_sequence`, `renewal_term_months`, `renewal_rent_basis` (FMR/FIX/CPI/NONE), `notice_min_months`, `notice_max_months` |

Surrogate keys (`*_id`) and foreign keys are wired automatically. Anything not listed above (contacts, notes, base-rent frequency) is not in the schema and is not recorded.

## Conventions

- Dates: ISO `YYYY-MM-DD`.
- `base_rent`: annual figure. Convert if the lease quotes monthly or per-SF.
- `escalation_pct`: percent value (`2.5` = 2.5%, not `0.025`).
- Notice window: `notice_min_months` = smaller number (deadline); `notice_max_months` = larger number (earliest notice).
- No renewal options → empty list.
- NNN = tenant pays its share of taxes/insurance/CAM separately. GRS = single all-in rent.

## How de-dup works

If a tenant, landlord, or property already exists (matched by name or address, case-insensitive), the loader reuses its existing `*_id`. Don't pre-assign IDs.

## Verifying the result

Open `Database.xlsx`. Rows 1–4 are headers; data starts at row 5. Your lease appears as the next row in `Leases`, with matching rows in `Tenants`, `Landlords`, `Properties`, and (if any) `RenewalOptions`.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Page in the approval card looks blank or has bad digits | Ask: "re-render at `--dpi 200`" |
| Loader aborts with `VALIDATION ERROR: <field>=…` | Bad enum/date in the record — correct and re-approve |
| `Could not read/write Database.xlsx after 3 attempts` | File is open in Excel or the mount is offline — close it / re-mount and retry |
| Approval card shows fields outside the schema (contacts, notes…) | Reject; tell the assistant "schema only" and re-approve |
