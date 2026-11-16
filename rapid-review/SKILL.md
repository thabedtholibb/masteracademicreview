---
name: rapid-review
description: "Conduct a rapid review — a streamlined systematic review for time-pressured decisions, with declared shortcuts (fewer databases, single reviewer, simplified extraction). Reported per Cochrane RAPID / adapted PRISMA. Use when the author needs a trustworthy-but-fast synthesis and accepts explicit methodological shortcuts. Trigger terms: rapid review, rapid evidence, Cochrane RAPID, accelerated review, tinjauan cepat."
metadata:
  version: "0.1.0"
  genre: rapid-review
  reporting_standard: "Cochrane RAPID / adapted PRISMA"
---

# Rapid Review

A **systematic review with explicit, declared shortcuts** for when a decision can't wait. The method stays reproducible, but you trade some comprehensiveness for speed — and you must say exactly what you traded.

## Scope

- **In scope:** a time-pressured evidence need; a focused question; the author accepts simplified methods.
- **Out of scope:** full comprehensiveness (→ `systematic-review`), statistical pooling (→ `meta-analysis`; rapid reviews usually summarize narratively).

## Pre-requisites

1. A focused question and a **deadline** — the deadline drives every shortcut.
2. The author's agreement to the shortcuts (recorded).

## Method (recommendation-first)

1. **Choose the shortcuts (ranked).** Present the tiers in priority order and recommend the least-damaging set for the deadline:
   - **#1** — 2 databases + grey literature, single reviewer with a 10–20% verification sample, simplified extraction.
   - **#2** — 1 database + reference-mining, single reviewer, narrative summary only.
   - **#3** — search only, no full-text retrieval for borderline records.
   The author picks a tier; each chosen shortcut is recorded in the methods.
2. **Search** — follow `shared/search_strategy.md` (fewer sources, documented).
3. **Screen** — follow `shared/screening.md`; single reviewer with a verification sample.
4. **Extract & summarize** — narrative summary per outcome; no statistical pooling.
5. **Report** — adapted PRISMA; a mandatory **"shortcuts taken"** subsection.

## Structure (adapted PRISMA)

```
Title (identifies as a rapid review)
Abstract
1. Introduction — rationale + urgency
2. Methods — shortcuts taken (explicit), search, screening, extraction
3. Results — included studies, summary per outcome
4. Discussion — what the shortcuts limit, implications
```

## Gate (Cochrane RAPID)

- [ ] Every shortcut is declared in a "shortcuts taken" subsection.
- [ ] The search and screening are documented enough to be re-run.
- [ ] The deadline and how it shaped the method are stated.

## Guardrails

- A rapid review's honesty lives in its declared shortcuts. Never present a rapid review as a full systematic review.
- If the deadline is the only reason for the shortcuts, say so.
