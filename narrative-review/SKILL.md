---
name: narrative-review
description: "Write a narrative (traditional) literature review: a broad, expert synthesis of a field without a rigid protocol. Use when the author wants an overview of what is known on a topic, the state of the art, or a synthesis for a thesis chapter, and does not require a reproducible PRISMA protocol. Trigger terms: narrative review, literature review, state of the art, tinjauan naratif, tinjauan pustaka, kajian literatur, kajian pustaka, literature synthesis."
metadata:
  version: "0.1.0"
  genre: narrative-review
  reporting_standard: "SANRA"
---

# Narrative Review

You write a **broad, expert synthesis** of a field. Unlike a systematic review, there is no pre-registered protocol and no mandatory dual screening, but the review must still be transparent about how literature was chosen, which is what SANRA enforces.

## Scope

- **In scope:** an overview/synthesis of what is known on a topic; a background or literature-review chapter of a thesis; a state-of-the-art survey.
- **Out of scope:** reproducible comprehensive synthesis (→ `systematic-review`), statistical pooling (→ `meta-analysis`), arguing a novel conceptual thesis (→ `critical-review`), a single book (→ `book-review`).

## What You Need Before Writing

1. The topic and its scope/boundaries.
2. The purpose: inform, frame a gap, or survey the state of the art.
3. Roughly how the literature was/will be gathered (databases, key terms, snowballing).

## Method

1. **Justify the review** (SANRA 1). State why this topic needs a review now.
2. **State the aims** (SANRA 2). One explicit sentence on what the review covers and excludes.
3. **Describe the search transparently** (SANRA 3). Even without a full protocol, name the databases searched, the key terms, and any inclusion limits. "We searched Scopus and PubMed for X, Y, Z" is enough to be honest; "the literature shows…" with no source is not.
4. **Synthesize thematically, not chronologically.** Group studies by theme/finding, not by year. Do not write an annotated bibliography disguised as prose.
5. **Argue from evidence** (SANRA 5). Every claim is backed by cited studies; distinguish established findings from contested ones.
6. **Close with gaps and a future-research agenda.**

## Structure

```
1. Introduction: why this review, its aims and scope
2. Thematic synthesis: 3–5 themes, each synthesizing multiple studies
3. Contradictions and gaps: where the evidence disagrees or is thin
4. Conclusion: what is established, what is open, where the field goes next
```

## Decision Points (JEV)

Every decision here follows the JEV protocol (`../shared/jev.md`): ranked options, **#1 recommended**, one line of evidence each, what would change the ranking, and the author approves. Approved choices go into `decisions.md`.

- **Organization:** recommend **thematic synthesis (#1)** over chronological; chronological only if the field's history is itself the point.
- **Tables/figures:** recommend adding one when it would compress many studies (#1), otherwise skip.
- **Rigour:** recommend a transparent search and selection description (#1), checked against SANRA, even though no protocol is required.

## Standards & Sources

Governing standard: **SANRA** (Baethge et al., 2019, doi:10.1186/s41073-019-0064-8). Context: Greenhalgh et al. 2018 on why narrative reviews are not a lesser systematic review (doi:10.1111/eci.12931). Full citations and the Q1-readiness checklist: `shared/method_sources.md`.

## SANRA Gate (6 Items: See `shared/reporting_standards.md`)

- [ ] Justification of the review's importance
- [ ] Concrete statement of aims
- [ ] Description of the literature search (sources, terms, limits)
- [ ] Referencing: key statements carry citations
- [ ] Scientific reasoning: conclusions follow from the cited evidence
- [ ] Appropriate presentation of data (tables/figures where they help)

## Guardrails

- Do not claim "comprehensive" or "systematic" for a narrative review: that mislabels the method.
- Keep a running bibliography of everything cited; a narrative review lives or dies by its sources.
- The author remains responsible for every characterization of the literature; flag any claim you cannot trace to a source.
