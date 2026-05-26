# Example queries

Twelve patterns across DB-only, visual, and hybrid paths. Each one names the
path so the skill picks the right routing.

## DB-only

### 1. "What leases expire in the next 18 months and have an unexercised renewal option?"
Filter: `expiration_date <= today + 18 months` AND lease has ≥1 option.
Show: tenant, property type, expiration_date, months_to_expiry, option count,
earliest notice deadline.

```python
from datetime import date
from dateutil.relativedelta import relativedelta
cutoff = date.today() + relativedelta(months=18)
opts = db["options"].groupby("lease_id").size().rename("n_options")
full = db["leases_full"].join(opts, on="lease_id")
m = (full["expiration_date"] <= cutoff) & (full["n_options"].fillna(0) > 0)
```

### 2. "Renewal notice windows opening in the next 90 days"
Compute `notice_window_open = expiration_date - notice_max_months months`.
Filter for those between today and today+90d. Order ascending. Show: tenant,
option sequence, window open date, window close date, days until open.

### 3. "Rent roll by property type"
Group `leases_full` by `property_type`. Aggregate:
- count of leases,
- sum of `base_rent`,
- sum of `size` where `size_unit == "RSF"` only,
- weighted-average `escalation_pct` (weight by `base_rent`).

### 4. "Top 5 tenants by share of annual base rent"
Group by `tenant_name`, sum `base_rent`, sort desc, percent of total.

### 5. "WALT by asset class"
For each lease: `months_to_expiry` (months between today and `expiration_date`).
Group by `property_type`. WALT = Σ(base_rent × months_to_expiry) / Σ(base_rent),
expressed in years.

### 6. "NNN vs gross exposure"
Group by `lease_type` (NNN, GRS). Count, sum base_rent, % of total.

### 7. "Five-year forward income forecast (escalation-weighted)"
For each year y in 1..5, for each lease compute
`base_rent × (1 + escalation_pct/100)^(y-1)` if the lease is still in term
during year y, else 0. Sum by year. Render a small markdown table.

## Visual

### 8. "Pull the site plan from the Saltgrass ground lease"
Slug: `Saltgrass_Storage`. Skim `page-02.png` for the table of contents to
locate the site-plan exhibit. Read those pages. Render a single-lease card
with a key-value summary of the site (acres, gate access, building footprint,
RV/boat area) and link to the page-NN file.

### 9. "What signage does Saltflats Tacos permit?"
Slug: `Saltflats_Tacos`. Find the signage exhibit (usually labeled "Sign
Criteria" or Exhibit D). Read those pages. Summarize: max sign area,
illumination, channel-letter rules, monument vs blade rules, landlord
approval requirements. Card-style widget.

### 10. "What's the cage configuration at Summit Grid?"
Slug: `Summit_Grid`. Find the suite layout / cage drawing exhibit. Read the
spec sheet (cage dimensions, cabinet count, power feeds per cabinet,
cross-connect schedule, raised floor / overhead routing). Card-style widget
with key specs.

## Hybrid

### 11. "For every lease with a renewal option in the next 24 months, surface the exhibit that shows expansion or ROFO premises"
DB filter (path 1 logic) → list of qualifying lease_ids → map each to its
slug via `slug-map` → for each lease, locate the expansion/ROFO exhibit
(typically late-numbered exhibit, e.g. Exhibit E or F). Read those pages.
Render a multi-lease widget with a dropdown selector. One card per lease
showing the expansion area summary (size, location relative to current
premises, when available, pricing mechanism) and the page reference.

### 12. "All medical-office leases — surface the exclusive-use clauses"
DB filter `property_type == "MED"` → for each, locate the exclusive-use
language. This sometimes lives in Article 6 / Permitted Use of the main
body, sometimes in an exhibit. Read both candidate sections. Quote the
operative language verbatim in a blockquote inside the widget. Multi-lease
widget with selector.

## How to present each path's output

- **DB-only** → markdown table inside the chat response. One-line context
  note above the table ("As of YYYY-MM-DD, N leases match.").
- **Visual** → short one-paragraph summary above an
  `mcp__visualize__show_widget` call. Card layout per `widget_template.md`.
- **Hybrid** → DB result line ("12 leases match the filter."), then the
  widget with a selector for the visual drill-down.

In all paths, end the response with a single follow-up suggestion using the
`sendPrompt(text)` mechanism inside the widget where it makes sense (e.g. a
button labeled "Show only retail tenants ↗" that calls `sendPrompt('Of
these, which are retail leases?')`).
