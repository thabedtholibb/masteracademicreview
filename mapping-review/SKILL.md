---
name: mapping-review
description: "Build an evidence and gap map (EGM): code studies into a predefined framework and visualize where evidence is dense and where it is missing. Reported per ROSES. Use when the deliverable is a structured visual map/matrix of the evidence landscape. Trigger terms: evidence and gap map, EGM, mapping review, evidence map, framework map, ROSES, peta bukti."
metadata:
  version: "0.1.0"
  genre: mapping-review
  reporting_standard: "ROSES / EGM conventions"
---

# Mapping Review (Evidence & Gap Map)

You produce a **structured visual map** of the evidence: coding studies into a framework (e.g. rows = interventions/populations, columns = outcomes) and showing where evidence is dense or absent. It is the more visual, framework-driven sibling of the scoping review.

## Scope

- **In scope:** a broad evidence landscape that benefits from a framework matrix; gap-finding for funders/agencies.
- **Out of scope:** answering a focused question (→ `systematic-review`), quality appraisal (→ `systematic-review`), broad mapping without a framework (→ `scoping-review`).

## Pre-Requisites

1. A **framework** (or the willingness to build one): e.g. intervention × outcome, or PICO-derived.
2. A searchable body of studies.

## Method (JEV)

1. **Define the framework (JEV):** propose a framework matrix (#1) based on the topic and show a small example before coding; the author approves it.
2. **Search & screen:** follow `shared/search_strategy.md` and `shared/screening.md`; document counts for the flow diagram (`shared/scripts/prisma_flow.py`). Deduplicate the database exports with `mar dedup --source <Name>=<file> ...`: certain duplicates are removed, near-matches are listed for you to decide (JEV), and the PRISMA identification counts are written for you.
3. **Code studies into the matrix:** place each study in its framework cell(s); this is the core mapping act.
4. **Visualize:** render the map (a matrix/heatmap) showing cell densities and gaps. No quality appraisal: mapping shows *where*, not *how good*.
5. **Report:** ROSES; present the map and the gap narrative.

## Structure (ROSES-aligned)

```
Title
Abstract
1. Introduction: rationale + the framework
2. Methods: framework, search, screening, coding
3. Results: the map, densities, gaps
4. Discussion: what the gaps mean, implications
References
```

## Decision Points (JEV)

Every decision here follows the JEV protocol (`../shared/jev.md`): ranked options, **#1 recommended**, one line of evidence each, what would change the ranking, and the author approves. Approved choices go into `decisions.md`.

- **Framework.** **#1 recommended:** a pre-specified, piloted coding framework approved by the author (see Method). #2: adapt an established framework from the field.
- **Output.** **#1 recommended:** an evidence-and-gap map (matrix with counts per cell); no claims about effects.
- **Reporting.** **#1 recommended:** ROSES, with the flow diagram from `prisma_flow.py`.

## Standards & Sources

Governing standard: **ROSES** (Haddaway et al., 2018, doi:10.1186/s13750-018-0121-7). Method sources: Saran & White 2018 on evidence and gap map approaches (doi:10.4073/cmdp.2018.2). Full citations and the Q1-readiness checklist: `shared/method_sources.md`.

## Gate

- [ ] A framework matrix is defined and applied consistently.
- [ ] The map (visual) is produced and the gaps are stated.
- [ ] Flow counts are reported (ROSES).

**Automated Gate:** run these before you call the review done. Both are offline; `pip install masteracademicreview` provides `mar`.

- [ ] `mar check-review review.md` reports **0 errors**: header fields, the sections this genre needs, citations matched to references, referenced and required artifacts present, no placeholders, and a gate line that matches the checklist. It ranks what to fix first.
- [ ] `mar verify-refs review.md` finds no unresolved citation or duplicate DOI; add `--online` before submission to check every reference against Crossref.

## Guardrails

- The map is only as good as the framework. Propose it, get approval, then code: don't code into a vague grid.
- A gap is "no evidence in this cell", not "no strong evidence": keep those distinct.
