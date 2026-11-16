# Skill-by-skill flows

How each masteracademicreview skill runs, end to end. Sixteen skills: three at the entry (`brainstorm`, `journal-match`, `review-router`) and thirteen review genres.

Every run ends with **`review.md` + artifacts** (and optional `review.docx`/`review.pdf`); see `shared/output_spec.md`.

---

## The journey (three phases)

```
PHASE A — brainstorm          PHASE B — review-router         PHASE C — genre skill
vague idea ──► question +      framed request ──► ranked       chosen genre ──► protocol
               keywords (ranked)                shortlist        → review document + artifacts
```

- **Phase A** runs only when the author lacks a research question or keywords.
- **Phase B** always runs (unless the author jumps straight to a genre).
- **Phase C** is the genre-specific protocol, which pulls methodology from `shared/*.md` and runs `shared/scripts/*.py` where it matters.

---

## Cheat sheet

| Skill | Use when | You provide | Output |
|---|---|---|---|
| `brainstorm` | vague idea, no question/keywords | raw topic | research question + keyword table + Boolean query |
| `journal-match` | choosing where to submit | topic/manuscript + constraints | ranked journal shortlist + submission cascade |
| `review-router` | unsure which review type | the request | ranked genre shortlist + brief |
| `book-review` | reviewing a single book | book + its thesis + venue | book review (summary → critique → verdict) |
| `narrative-review` | broad expert synthesis | topic + scope | narrative review (SANRA) |
| `critical-review` | arguing a thesis | thesis + literature | critical review (argument) |
| `systematic-review` | reproducible synthesis | PICO + protocol | PRISMA review + `prisma_flow.svg` |
| `meta-analysis` | statistically pool results | effect-size data | pooled estimate + forest/funnel + report |
| `scoping-review` | map breadth, no appraisal | PCC + broad question | scoping review + evidence map |
| `umbrella-review` | synthesize existing reviews | the reviews | umbrella review + AMSTAR-2 + CCA |
| `meta-synthesis` | synthesize qualitative studies | qualitative findings | meta-synthesis + themes (ENTREQ) |
| `rapid-review` | fast, declared shortcuts | question + deadline | rapid review + shortcuts |
| `integrative-review` | combine diverse designs | multi-design literature | integrative review + framework |
| `mapping-review` | visual evidence & gap map | framework + studies | EGM + matrix + gaps |
| `bibliometric-review` | quantitative map of a field | Scopus CSV export | bibliometric review + plots |
| `realist-review` | explain what works for whom, why | programme theory | realist review + CMO configurations |

---

## `brainstorm` (Phase A)

