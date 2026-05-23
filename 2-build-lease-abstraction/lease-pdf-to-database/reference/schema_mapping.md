# Schema mapping reference

How lease language maps into the JSON record and onward into the five
`Database.xlsx` tables. The flat extraction schema is the source of truth
(`../../Completed - Schema.xlsx`); the database normalizes it across five
sheets linked by primary/foreign keys.

## Database.xlsx layout (important)

Every sheet has **4 header rows** before any data:

| Row | Content |
|-----|---------|
| 1 | column names (`tenant_id`, `tenant_name`, …) |
| 2 | PK / FK / CHECK-constraint annotations |
| 3 | data type |
| 4 | description |

**Real data starts on row 5.** `load_record.py` already accounts for this —
never write into rows 1–4.

## Table relationships

```
Tenants (tenant_id PK) ─┐
Landlords (landlord_id PK) ─┤
Properties (property_id PK) ─┼─< Leases (lease_id PK,
                              │      tenant_id FK, landlord_id FK, property_id FK)
                              └────────────┘
                                           └─< RenewalOptions (option_id PK, lease_id FK)
```

One lease row links to exactly one tenant, one landlord, one property, and
zero-or-more renewal-option rows.

## De-duplication rule

A landlord (and sometimes a property or tenant) recurs across leases. Before
inserting, the loader checks whether the entity already exists and **reuses
its existing key** instead of creating a duplicate:

- **Tenants** — matched on `tenant_name`
- **Landlords** — matched on `landlord_name`
- **Properties** — matched on `premises_address`

Matching is case-insensitive, whitespace-collapsed, and ignores a trailing
period. If you intend a genuinely new entity that happens to share a name,
disambiguate the name/address before loading.

## Field-by-field

### Tenants / Landlords
| JSON field | Source in lease | Notes |
|---|---|---|
| `*_name` | Article 1 "Tenant" / "Landlord" defined term | Full legal name incl. ", LLC" |
| `*_entity_type` | from the legal name | LLC, Corp, REIT, Trust, Individual… |
| `*_contact_name` | Notice Address / Tenant Contact exhibit | |
| `*_contact_email` | Notice Address ("courtesy email copy to …") | |
| `*_contact_phone` | Tenant Contact Information exhibit table | "" if none stated |
| `notes` | jurisdiction, broker, anything useful | free text |

### Properties
| JSON field | Source | Enum / notes |
|---|---|---|
| `premises_address` | Building / Premises defined term | "Street, City, ST ZIP" |
| `property_type` | asset class of the deal | **OFF** office · **MED** medical office · **IND** industrial · **RET** retail/restaurant · **COW** coworking · **LAB** life-sciences lab · **DC** data center · **GND** ground/land lease |
| `size` | rentable area or land area | decimal |
| `size_unit` | unit for `size` | **RSF** rentable sq ft · **ACRE** acres. Use RSF for building leases; ACRE for ground leases. |
| `notes` | building character, single/multi-tenant, land acreage | |

### Leases
| JSON field | Source | Enum / notes |
|---|---|---|
| `commencement_date` | Commencement Date | ISO `YYYY-MM-DD` |
| `expiration_date` | Expiration Date | ISO `YYYY-MM-DD` |
| `term_months` | Term ("(120) full calendar months") | integer |
| `lease_type` | rent structure | **NNN** triple-net (tenant pays its share of taxes/insurance/CAM separately) · **GRS** gross |
| `base_rent` | **starting** base rent at the first full (non-abated) rate | decimal currency |
| `base_rent_frequency` | whether `base_rent` is annual or monthly | **ANNUAL** · **MONTHLY** — state which you recorded |
| `escalation_pct` | annual step-up | the **percent value itself**, e.g. `2.5` means 2.5% (NOT the fraction `0.025`). Derive from the rent schedule if not stated outright. |
| `security_deposit_amount` | Security Deposit / Letter of Credit amount | decimal currency |
| `security_deposit_type` | form of the deposit | **Cash** · **CL** letter of credit · **NONE** |
| `permitted_use` | Permitted Use defined term | summarize if very long |
| `notes` | abatement, TI allowance, escalation detail, caveats | |

### RenewalOptions (one object per option)
| JSON field | Source | Enum / notes |
|---|---|---|
| `option_sequence` | order of the option | 1, 2, 3 … |
| `renewal_term_months` | length of this option | integer (e.g. 60 for 5 years) |
| `renewal_rent_basis` | how renewal rent is set | **FMR** fair market rent · **FIX** fixed/stated · **CPI** index-adjusted · **NONE** |
| `renewal_rent_value` | stated rent if FIX (currency), or CPI cap if CPI (percent value, e.g. `3` for a 3% cap) | `null` for FMR/NONE |
| `notice_min_months` | minimum months of notice required (closest-to-expiry edge of the window) | e.g. lease says "not later than 15 months before expiry" → `15` |
| `notice_max_months` | maximum months early notice may be given (furthest-from-expiry edge) | e.g. "not earlier than 18 months before expiry" → `18` |
| `notes` | exercise conditions, occupancy threshold, time-of-the-essence | |

**Notice window convention:** record the window as
`notice_min_months` = the smaller number (deadline, latest you may notify) and
`notice_max_months` = the larger number (earliest you may notify), and restate
the literal lease wording in `notes` so there is no ambiguity. A lease that
says "not earlier than 18 months and not later than 15 months before
expiration" → `notice_min_months=15`, `notice_max_months=18`.

If the lease has **no renewal option**, set `renewal_options` to `[]` (empty).
Do not invent a `NONE` row unless you specifically want a placeholder.
