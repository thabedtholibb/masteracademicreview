---
name: mapping-review
description: "Build an evidence and gap map (EGM) — code studies into a predefined framework and visualize where evidence is dense and where it is missing. Reported per ROSES. Use when the deliverable is a structured visual map/matrix of the evidence landscape. Trigger terms: evidence and gap map, EGM, mapping review, evidence map, framework map, ROSES, peta bukti."
metadata:
  version: "0.1.0"
  genre: mapping-review
  reporting_standard: "ROSES / EGM conventions"
---

# Mapping Review (Evidence & Gap Map)

You produce a **structured visual map** of the evidence — coding studies into a framework (e.g. rows = interventions/populations, columns = outcomes) and showing where evidence is dense or absent. It is the more visual, framework-driven sibling of the scoping review.

## Scope

- **In scope:** a broad evidence landscape that benefits from a framework matrix; gap-finding for funders/agencies.
- **Out of scope:** answering a focused question (→ `systematic-review`), quality appraisal (→ `systematic-review`), broad mapping without a framework (→ `scoping-review`).

## Pre-requisites

1. A **framework** (or the willingness to build one) — e.g. intervention × outcome, or PICO-derived.
2. A searchable body of studies.

## Method (recommendation-first)

1. **Define the framework (recommendation-first)** — propose a framework matrix (#1) based on the topic and show a small example before coding; the author approves it.
2. **Search & screen** — follow `shared/search_strategy.md` and `shared/screening.md`; document counts for the flow diagram (`shared/scripts/prisma_flow.py`).
3. **Code studies into the matrix** — place each study in its framework cell(s); this is the core mapping act.
4. **Visualize** — render the map (a matrix/heatmap) showing cell densities and gaps. No quality appraisal — mapping shows *where*, not *how good*.
5. **Report** — ROSES; present the map and the gap narrative.

## Structure (ROSES-aligned)

```
Title
Abstract
1. Introduction — rationale + the framework
2. Methods — framework, search, screening, coding
3. Results — the map, densities, gaps
4. Discussion — what the gaps mean, implications
```

## Gate

- [ ] A framework matrix is defined and applied consistently.
- [ ] The map (visual) is produced and the gaps are stated.
- [ ] Flow counts are reported (ROSES).

## Guardrails

- The map is only as good as the framework. Propose it, get approval, then code — don't code into a vague grid.
- A gap is "no evidence in this cell", not "no strong evidence" — keep those distinct.
