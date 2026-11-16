# How to Use masteracademicreview

For the step-by-step flow of **each** of the 15 skills, see [FLOWS.md](FLOWS.md).

## The short answer: it is *not* a full-paper pipeline

masteracademicreview does **not** turn one sentence into a complete research paper the way Spark-to-Paper or AI-Scientist do. It does **not** design or run experiments, and it does **not** generate new results.

masteracademicreview produces **one kind of deliverable: a review document**, plus the auditable artifacts that back it (search counts, a PRISMA flow diagram, pooled estimates, forest/funnel plots). It is a *specialist for the review genre*, working interactively with you as the author.

| | Full-paper pipeline (Spark / AI-Scientist) | masteracademicreview |
|---|---|---|
| Starts from | an idea or dataset | a review request |
| Produces | a full research paper, with experiments | a **review document** |
| Runs experiments? | yes | no |
| Generates new findings? | yes | no — it synthesizes existing work |
| Interaction | mostly one-shot | interactive, stops for your decisions |
| Domain | papers | **reviews** (book, narrative, critical, systematic, meta-analysis) |

## The working model

```
 vague idea
   ▼
 brainstorm ──► research question + keywords   (skip if you already have both)
   ▼
 review-router ──► interviews you ──► classifies the genre
   ▼
 genre skill (thirteen genres: book, narrative, critical, systematic,
              meta-analysis, scoping, umbrella, meta-synthesis, rapid,
              integrative, mapping, bibliometric, realist)
   │   pulls methodology from shared/*.md
   │   runs shared/scripts/*.py (systematic, scoping, meta)
   ▼
 review document  +  artifacts (SVG / PNG / CSV / pooled numbers)
```

**How you start (pick one):**
- **Auto** — describe what you want (*"Saya mau meta-analysis dari data ini"*); the matching skill loads itself.
- **`@skill-id` (OpenCode)** — `@brainstorm`, `@meta-analysis`, `@book-review`, etc.
- **`/command` (Claude Code)** — `/brainstorm`, `/review`, `/meta-analysis`, etc. (after copying `commands/` — see INSTALL.md).

1. If your topic is vague, `brainstorm` sharpens the research question and builds keywords first.
2. `review-router` interviews you along four axes — **object, purpose, rigor, data** — and classifies the genre (or you jump straight to a genre).
3. The genre skill runs its protocol, pulling methodology from `shared/` and, for the protocol-driven genres, running the Python scripts.
4. You make the decisions (inclusion/exclusion, protocol, thesis); the tool does the grunt work and the arithmetic.
5. You receive a review document and its artifacts.

**Output format:** the review is a **`review.md`** Markdown document plus artifacts; run `python shared/scripts/export.py review.md` to also produce `review.docx` (Word) and `review.pdf`. The full convention is in `shared/output_spec.md`.

## Deliverables by genre

| Genre | Main output | Artifacts |
|---|---|---|
| `book-review` | book review / resensi (Markdown) | — |
| `narrative-review` | narrative review (Markdown) | running bibliography |
| `critical-review` | critical review (Markdown) | — |
| `systematic-review` | systematic review (Markdown, PRISMA-structured) | `prisma_flow.svg`, screening log, characteristics table |
| `meta-analysis` | meta-analysis (Markdown, PRISMA + MOOSE) | `forest.png`, `funnel.png`, `effects.csv`, pooled estimate + I²/Q/Egger |
| `scoping-review` | scoping review (Markdown, PRISMA-ScR) | `prisma_flow.svg`, evidence map/matrix |
| `umbrella-review` | umbrella review (Markdown, PRIOR) | AMSTAR-2 ratings, CCA overlap table |
| `meta-synthesis` | meta-synthesis (Markdown, ENTREQ) | developed themes, quote table |
| `rapid-review` | rapid review (Markdown, adapted PRISMA) | declared shortcuts, narrative summary |
| `integrative-review` | integrative review (Markdown) | integrated themes/framework |
| `mapping-review` | evidence & gap map (Markdown + matrix) | framework matrix/heatmap, gaps |
| `bibliometric-review` | bibliometric review (Markdown) | networks/clusters, performance stats |
| `realist-review` | realist review (Markdown, RAMESES) | CMO configurations |

## Example 1 — systematic review

> **You:** "Bantu saya systematic review tentang efektivitas terapi X pada kondisi Y."
> **Router:** classifies `systematic-review`; asks for your PICO question and whether you have a protocol (e.g. PROSPERO).
> **You:** provide the PICO and protocol.
> **Skill:** walks search → screening → extraction → risk-of-bias → PRISMA report; generates `prisma_flow.svg` from your screening counts.
> **You get:** a PRISMA-structured review + the flow diagram.

## Example 2 — meta-analysis

> **You:** "Saya punya effect size dari 5 studi, mau meta-analysis."
> **Skill:**
> - converts each study to Hedges' g via `effect_sizes.py`;
> - pools with random effects via `pooling.py` → I², Q, tau², pooled estimate + 95% CI;
> - draws forest and funnel plots and runs Egger's test via `plots.py`.
> **You get:** the pooled estimate, heterogeneity, plots, and a PRISMA/MOOSE write-up.

## Example 3 — book review

> **You:** "Resensi buku ini."
> **Skill:** asks for the book's thesis, then produces summary → critique → verdict.

## Running the Python scripts

From the repo root:

```bash
python shared/scripts/meta/example.py    # end-to-end demo of the meta engine
python shared/scripts/meta/pooling.py    # demo of fixed/random effects + I²/Q
python shared/scripts/prisma_flow.py     # demo PRISMA flow → prisma_flow.svg
```

In real work, the skill guides you to (a) prepare the inputs — a screening-counts dict for `prisma_flow.py`, or an `effects.csv` for the meta engine — then (b) run the relevant functions. Scripts live under `shared/scripts/` and are referenced from skills as `../shared/scripts/…`.

## The one rule that never changes

masteracademicreview **never fabricates** study counts, effect sizes, or outcomes. Numbers come from your data or the literature; the code only computes. If a number cannot be produced by the code from real inputs, it does not go in the document. You remain the author and answer for every claim.
