# Lease database schema

`Database.xlsx` has 5 sheets. Every sheet has **4 header rows** (column names,
constraint tags, types, descriptions) before any data. Real data starts on
row 5. `scripts/query_db.py` already handles this — use it.

## Tables

### Tenants
- `tenant_id` (PK)
- `tenant_name`

### Landlords
- `landlord_id` (PK)
- `landlord_name`

### Properties
- `property_id` (PK)
- `premises_address`
- `property_type` enum:
  - `OFF` Office
  - `MED` Medical office
  - `IND` Industrial
  - `RET` Retail / restaurant
  - `COW` Coworking
  - `LAB` Life-sciences lab
  - `DC` Data center
  - `GND` Ground / land lease
- `size` (decimal)
- `size_unit` enum: `RSF`, `ACRE`

### Leases
- `lease_id` (PK)
- `tenant_id`, `landlord_id`, `property_id` (FKs)
- `commencement_date`, `expiration_date` (ISO `YYYY-MM-DD` strings)
- `term_months` (integer)
- `lease_type` enum: `NNN` (triple-net), `GRS` (gross / modified gross)
- `base_rent` (decimal USD, **annual**, first full non-abated year)
- `escalation_pct` (decimal percent, e.g. `2.5` means 2.5%)
- `security_deposit_amount` (decimal USD; `0` if none)
- `security_deposit_type` enum: `Cash`, `CL` (letter of credit), `NONE`
- `permitted_use` (free text)

### RenewalOptions
- `option_id` (PK)
- `lease_id` (FK)
- `option_sequence` (1, 2, 3 ...)
- `renewal_term_months` (integer)
- `renewal_rent_basis` enum: `FMR`, `FIX`, `CPI`, `NONE`
- `notice_min_months` (smaller number — deadline / latest you may notify)
- `notice_max_months` (larger number — earliest you may notify)

## Joins you'll write constantly

```python
from query_db import load
db = load("Database.xlsx")

# One row per lease, with tenant/landlord/property denormalized:
full = db["leases_full"]

# Leases with their options (LEFT JOIN — leases without options keep NaN):
with_opts = full.merge(db["options"], on="lease_id", how="left")
```

## Computed columns

`scripts/query_db.py` exposes a `with_dates(df, today=None)` helper that adds
these to a leases DataFrame:

- `months_to_expiry` = whole months between today and `expiration_date`
- `notice_window_open` = `expiration_date - notice_max_months` (per option)
- `notice_window_close` = `expiration_date - notice_min_months` (per option)
- `notice_window_is_open` = today between (open, close), inclusive

Use whole months so "expires in 18 months" matches a lease expiring exactly
18 months from today.

## Common pitfalls

- `property_type='GND'` rows use `size_unit='ACRE'` — exclude them when
  summing rentable square feet across the portfolio.
- A lease can have zero, one, or many renewal options. Use `LEFT JOIN`
  whenever your filter "matters" only when an option exists (otherwise
  leases without options drop silently).
- Sample portfolio dates start in 2026 — don't assume "today" is always after
  the commencement dates. Some leases may not have started yet.
- Some `lease_type='GRS'` leases are actually modified gross with operating
  expense pass-throughs above a base year — but they're tagged GRS, not NNN.
