# Exercise 5: Evaluating Our Abstractor

Run your skill across three leases, grade the output against the golden dataset, then have Claude build an artifact to view the results.

> **Point Cowork at this folder** (`5-evaluating-our-abstractor`).

## Files

- `leases/` — three lease PDFs: `aspen_hollow`, `ironhide`, `saltflats`.
- `schema.docx` — the field definitions and match rules.
- `golden-dataset.xlsx` — verified answer key. `GoldenAnswers` tab (one row per lease) + `RentSchedule` tab (one row per rent period).
- `instructor/` — ignore.

## 5.1 — Run your skill

> `/YOUR-SKILL-NAME` — abstract all three leases in `leases/` using `schema.docx`. Return one record per lease, keyed by `lease_id` (`aspen_hollow`, `ironhide`, `saltflats`), with every schema field plus the full rent schedule.

## 5.2 — Evaluate against the golden dataset

> Compare my skill's output to `golden-dataset.xlsx`. For each lease and field, tell me whether it matches, and grade `rent_schedule` period-by-period. Normalize formatting first — `$641,625.00`/`641625`, `December 1, 2026`/`2026-12-01`, `UT`/`Utah`, blank/`null` all count as equal.

## 5.3 — Build an artifact

> Build me an artifact that shows this eval as a scorecard: one row per field, one column per lease, color-coded match/partial/miss, running accuracy at the top, and a "show misses only" toggle. Grade the rent schedule period-by-period and show which rows matched.

## Iterate

Fix the skill, then re-run 5.1 → 5.2 → 5.3 and watch the number move:

- **Vague schema?** Tighten the field description in your skill.
- **Ambiguous?** Pin the rule down in the schema's match-rule column.
- **Hallucination?** Add a guardrail ("if no renewal option exists, return null").