- **Use when:** the author has a rough idea but no focused research question or search keywords.
- **You provide:** the raw topic (population, intervention/phenomenon, outcome, context as available).
- **Flow (recommendation-first):**
  1. Elicit the raw idea — minimally.
  2. Propose the framing, ranked — **PICO (#1)** for effectiveness, **PICo/SPIDER** for qualitative, **PCC** for mapping.
  3. Draft 2–3 candidate research questions, **#1 recommended**, author picks or edits.
  4. Build a keyword table, terms ranked best-first per concept, top pick marked.
  5. Assemble the Boolean query (`OR` within concept, `AND` across).
  6. Hand off with a ranked genre hint to `review-router`.
  7. If the author wants to publish, offer `journal-match` with the brief.
- **Output:** research question + framing + keyword table + Boolean query (+ optional journal shortlist).

## `journal-match` (Phase A, optional)

- **Use when:** the author asks where to submit, which journal fits, or wants a Q1/Q2 shortlist — before writing (recommended) or after drafting.
- **You provide:** topic/title + abstract (or key claims), genre, and hard constraints (indexing, quartile, APC budget, deadline, OA).
- **Flow:**
  1. Collect inputs; mark scope fit provisional if there is no abstract yet.
  2. Build 8–15 candidates from the review corpus, reference list, subject lists, and finder tools (leads only).
  3. Screen against hard constraints, recording every exclusion reason.
  4. Score eight criteria 0–5 and run `shared/scripts/journal_rank.py`.
  5. Assign reach / target / safety tiers and a submission cascade (**#1 = target**).
  6. Write `journal_shortlist.md` with an evidence table (source + check date) and cover-letter angles.
- **Decision points:** run before writing (**#1**) vs after; target journal (**#1**) vs reach/safety.
- **Output:** ranked shortlist + evidence table + cascade; **gate: every metric verified or marked `unverified`, author approves the target**.

## `review-router` (Phase B)

- **Use when:** the author wants "a review" and doesn't know which type (or asks for one explicitly).
- **You provide:** the (framed) request.
- **Flow:**
  1. Recognize it as a review request (or decline if it's a new-paper/experiment/grant task).
  2. Interview along four axes — object, purpose, rigor, data.
  3. Classify into a **ranked shortlist** (top 2–3, **#1 recommended**, each with a reason).
  4. Dispatch #1 with a brief; the author can override.
- **Output:** ranked genre shortlist + brief + handoff to the genre skill (and an optional `journal-match` handoff).

---

## `book-review`

- **Use when:** the object is a single book/monograph.
- **You provide:** bibliographic facts, the book's thesis, the venue/audience.
- **Flow:** situate the book → reconstruct the argument fairly → evaluate on its own terms → give a verdict.
- **Decision points:** audience & length (scholarly **#1** vs resensi/newspaper); verdict (honest mixed verdict allowed).
- **Output:** book review (heading, overview, summary, critique, verdict + audience).

## `narrative-review`

- **Use when:** broad expert synthesis; no reproducible protocol needed.
- **You provide:** topic + scope + rough search terms.
- **Flow:** justify the review → state aims → describe the search transparently → synthesize thematically → argue from evidence → close with gaps.
- **Decision points:** thematic organization (**#1**) over chronological; add a table/figure if it compresses studies.
- **Output:** narrative review (intro, thematic synthesis, contradictions/gaps, conclusion); **gate: SANRA (6 items)**.

## `critical-review`

- **Use when:** the purpose is to argue a conceptual thesis.
- **You provide:** a thesis (or the author sharpens one) + the literature to engage.
- **Flow:** fix the thesis → map the field as *positions* → build the argument (consensus → assumption → counter-evidence → alternative) → address the strongest objection → state the contribution.
- **Decision points:** sharpen the author's thesis (**#1**) over substituting your own.
- **Output:** critical review (thesis, debate, critique, alternative, implications).

---

## `systematic-review`

- **Use when:** reproducible, comprehensive synthesis of a focused question (PRISMA).
- **You provide:** PICO question + protocol (ideally PROSPERO-registered) + database access.
- **Flow:** frame + protocol → search (`shared/search_strategy.md`) → screen (dual, `shared/screening.md`) → extract (`shared/data_extraction.md`) → risk of bias (`shared/risk_of_bias.md`) → narrative synthesis → PRISMA report + flow diagram (`shared/scripts/prisma_flow.py`).
- **Decision points:** risk-of-bias tool by design (**#1** = design-matched); if pooling is wanted → `meta-analysis`.
- **Output:** PRISMA review + `prisma_flow.svg` + screening log + characteristics table; **gate: PRISMA 2020 (27 items)**.

## `meta-analysis`

- **Use when:** ≥2 studies with extractable effect sizes; the author wants a pooled estimate.
- **You provide:** effect-size data (means/SD per arm, 2×2 tables, or correlations).
- **Flow:** run the full `systematic-review` protocol → convert to a common effect size (`effect_sizes.py`) → pool (`pooling.py`, random effects) → assess heterogeneity (I², Q) → forest/funnel + Egger (`plots.py`) → GRADE certainty → PRISMA + MOOSE report.
- **Decision points:** effect-size measure (**Hedges' g / log OR / Fisher z (#1)** by data type); model (**random effects #1**).
- **Output:** pooled estimate + 95% CI, I²/Q/tau², `forest.png`, `funnel.png`, `effects.csv`, report; **gate: PRISMA + MOOSE**.

## `scoping-review`

- **Use when:** mapping the breadth of evidence; no quality appraisal.
- **You provide:** a broad question (PCC frame) + protocol.
- **Flow:** frame PCC → broad search → screen → chart data into a matrix → map + gaps → PRISMA-ScR report + flow diagram.
- **Decision points:** framing **PCC (#1)**; skip quality appraisal (**#1**).
- **Output:** scoping review + evidence map + `prisma_flow.svg`; **gate: PRISMA-ScR (22 items)**.

## `umbrella-review`

- **Use when:** the unit of analysis is existing reviews/meta-analyses.
- **You provide:** the eligible systematic reviews.
- **Flow:** search for reviews → screen → appraise with AMSTAR-2 → measure overlap (CCA) → synthesize per outcome (GRADE) → PRIOR report.
- **Decision points:** **AMSTAR-2 (#1)** for quality; report **CCA (#1)** for overlap.
- **Output:** umbrella review + AMSTAR-2 ratings + CCA table; **gate: PRIOR**.

## `meta-synthesis`

- **Use when:** synthesizing qualitative studies into themes or theory.
- **You provide:** qualitative studies with extractable findings (themes, quotes).
- **Flow:** frame (PICo/SPIDER) → search & screen → appraise (CASP) → extract findings → synthesize → ENTREQ report.
- **Decision points:** synthesis method — **thematic synthesis (#1)**, meta-ethnography (#2), meta-aggregation (#3).
- **Output:** meta-synthesis + developed themes + quote table; **gate: ENTREQ (21 items)**.

## `rapid-review`

- **Use when:** a deadline demands a fast, declared-shortcut synthesis.
- **You provide:** a focused question + a deadline.
- **Flow:** choose shortcut tier (ranked #1/#2/#3) → search (fewer sources) → screen (single + verification sample) → narrative summary → adapted PRISMA with a mandatory "shortcuts taken" subsection.
- **Decision points:** shortcut tier (**#1** = 2 databases + verification sample).
- **Output:** rapid review + declared shortcuts; **gate: Cochrane rapid-review guidance**.

## `integrative-review`

- **Use when:** combining quantitative, qualitative, and theoretical literature.
- **You provide:** literature spanning multiple designs.
- **Flow (Whittemore & Knafl):** problem → multi-database search → design-matched appraisal → constant-comparison analysis → integrated presentation.
- **Decision points:** analysis = **constant comparison (#1)**.
- **Output:** integrative review + integrated themes/framework.

## `mapping-review`

- **Use when:** the deliverable is a visual evidence & gap map (EGM).
- **You provide:** a framework (or willingness to build one) + studies.
- **Flow:** propose the framework matrix (#1) → search & screen → code studies into the matrix → visualize densities/gaps → ROSES report.
- **Decision points:** propose the framework (**#1**) and get approval before coding.
- **Output:** EGM + matrix/heatmap + gap narrative; **gate: ROSES**.

## `bibliometric-review`

- **Use when:** a quantitative map of a field (authors, sources, themes, trends).
- **You provide:** a **Scopus CSV export** (with `Document Type`).
- **Flow:** Scopus-only search (documented) → choose analysis (science mapping **#1** vs performance vs both) → filter to Article/Review (`filter_document_type`) → run the engine (`shared/scripts/bibliometric/`) → interpret + PRISMA report.
- **Decision points:** Scopus (**#1**) as sole source; keep **Article + Review (#1)**; science mapping + performance (**both #3**) for a full review.
- **Output:** bibliometric review + trend/top/co-occurrence plots; **gate: PRISMA (search) + Scopus-only documented + filter applied**.

## `realist-review`

- **Use when:** explaining "what works, for whom, under what circumstances, and why".
- **You provide:** a programme theory (draft) + the explanatory question.
- **Flow:** state the programme theory → iterative theory-driven search → appraise by relevance & rigour → extract Context–Mechanism–Outcome → synthesize refined CMOs → RAMESES report.
- **Decision points:** purposive, theory-driven search (**#1**) over exhaustive recall.
- **Output:** realist review + CMO configurations + middle-range theory; **gate: RAMESES**.

---

## Invoking any skill

- **Auto:** describe what you want; the matching skill loads.
- **`@skill-id` (OpenCode):** `@meta-analysis`, `@brainstorm`, …
- **`/command` (Claude Code):** `/review`, `/meta-analysis`, `/brainstorm`, …
