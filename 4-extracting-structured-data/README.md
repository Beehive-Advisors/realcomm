# Exercise 4: Extracting Structured Data

In Exercise 3 you queried leases. Now you'll pull **structured data** out of one — the core of almost every real estate workflow. By the end you'll have two things: a **abstracte lease** and a reusable **abstraction skill**. In Exercise 5 you'll use both to *measure* how good the extraction actually is.

> **Point Cowork at this folder** (`4-extracting-structured-data`), not the repo root.

Files in this directory:
- `schema.docx` — the data definition. The first rows are filled in; you'll complete the rest.
- `Ironhide_Cold_Logistics_Industrial_Lease.pdf` — the one lease you'll work with.
- `instructor/` — ignore this; it's the answer key.

---

## Exercise 4.1: Finish the schema

A **schema** is the formal definition of the data you want to extract. Open [`schema.docx`](./schema.docx). For each field you define three things:

1. **Name** — what the field is called.
2. **Description** — what it is and where to find it in the lease.
3. **Type** — the output format (string, number, date, enum).

Let's fill this out together. 

## Exercise 4.2: Abstract the Ironhide lease

Point Claude at `schema.docx` and `Ironhide_Cold_Logistics_Industrial_Lease.pdf` and ask it to extract the data. A good prompt names the document, the schema, and the output shape:

> Using `schema.docx` as the field definitions, abstract the Ironhide lease. Return the result as a table with one row per field, and follow the Match Rule column.

Look it over. Does anything seem off? Hold that thought — Exercise 5 is where we stop eyeballing and start measuring.

## Exercise 4.3: Write the result to an Excel spreadsheet

Now have Claude save the abstraction into an excel file.

## Exercise 4.4: Turn this into a skill

You don't want to re-type that prompt every time. Ask Claude to package this conversation into an **agent skill**:

> Create an agent skill from this conversation that abstracts a commercial lease using my schema. Ask me any clarifying questions first.

Agent skills are just text files describing an action you want to run on demand. Review what Claude proposes, answer its questions, then save it.

## Exercise 4.5: Save the skill

Click **"Save Skill"** in the Claude interface:

![Save skill button on the Claude interface](../readme-images/save-skill.png)

Now you can invoke it with slash (`/`) notation in any chat. To view it: Customize → Skills → Personal Skills → `YOUR-SKILL-NAME`.

You'll run this skill across a batch of leases in Exercise 5 — and find out how often it's right.

---

### What you learned
- A schema defines not just the data, but what counts as a **correct** answer.
- An **agent skill** turns a one-off prompt into a repeatable tool.
