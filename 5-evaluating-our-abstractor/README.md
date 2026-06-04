# Exercise 5: Evaluating Our Abstractor

In Exercise 4 you built an abstraction skill and ran it on a single lease. Eyeballing one result is fine for a demo, but in production you need to *know* how often your skill is right. In this exercise you'll run the skill across several leases and grade its output against a **golden dataset** — a hand-verified answer key — so the question stops being "does this look right?" and becomes "what's our accuracy?"

> **Point Cowork at this folder** (`5-evaluating-our-abstractor`), not the repo root.

Files in this directory:
- `leases/` — three leases to abstract (`aspen_hollow`, `ironhide`, `saltflats`).
- `golden-dataset.xlsx` — the answer key, with the correct value for every field of every lease.

## Exercise 5.1: Run your skill across the leases

Invoke the abstraction skill you saved in Exercise 4 and point it at the three leases in the `leases/` folder. Ask Claude to return one record per lease — and to include not just the simple fields, but the full rent schedule for each one. This is the raw output we're about to grade.

## Exercise 5.2: Evaluate against the golden dataset

Now ask Claude to compare its own output to `golden-dataset.xlsx`, field by field, and tell you where it matches and where it misses.

The catch is formatting. A correct answer can *look* different from the golden value — `$641,625.00` vs `641625`, `December 1, 2026` vs `2026-12-01`, `UT` vs `Utah`, a blank cell vs `null`. Make sure Claude normalizes formatting before scoring, so it's grading the actual data and not the punctuation. Remember to have it grade the rent schedule period-by-period, since that's where most of the real differences hide.

## Exercise 5.3: Build an artifact to view the results

A wall of pass/fail text is hard to read. Ask Claude to build you an artifact — a visual scorecard — so you can see the whole eval at a glance: one row per field, one column per lease, color-coded matches and misses, your running accuracy up top, and a way to filter down to just the misses. This is what you'd actually show a stakeholder.

## Iterate

Here's the payoff. Once you can *measure* accuracy, you can improve it. Look at where your skill missed, fix the skill, then re-run 5.1 → 5.2 → 5.3 and watch the number move:

- **Vague schema?** Tighten the field description in your skill so Claude knows exactly what to look for.
- **Ambiguous?** Pin the rule down in the schema's match-rule column.
- **Hallucination?** Add a guardrail — for example, tell it to return null when no renewal option exists instead of inventing one.

---

### What you learned
- A **golden dataset** turns "looks right" into a measurable accuracy number.
- Most disagreements are formatting, not data — **normalize before you grade**.
- An eval you can *see* is an eval you can *act on*: measure, fix the skill, re-run, repeat.
