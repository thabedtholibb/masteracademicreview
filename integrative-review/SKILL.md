---
name: integrative-review
description: "Conduct an integrative review — synthesize empirical and theoretical literature of diverse designs into a whole, using Whittemore & Knafl's five stages. Common in nursing and applied health. Use when the author must combine quantitative, qualitative, and theoretical sources into one framework. Trigger terms: integrative review, Whittemore and Knafl, mixed-method synthesis, tinjauan integratif."
metadata:
  version: "0.1.0"
  genre: integrative-review
  reporting_standard: "Whittemore & Knafl (2005); no EQUATOR checklist"
---

# Integrative Review

You synthesize **diverse source types** — empirical (quantitative + qualitative) and theoretical — into an integrated whole. The signature is breadth of design plus a synthesis that goes beyond summing the parts.

## Scope

- **In scope:** combining quantitative, qualitative, and theoretical literature on one topic; applied/health fields.
- **Out of scope:** single-design synthesis (→ `systematic-review` / `meta-analysis` / `meta-synthesis`), mapping only (→ `scoping-review` / `mapping-review`).

## Pre-requisites

1. A problem/topic that genuinely spans multiple study designs.
2. Literature from more than one methodological tradition.

## Method (Whittemore & Knafl, recommendation-first)

1. **Problem identification** — frame the topic clearly.
2. **Literature search** — follow `shared/search_strategy.md`; deliberately multi-database because the designs are diverse. Recommend the 2 best databases (#1/#2).
3. **Data evaluation** — appraise quality with the tool matching each study's design (see `shared/risk_of_bias.md`); recommend the design-matched tool (#1), not a one-size score.
4. **Data analysis (JEV)** — recommend **constant comparison (#1)** to categorize and integrate findings across designs; order, code, compare, and build themes that connect the evidence.
5. **Presentation** — present the integrated synthesis (often a model or table of themes) plus a note on limitations from source diversity.

## Structure

```
Title
Abstract
1. Introduction — the problem and why integration is needed
2. Methods — search, evaluation, analysis approach
3. Results — the integrated themes/framework
4. Discussion — meaning, limitations, implications
```

## Decision points (JEV)

Every decision here follows the JEV protocol (`../shared/jev.md`): ranked options, **#1 recommended**, one line of evidence each, what would change the ranking, and the author approves. Approved choices go into `decisions.md`.

- **Framework.** **#1 recommended:** Whittemore & Knafl's five stages. #2: Torraco's guidance when the sources are mostly conceptual.
- **Appraisal across designs.** **#1 recommended:** the design-matched tool per source, summarised in one table. #2: a mixed-methods appraisal approach (Pluye & Hong 2014) when most sources are empirical.
- **Presentation.** **#1 recommended:** a model or table of integrated themes, each linked to sources of every design that supports it.

## Standards & sources

Governing method: **Whittemore & Knafl's five stages** (Whittemore & Knafl, 2005, doi:10.1111/j.1365-2648.2005.03621.x). Method sources: Torraco 2005 (doi:10.1177/1534484305278283), Hopia et al. 2016 (doi:10.1111/scs.12327). No EQUATOR-registered checklist exists for integrative reviews; the gate below is the method contract. Full citations: `shared/method_sources.md`.

## Gate

- [ ] The synthesis integrates across designs — it does not just list study summaries.
- [ ] Quality appraisal is design-matched, not one-size-fits-all.
- [ ] The diversity of sources is reflected in the limitations.

## Guardrails

- Integration means a *new whole*, not a juxtaposition. If the result is a list, it is not an integrative review.
- Do not pool effect sizes (that is meta-analysis); you integrate findings.
