---
name: systematic-review
description: "Conduct a systematic review — a reproducible, comprehensive synthesis of all evidence on a focused question, following a pre-registered protocol and reported per PRISMA 2020. Use when the author needs a protocol-driven search, dual screening, a PRISMA flow diagram, risk-of-bias assessment, and a transparent audit trail. Trigger terms: systematic review, PRISMA, systematic literature review, SLR, tinjauan sistematis, systematic review protocol."
metadata:
  version: "0.1.0"
  genre: systematic-review
  reporting_standard: "PRISMA 2020 (27 items) + PRISMA-S"
---

# Systematic Review

You run a **reproducible, protocol-driven** synthesis. Every methodological decision is documented so another researcher could rerun the review and reach the same study set. This is the review type where the process *is* part of the result.

## Scope

- **In scope:** a focused question answered comprehensively and reproducibly; requires a protocol and PRISMA reporting.
- **Out of scope:** no protocol / quick expert summary (→ `narrative-review`), statistical pooling of effect sizes (→ `meta-analysis`, which *extends* this skill), a single book (→ `book-review`).

## Pre-requisites (fail-closed)

Before writing anything, confirm the author has — or is willing to create:

1. A focused research question in a structured frame (PICO/PICo/SPIDER).
2. A protocol (ideally registered, e.g. PROSPERO) stating eligibility criteria and methods *in advance*.
3. Access to the databases to be searched.

If these are missing, stop and establish them first — do not run an un-protocoled "systematic" review and call it systematic.

## Method (run in order)

1. **Frame & protocol** — write the question, eligibility criteria, and methods; register if possible.
2. **Search** — follow `shared/search_strategy.md`; record per-database queries and raw counts (PRISMA-S).
3. **Screen** — follow `shared/screening.md`; dual reviewers, ordered exclusion reasons, agreement (κ/PABAK).
4. **Extract** — follow `shared/data_extraction.md`; build the characteristics table.
5. **Risk of bias** — follow `shared/risk_of_bias.md`; recommend the tool by design (**#1** = the design-matched tool), naming the runner-up only if ambiguous.
6. **Synthesize** — narrative synthesis of the included studies; group by outcome/theme. If the author wants statistical pooling, recommend `meta-analysis` (**#1**) rather than doing it here.
7. **Report** — write to PRISMA 2020; generate the flow diagram with `shared/scripts/prisma_flow.py`.

## Flow diagram (deterministic)

Generate the PRISMA flow from your screening counts:

```python
from prisma_flow import render_prisma
render_prisma({
    "database_records": [("PubMed", 102), ("Scopus", 88)],
    "other_sources": 9,
    "after_dedup": 140,
    "screened": 140,
    "excluded_title_abstract": 95,
    "sought_retrieval": 45,
    "not_retrieved": 4,
    "assessed": 41,
    "excluded_fulltext": [("Wrong population", 12), ("Wrong outcome", 11), ("Wrong design", 8)],
    "included": 10,
}, "prisma_flow.svg")
```

## Structure (PRISMA-aligned)

```
Title (identifies as a systematic review)
Abstract (structured)
1. Introduction — rationale + objectives (PICO)
2. Methods — eligibility, search, selection, data items, RoB, synthesis, bias, certainty
3. Results — study selection (flow diagram), characteristics, RoB, individual studies, synthesis
4. Discussion — interpretation, evidence limitations, process limitations, implications
Other — registration, funding, conflicts, data availability
```

## Standards & sources

Governing standard: **PRISMA 2020** (Page et al., 2021, doi:10.1136/bmj.n71) with **PRISMA-S** for search reporting (Rethlefsen et al., 2021, doi:10.1186/s13643-020-01542-z). Method sources: *Cochrane Handbook* v6.4 (2023), RoB 2 (Sterne et al., 2019, doi:10.1136/bmj.l4898), ROBINS-I (Sterne et al., 2016, doi:10.1136/bmj.i4919), GRADE (Guyatt et al., 2008, doi:10.1136/bmj.39489.470347.AD). Full citations and the Q1-readiness checklist: `shared/method_sources.md`.

## Gate (PRISMA 2020, 27 items)

Walk `shared/reporting_standards.md` item by item and mark each **present / partial / missing**. Flag every `missing` item; the review is not "done" until each is satisfied or explicitly waived by the author with a recorded reason. The flow diagram must exist and match the reported counts.

## Guardrails

- Never invent record counts, study details, or outcomes. Missing data is recorded as missing.
- Screening decisions belong to the author (and a second reviewer); you record, reconcile, and audit — you do not unilaterally decide inclusion for a systematic review.
- "Systematic" is a claim about method. If the protocol is not followed, call it what it is and route to `narrative-review`.
