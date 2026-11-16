---
name: scoping-review
description: "Conduct a scoping review — map the breadth and volume of evidence on a broad topic, identify gaps, and inform whether a full systematic review is feasible. Reported per PRISMA-ScR. Use when the goal is to map a field, not to answer a narrow question or pool effect sizes. Trigger terms: scoping review, PRISMA-ScR, scoping study, evidence map, mapping review, pemetaan literatur, tinjauan pemetaan."
metadata:
  version: "0.1.0"
  genre: scoping-review
  reporting_standard: "PRISMA-ScR (22 items)"
---

# Scoping Review

You map the **breadth and volume** of evidence on a topic — what has been studied, with what methods, and where the gaps are. You do **not** answer a narrow clinical question and do **not** appraise study quality (unlike a systematic review).

## Scope

- **In scope:** broad or emerging topics; mapping concepts, sources, and evidence types; informing whether a systematic review is warranted.
- **Out of scope:** answering a focused question (→ `systematic-review`), pooling effect sizes (→ `meta-analysis`), synthesizing reviews (→ `umbrella-review`), synthesizing qualitative findings (→ `meta-synthesis`).

## Pre-requisites

1. A broad research question with a clear **scope** — the PCC frame (Population, Concept, Context) is the norm.
2. A protocol stating the mapping objective and the charting fields in advance.

## Method

1. **Frame (PCC)** — Population, Concept, Context.
2. **Search** — follow `shared/search_strategy.md`. Scoping searches are deliberately broad; document databases, full query, and limits.
3. **Screen** — follow `shared/screening.md` (title/abstract → full text; dual reviewer recommended).
4. **Chart the data** — extract study characteristics, concept categories, and evidence types into a matrix (see `shared/data_extraction.md`, charting focus rather than outcomes). No risk-of-bias appraisal — PRISMA-ScR permits it as optional, but it is not the norm.
5. **Map & report** — present the evidence as a descriptive map (tables, matrices, frequency counts) and identify gaps; generate the PRISMA-ScR flow diagram with `shared/scripts/prisma_flow.py`.

## Structure (PRISMA-ScR)

```
Title (identifies as a scoping review)
Abstract (structured)
1. Introduction — rationale + objectives (PCC) + review question
2. Methods — protocol, eligibility, search, selection, charting
3. Results — selection (flow diagram), characteristics of sources, mapping of evidence, gaps
4. Discussion — summary, limitations, implications
```

## Decision points (recommendation-first)

- **Framing** — recommend **PCC (#1)** for mapping questions.
- **Quality appraisal** — recommend **skipping it (#1)**; PRISMA-ScR permits it as optional, but it is not the norm for scoping.

## Gate (PRISMA-ScR, 22 items)

Walk the PRISMA-ScR checklist in `shared/reporting_standards.md` item by item; mark each **present / partial / missing** and flag every missing item. The flow diagram must exist and match the reported counts.

## Guardrails

- A scoping review *maps*; it does **not** judge quality or pool results. Do not claim "systematic review" or report a pooled estimate.
- The gap analysis must follow from the charted evidence, not from what you wished were there.
