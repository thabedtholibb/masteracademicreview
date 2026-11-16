---
name: realist-review
description: "Conduct a realist review: explain what works, for whom, under what circumstances, by building Context–Mechanism–Outcome (CMO) configurations from diverse evidence. Reported per RAMESES. Use when the question is explanatory and context-dependent ('why/how does X work here but not there'). Trigger terms: realist review, realist synthesis, CMO, context mechanism outcome, programme theory, RAMESES."
metadata:
  version: "0.1.0"
  genre: realist-review
  reporting_standard: "RAMESES"
---

# Realist Review

You explain **how and why** an intervention works (or not) in context, by building **Context–Mechanism–Outcome (CMO)** configurations. It is theory-driven and iterative, and it embraces heterogeneous evidence rather than averaging it away.

## Scope

- **In scope:** explanatory, context-dependent questions ("what works, for whom, under what circumstances"); complex interventions.
- **Out of scope:** "does it work on average" (→ `meta-analysis`), mapping breadth (→ `scoping-review` / `mapping-review`), fixed-protocol synthesis (→ `systematic-review`).

## Pre-Requisites

1. A question of the form "what works, for whom, in what circumstances, and why".
2. An initial **programme theory** (draft) of candidate mechanisms to refine.

## Method (JEV)

1. **State the programme theory (draft):** lay out candidate CMOs as hypotheses to test against evidence.
2. **Search iteratively (JEV):** recommend a purposive, theory-driven search (#1) over exhaustive recall; search, then let findings redirect the next search (snowballing, grey literature).
3. **Appraise by relevance & rigour:** realist reviews judge sources by whether they can *test a mechanism* (relevance) and their trustworthiness (rigour), not a standard RoB tool.
4. **Extract CMOs:** pull context, mechanism, and outcome from each source; refine the programme theory as patterns emerge.
5. **Synthesize:** build refined CMO configurations that explain the outcome pattern; state the middle-range theory.
6. **Report:** RAMESES.

## Structure (RAMESES-aligned)

```
Title
Abstract
1. Introduction: the question + initial programme theory
2. Methods: iterative search, relevance & rigour appraisal, CMO extraction
3. Findings: refined CMO configurations (what works for whom, why)
4. Discussion: the middle-range theory, limitations, implications
```

## Decision Points (JEV)

Every decision here follows the JEV protocol (`../shared/jev.md`): ranked options, **#1 recommended**, one line of evidence each, what would change the ranking, and the author approves. Approved choices go into `decisions.md`.

- **Initial programme theory.** **#1 recommended:** built from the literature and stakeholder input before the main search. #2: from the literature only (say so).
- **Appraisal.** **#1 recommended:** relevance and rigour per source (RAMESES), not a design hierarchy.
- **Output.** **#1 recommended:** refined CMO configurations, each tied to its sources. #2: a narrative middle-range theory, only where CMOs cannot be supported.

## Standards & Sources

Governing standard: **RAMESES** (Wong et al., 2013, doi:10.1186/1741-7015-11-21). Method source: Pawson et al. 2005, the original realist-review method (doi:10.1258/1355819054308530). Full citations and the Q1-readiness checklist: `shared/method_sources.md`.

## Gate

- [ ] CMO configurations are explicit (context, mechanism, outcome separated).
- [ ] The programme theory evolved in response to evidence.
- [ ] Relevance & rigour appraisal is described (not a standard RoB score).

## Guardrails

- Do not average heterogeneous outcomes: the heterogeneity *is* the finding.
- A mechanism is a causal explanation, not a description of the intervention; keep them distinct.
