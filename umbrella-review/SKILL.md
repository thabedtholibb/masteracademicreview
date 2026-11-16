---
name: umbrella-review
description: "Conduct an umbrella review (overview of reviews): synthesize existing systematic reviews and meta-analyses on a topic, appraise their quality with AMSTAR-2, and report per PRIOR. Use when the unit of analysis is reviews themselves, not primary studies. Trigger terms: umbrella review, overview of reviews, review of reviews, PRIOR, AMSTAR-2."
metadata:
  version: "0.1.0"
  genre: umbrella-review
  reporting_standard: "PRIOR"
---

# Umbrella Review

You synthesize **existing systematic reviews and meta-analyses** rather than primary studies. The unit of analysis is the review itself.

## Scope

- **In scope:** a topic already covered by multiple SRs/meta-analyses; the goal is a high-level, trustworthy summary of what the reviews conclude.
- **Out of scope:** primary-study synthesis (→ `systematic-review` / `meta-analysis`), mapping breadth (→ `scoping-review`).

## Pre-Requisites

1. A focused question and **≥2 eligible systematic reviews/meta-analyses**.
2. A protocol defining which reviews are eligible (e.g. must report a search and a quality assessment).

## Method

1. **Search for reviews:** follow `shared/search_strategy.md`, filtering for the SR/meta-analysis study type.
2. **Screen:** follow `shared/screening.md`; eligibility targets *reviews*, not primary studies.
3. **Assess review quality:** apply **AMSTAR-2** to each included review (see `shared/risk_of_bias.md`).
4. **Handle overlap:** compute and report the *corrected covered area (CCA)* to show how much primary-study evidence is double-counted across reviews.
5. **Synthesize per outcome:** summarize each review's conclusion and certainty (GRADE); note where reviews disagree and why.
6. **Report:** write to PRIOR (`shared/reporting_standards.md`).

## Structure (PRIOR)

```
Title (identifies as an overview/umbrella review)
Abstract (structured)
1. Introduction: rationale + objectives
2. Methods: eligibility, search, selection, AMSTAR-2, overlap, certainty
3. Results: reviews included, their quality (AMSTAR-2), overlap (CCA), synthesis per outcome
4. Discussion: interpretation, limitations, implications
```

## Decision Points (JEV)

Every decision here follows the JEV protocol (`../shared/jev.md`): ranked options, **#1 recommended**, one line of evidence each, what would change the ranking, and the author approves. Approved choices go into `decisions.md`.

- **Quality tool:** recommend **AMSTAR-2 (#1)** for appraising included reviews.
- **Overlap:** recommend reporting the **corrected covered area (CCA) (#1)** to show double-counting.
- **Discordant reviews:** recommend reporting each review's result next to its AMSTAR-2 rating (#1); do not re-pool primary studies unless that is the stated aim.
- **High overlap:** recommend a pre-stated rule (#1): keep the most recent, highest-confidence review per question.

## Standards & Sources

Governing standard: **PRIOR** (Gates et al., 2022, doi:10.1136/bmj-2022-070849). Method sources: Aromataris et al. 2015 (doi:10.1097/XEB.0000000000000055), AMSTAR 2 (Shea et al., 2017, doi:10.1136/bmj.j4008), and Pieper et al. 2015 on AMSTAR's measurement properties (doi:10.1016/j.jclinepi.2014.12.009). Full citations and the Q1-readiness checklist: `shared/method_sources.md`.

## Gate (PRIOR)

Walk the PRIOR items in `shared/reporting_standards.md`; flag every missing item. AMSTAR-2 ratings and the CCA must be reported.

## Guardrails

- The umbrella review's certainty is capped by the quality of its included reviews; a review rated *critically low* by AMSTAR-2 must not be leaned on for strong conclusions.
- Do **not** re-pool effect sizes across reviews. You synthesize their conclusions, not their numbers.
