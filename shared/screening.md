# Screening (shared core)

Use for `systematic-review` and `meta-analysis`; adapted for any review with inclusion/exclusion. Screening is the reproducible filter that turns raw search results into the final included set. Every decision must be traceable.

## 1. Freeze eligibility criteria before screening

Write inclusion and exclusion criteria explicitly, tied to the PICO/PICo frame. Each criterion must be a **yes/no** question answerable from the record. Vague criteria ("recent studies") are not allowed; replace with operational ones ("published 2015–2026").

## 2. Two stages

1. **Title/abstract screening** — exclude records clearly ineligible on title/abstract alone.
2. **Full-text screening** — retrieve remaining records and assess against full criteria.

At full-text stage, **every excluded study must carry an exclusion reason**. Use an ordered reason list so a study excluded for multiple reasons gets exactly one primary reason:

1. Wrong population
2. Wrong intervention/exposure
3. Wrong comparator
4. Wrong outcome
5. Wrong study design
6. Wrong publication type (e.g. conference abstract, editorial)
7. Full text unavailable
8. Duplicate (already resolved at dedup)
9. Language
10. Other (specify)

## 3. Dual screening (required for systematic/meta)

- Two reviewers screen independently; conflicts resolved by discussion or a third reviewer.
- Do **not** silently default to "include on conflict" — adjudicate each conflict.
- Record inter-rater agreement (Cohen's κ, or PABAK for skewed prevalence) at title/abstract stage.

## 4. Track the flow (PRISMA)

For each stage, record the running counts that feed `shared/scripts/prisma_flow.py`:

- records identified per database (from search)
- records after deduplication
- records screened (title/abstract)
- records excluded at title/abstract
- records sought for full-text retrieval
- records not retrieved
- records assessed for eligibility
- records excluded at full-text (with reasons)
- studies included

## 5. Output

Produce a screening log (CSV or table) with one row per record: `record_id | title | stage | decision | exclusion_reason | reviewer`. This log is the auditable artifact behind the PRISMA flow diagram.

## Guardrails

- Never invent records or counts. If a stage's count is unknown, mark it `pending`, do not estimate.
- A study that fails one criterion is excluded once, with its primary reason — do not double-count.
- Screening decisions are the author's (and any second reviewer's), not yours alone; you record and reconcile, you do not unilaterally decide for a systematic review.
