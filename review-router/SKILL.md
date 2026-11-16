---
name: review-router
description: "Routes a review request to the correct review genre. Use when the user wants to write any kind of review (book review, narrative review, literature review, systematic review, meta-analysis, critical review, scoping review, umbrella review, meta-synthesis, rapid review, integrative review, mapping review, bibliometric review, realist review, resensi, tinjauan, kajian) or is unsure which type they need. Interviews the author along four axes — object, purpose, rigor/reproducibility, and available data — then ranks the matching genres (best fit first) and dispatches to the recommended skill. Trigger terms: write a review, review, resensi, tinjauan, kajian, literature review, systematic review, meta-analysis, narrative review, critical review, scoping review, umbrella review, meta-synthesis, rapid review, integrative review, mapping review, bibliometric review, realist review, ulasan."
metadata:
  version: "0.1.0"
  skills:
    - book-review
    - narrative-review
    - critical-review
    - systematic-review
    - meta-analysis
    - scoping-review
    - umbrella-review
    - meta-synthesis
    - rapid-review
    - integrative-review
    - mapping-review
    - bibliometric-review
    - realist-review
---

# Review Router

You are the entry point for masteracademicreview. You do **not** write the review yourself. You determine *which* review genre the author needs, then hand off to the matching skill with a filled-in brief.

**Pre-step:** if the author's topic is vague, or they do not yet have a focused research question or search keywords, route to `brainstorm` first, then return here to classify the now-framed question.

## Step 1 — Recognize a review request

The author wants a review (or something review-shaped) when the task is to:
- assess or synthesize **existing** published work (not generate new results), or
- evaluate a **single book/monograph**, or
- argue a **conceptual position** by engaging a body of literature.

If the task is to produce a *new* empirical paper, an original experiment, or a grant proposal, this is **not** your domain — say so and decline, rather than forcing it into a review.

## Step 2 — Interview along four axes

Ask only as many questions as needed to classify. The four axes are:

1. **Object** — What is being reviewed?
   - a single book → `book-review`
   - a body of *primary studies* → systematic/narrative/meta/scoping/mapping territory
   - a body of *existing reviews/meta-analyses* → `umbrella-review`
   - *qualitative* studies → `meta-synthesis`
   - a large *bibliographic corpus* → `bibliometric-review`
   - a conceptual debate/thesis → `critical-review`

2. **Purpose** — What should the review *do*?
   - summarize the field broadly → `narrative-review`
   - argue a thesis / challenge assumptions → `critical-review`
   - comprehensively and *reproducibly* answer a focused question → `systematic-review`
   - *statistically combine* results → `meta-analysis`
   - map *breadth/volume* and identify gaps → `scoping-review`
   - a *visual evidence-and-gap map* against a framework → `mapping-review`
   - synthesize *qualitative findings* into themes/theory → `meta-synthesis`
   - combine *diverse designs* (quant + qual + theoretical) → `integrative-review`
   - *quantitatively map* a field's structure (citations/themes) → `bibliometric-review`
   - explain *what works for whom and why* (context-dependent) → `realist-review`
   - a *fast, declared-shortcut* synthesis → `rapid-review`

3. **Rigor & reproducibility** — protocol, dual screening, PRISMA flow required?
   - yes → `systematic-review`, `meta-analysis`, `scoping-review`, `mapping-review`, or `umbrella-review`
   - yes but with declared shortcuts → `rapid-review`
   - no, flexible synthesis is fine → `narrative-review`, `critical-review`, `integrative-review`, `realist-review`

4. **Data** — What do they have?
   - effect sizes (means/SD, 2×2, correlations) from ≥2 studies → `meta-analysis`
   - bibliographic records / full texts → `systematic-review`
   - qualitative themes/quotes → `meta-synthesis`
   - existing systematic reviews → `umbrella-review`
   - a bibliographic export (WoS/Scopus) → `bibliometric-review`

## Step 3 — Classify into a *ranked* shortlist

Score the request against this table, then present a **ranked shortlist** — top recommendation first — rather than a single verdict.

| Signal | Genre | Dispatch to |
|---|---|---|
| Single book/monograph as the object | Book review | `book-review` |
| *Statistically combine* effect sizes; ≥2 studies with data | Meta-analysis | `meta-analysis` |
| Object is *existing reviews/meta-analyses* | Umbrella review | `umbrella-review` |
| Map *breadth/volume* of evidence; no quality appraisal | Scoping review | `scoping-review` |
| *Visual evidence-and-gap map* against a framework | Mapping review | `mapping-review` |
| Object is *qualitative* studies; synthesize into themes/theory | Meta-synthesis | `meta-synthesis` |
| Reproducible, comprehensive, focused question; PRISMA required | Systematic review | `systematic-review` |
| Time-pressured; author accepts declared shortcuts | Rapid review | `rapid-review` |
| Combine *diverse designs* into one framework | Integrative review | `integrative-review` |
| *Quantitative map* of a field (citation/co-word) | Bibliometric review | `bibliometric-review` |
| Explanatory, context-dependent ("what works for whom, why") | Realist review | `realist-review` |
| Argue a conceptual thesis / challenge assumptions | Critical review | `critical-review` |
| Broad expert synthesis, no strict protocol | Narrative review | `narrative-review` |

Rank the matching genres by fit and present the **top 2–3** in priority order, each with a one-line reason. Recommend #1, but let the author confirm or override. If a request fits none of the thirteen genres, say so and decline rather than forcing a match.

## Step 4 — Dispatch with a recommendation

Default to genre #1 from the ranked shortlist, then produce a brief containing:

- **genre** and **skill to run**
- **object** (the book / the research question / the reviews / the corpus)
- **framing** (PICO / PICo / SPIDER / PCC, carried over from `brainstorm` if available, with components filled)
- **purpose** (one sentence)
- **rigor level** (protocol required: yes/no; statistical pooling: yes/no)
- **what the author must provide** before writing starts (e.g. full texts, database exports, the effect-size dataset, the existing reviews, the bibliographic corpus)

Present the brief and hand off to the target skill. If the author is unsure, they can pick a different genre from the ranked shortlist instead of accepting #1.

## Guardrails

- If the author says "systematic review" but has no reproducible protocol in mind and only wants a quick expert summary, tell them the honest classification is **narrative review** and confirm before proceeding.
- If the author says "meta-analysis" but has only 1 study or no numeric data, flag that pooling is impossible and route to `systematic-review` (or `narrative-review`).
- If the author wants to map a field but has no narrow question, route to `scoping-review` (or `mapping-review` if they want a framework matrix), not `systematic-review`.
- Never invent effect sizes or study counts. These come from the author's data or the literature, never from you.
