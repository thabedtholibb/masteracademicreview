---
name: rapid-review
description: "Conduct a rapid review: a streamlined systematic review for time-pressured decisions, with declared shortcuts (fewer databases, single reviewer, simplified extraction). Reported per Cochrane rapid-review guidance / adapted PRISMA. Use when the author needs a trustworthy-but-fast synthesis and accepts explicit methodological shortcuts. Trigger terms: rapid review, rapid evidence, Cochrane RAPID, accelerated review, tinjauan cepat."
metadata:
  version: "0.1.0"
  genre: rapid-review
  reporting_standard: "Cochrane rapid-review guidance (2021/2024) + adapted PRISMA"
---

# Rapid Review

A **systematic review with explicit, declared shortcuts** for when a decision can't wait. The method stays reproducible, but you trade some comprehensiveness for speed, and you must say exactly what you traded.

## Scope

- **In scope:** a time-pressured evidence need; a focused question; the author accepts simplified methods.
- **Out of scope:** full comprehensiveness (→ `systematic-review`), statistical pooling (→ `meta-analysis`; rapid reviews usually summarize narratively).

## Pre-Requisites

1. A focused question and a **deadline**: the deadline drives every shortcut.
2. The author's agreement to the shortcuts (recorded).

## Method (JEV)

1. **Choose the shortcuts (ranked).** Present the tiers in priority order and recommend the least-damaging set for the deadline:
   - **#1:** 2 databases + grey literature, single reviewer with a 10–20% verification sample, simplified extraction.
   - **#2:** 1 database + reference-mining, single reviewer, narrative summary only.
   - **#3:** search only, no full-text retrieval for borderline records.
   The author picks a tier; each chosen shortcut is recorded in the methods.
2. **Search:** follow `shared/search_strategy.md` (fewer sources, documented). Deduplicate the database exports with `mar dedup --source <Name>=<file> ...`: certain duplicates are removed, near-matches are listed for you to decide (JEV), and the PRISMA identification counts are written for you.
3. **Screen:** follow `shared/screening.md`; single reviewer with a verification sample.
4. **Extract & summarize:** narrative summary per outcome; no statistical pooling.
5. **Report:** adapted PRISMA; a mandatory **"shortcuts taken"** subsection.

## Structure (Adapted PRISMA)

```
Title (identifies as a rapid review)
Abstract
1. Introduction: rationale + urgency
2. Methods: shortcuts taken (explicit), search, screening, extraction
3. Results: included studies, summary per outcome
4. Discussion: what the shortcuts limit, implications
References
```

## Decision Points (JEV)

Every decision here follows the JEV protocol (`../shared/jev.md`): ranked options, **#1 recommended**, one line of evidence each, what would change the ranking, and the author approves. Approved choices go into `decisions.md`.

- **Protocol.** **#1 recommended:** a short registered protocol (PROSPERO or OSF) even under time pressure; generate it with `protocol.py --template rapid-review`.
- **Risk of bias.** **#1 recommended:** single assessor with verification by a second reviewer, limited to the critical outcomes. Skipping it entirely is not an option.
- **Synthesis.** **#1 recommended:** narrative summary per outcome; no statistical pooling under rapid-review shortcuts.
- *What changes the ranking:* a longer deadline moves the review up to `systematic-review`.

## Standards & Sources

Governing standard: **Cochrane Rapid Reviews Methods Group guidance** (Garritty et al., 2021, doi:10.1016/j.jclinepi.2020.10.007; updated 2024, doi:10.1136/bmj-2023-076335), reported through an **adapted PRISMA 2020** flow. Method sources: Tricco et al. 2015 (doi:10.1186/s12916-015-0465-6), Khangura et al. 2012 (doi:10.1186/2046-4053-1-10). Full citations: `shared/method_sources.md`.

## Gate (Cochrane Rapid-Review Guidance)

- [ ] Every shortcut is declared in a "shortcuts taken" subsection.
- [ ] The search and screening are documented enough to be re-run.
- [ ] The deadline and how it shaped the method are stated.

**Automated Gate:** run these before you call the review done. Both are offline; `pip install masteracademicreview` provides `mar`.

- [ ] `mar check-review review.md` reports **0 errors**: header fields, the sections this genre needs, citations matched to references, referenced and required artifacts present, no placeholders, and a gate line that matches the checklist. It ranks what to fix first.
- [ ] `mar verify-refs review.md` finds no unresolved citation or duplicate DOI; add `--online` before submission to check every reference against Crossref.

## Guardrails

- A rapid review's honesty lives in its declared shortcuts. Never present a rapid review as a full systematic review.
- If the deadline is the only reason for the shortcuts, say so.
