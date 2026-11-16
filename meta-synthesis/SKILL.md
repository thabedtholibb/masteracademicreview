---
name: meta-synthesis
description: "Conduct a qualitative evidence synthesis (meta-synthesis): aggregate and interpret findings across qualitative studies into new themes or theory, reported per ENTREQ. Use when the primary studies are qualitative (interviews, ethnography, focus groups) and the goal is thematic synthesis or theory-building, not statistical pooling. Trigger terms: meta-synthesis, qualitative synthesis, meta-ethnography, thematic synthesis, ENTREQ, sintesis kualitatif."
metadata:
  version: "0.1.0"
  genre: meta-synthesis
  reporting_standard: "ENTREQ (21 items)"
---

# Meta-Synthesis (Qualitative Evidence Synthesis)

You synthesize **qualitative** studies into higher-order themes or theory. There is no statistics here: the "effect" is interpretive insight.

## Scope

- **In scope:** primary qualitative studies (interviews, focus groups, ethnography, phenomenology) on a shared phenomenon; the goal is new interpretation or theory.
- **Out of scope:** quantitative studies or pooling (→ `meta-analysis`), mapping breadth (→ `scoping-review`).

## Pre-Requisites

1. A phenomenon-focused question (PICo or SPIDER frame).
2. A body of eligible qualitative studies with extractable findings (themes, categories, participant quotes).

## Method

1. **Frame (PICo/SPIDER):** Population, phenomenon of Interest, Context.
2. **Search & screen:** follow `shared/search_strategy.md` and `shared/screening.md`; add qualitative search terms (experience, perception, lived, meaning).
3. **Appraise:** apply the **CASP Qualitative** checklist (see `shared/risk_of_bias.md`) to judge trustworthiness; it informs interpretation, it does not exclude.
4. **Extract findings:** extract each study's themes, categories, and supporting quotes (see `shared/data_extraction.md`).
5. **Synthesize (JEV):** recommend the method by goal, then state it: **thematic synthesis (#1, default)** for descriptive → analytical themes; **meta-ethnography (#2)** for a new interpretive theory; **meta-aggregation (#3)** for practical recommendations. Build the higher-order themes or theory.
6. **Report:** write to ENTREQ (`shared/reporting_standards.md`).

## Structure (ENTREQ-aligned)

```
Title
Abstract
1. Introduction: the phenomenon and why synthesis is needed
2. Methods: search, appraisal (CASP), extraction, synthesis method
3. Findings: the developed themes, each grounded in the studies' data (with quotes)
4. Discussion: the new interpretation, trustworthiness, limitations
```

## Decision Points (JEV)

Every decision here follows the JEV protocol (`../shared/jev.md`): ranked options, **#1 recommended**, one line of evidence each, what would change the ranking, and the author approves. Approved choices go into `decisions.md`.

- **Synthesis method.** Ranked in the Method section above (thematic synthesis #1, meta-ethnography #2).
- **Appraisal use.** **#1 recommended:** CASP Qualitative to describe trustworthiness and in a sensitivity check; do not exclude studies by score alone.
- **Reporting.** **#1 recommended:** ENTREQ, with every theme traced to its source studies and quotes.

## Standards & Sources

Governing standard: **ENTREQ** (Tong et al., 2012, doi:10.1186/1471-2288-12-181). Method sources: Thomas & Harden 2008 for thematic synthesis (doi:10.1186/1471-2288-8-45), Noblit & Hare 1988 for meta-ethnography, Lockwood et al. 2015 for meta-aggregation (doi:10.1097/XEB.0000000000000062), Flemming et al. 2018 for Cochrane qualitative reporting (doi:10.1016/j.jclinepi.2017.10.022). Full citations: `shared/method_sources.md`.

## Gate (ENTREQ, 21 Items)

Walk the 21 ENTREQ items in `shared/reporting_standards.md`; flag every missing item. Every developed theme must trace to the included studies' findings or quotes.

## Guardrails

- Analytical themes must be *grounded* in the included studies' data: do not import your own theory and dress it up as findings.
- Name the synthesis method explicitly; thematic synthesis and meta-ethnography are different and not interchangeable.
- Do not convert qualitative findings into counts or claim statistical generality.
