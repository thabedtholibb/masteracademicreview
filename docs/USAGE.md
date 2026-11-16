# How To Use Masteracademicreview

For the step-by-step flow of **each** of the 16 skills, see [FLOWS.md](FLOWS.md).

## The Short Answer: It Is *Not* A Full-Paper Pipeline

masteracademicreview does **not** turn one sentence into a complete research paper the way Spark-to-Paper or AI-Scientist do. It does **not** design or run experiments, and it does **not** generate new results.

masteracademicreview produces **one kind of deliverable: a review document**, plus the auditable artifacts that back it (search counts, a PRISMA flow diagram, pooled estimates, forest/funnel plots). It is a *specialist for the review genre*, working interactively with you as the author.

| | Full-Paper Pipeline (Spark / AI-Scientist) | Masteracademicreview |
|---|---|---|
| Starts from | an idea or dataset | a review request |
| Produces | a full research paper, with experiments | a **review document** |
| Runs experiments? | yes | no |
| Generates new findings? | yes | no: it synthesizes existing work |
| Interaction | mostly one-shot | interactive, stops for your decisions |
| Domain | papers | **reviews** (book, narrative, critical, systematic, meta-analysis) |

## The Working Model

```
 vague idea
   ▼
 brainstorm ──► research question + keywords   (skip if you already have both)
   │
   ├──► journal-match ──► verified target-journal shortlist (optional)
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
- **Auto:** describe what you want (*"Saya mau meta-analysis dari data ini"*); the matching skill loads itself.
- **`@skill-id` (OpenCode):** `@brainstorm`, `@meta-analysis`, `@book-review`, etc.
- **`/command` (Claude Code):** `/brainstorm`, `/review`, `/meta-analysis`, etc. (after copying `commands/`: see INSTALL.md).

1. If your topic is vague, `brainstorm` sharpens the research question and builds keywords first.
2. If you want to publish, `journal-match` turns the topic into a ranked, verified target-journal shortlist (optional; it can also run after drafting).
3. `review-router` interviews you along four axes (**object, purpose, rigor, data**) and classifies the genre (or you jump straight to a genre).
4. The genre skill runs its protocol, pulling methodology from `shared/` and, for the protocol-driven genres, running the Python scripts.
5. You make the decisions (inclusion/exclusion, protocol, thesis); the tool does the grunt work and the arithmetic.
6. You receive a review document and its artifacts.

**Output format:** the review is a **`review.md`** Markdown document plus artifacts; run `python shared/scripts/export.py review.md` to also produce `review.docx` (Word) and `review.pdf`. The full convention is in `shared/output_spec.md`.

## Deliverables By Genre

| Genre | Main Output | Artifacts |
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

## Example 1: Systematic Review

> **You:** "Bantu saya systematic review tentang efektivitas terapi X pada kondisi Y."
> **Router:** classifies `systematic-review`; asks for your PICO question and whether you have a protocol (e.g. PROSPERO).
> **You:** provide the PICO and protocol.
> **Skill:** walks search → screening → extraction → risk-of-bias → PRISMA report; generates `prisma_flow.svg` from your screening counts.
> **You get:** a PRISMA-structured review + the flow diagram.

## Example 2: Meta-Analysis

> **You:** "Saya punya effect size dari 5 studi, mau meta-analysis."
> **Skill:**
> - converts each study to Hedges' g via `effect_sizes.py`;
> - pools with random effects via `pooling.py` → I², Q, tau², pooled estimate + 95% CI;
> - draws forest and funnel plots and runs Egger's test via `plots.py`.
> **You get:** the pooled estimate, heterogeneity, plots, and a PRISMA/MOOSE write-up.

## Example 3: Book Review

> **You:** "Resensi buku ini."
> **Skill:** asks for the book's thesis, then produces summary → critique → verdict.

## Journal Targeting (Optional)

> **You:** "Jurnal mana yang cocok untuk review ini?"
> **Skill:** collects the topic, genre, and hard constraints (indexing, quartile, APC budget, deadline), builds 8–15 candidates from the review corpus and the reference list, scores eight criteria 0–5, and runs `shared/scripts/journal_rank.py`.
> **You get:** `journal_shortlist.md`: a ranked table with fit, confidence, evidence gaps, reach/target/safety tiers, a submission cascade, and a cover-letter angle for the top three. Every metric carries a source and a check date; anything unverified is labelled, never guessed.

## Which Skill? FAQ? Something Broke?

- [docs/DECISION_TREE.md](DECISION_TREE.md): which skill do I need?
- [docs/FAQ.md](FAQ.md): scope, references, methods, output files
- [docs/TROUBLESHOOTING.md](TROUBLESHOOTING.md): Windows, encoding, Pandoc, dependencies

## Running The Python Scripts

Every script below is also available as `mar <tool>` after `pip install` (see `mar list`). A complete, runnable chain is in `examples/systematic-review-demo/`.

```bash
python shared/scripts/dedup.py --source Scopus=scopus.csv --source PubMed=pubmed.ris --source WoS=wos.bib
python shared/scripts/prisma_flow.py dedup_out/prisma_identification.json screening_counts.json --strict
python shared/scripts/submission.py cover-letter review.md --shortlist journal_shortlist.json --gate-report review_check.md
python shared/scripts/submission.py response reviewer_comments.txt --review review.md --lang id
```

From the repo root:

```bash
python shared/scripts/meta/example.py    # end-to-end demo of the meta engine
python shared/scripts/meta/pooling.py    # demo of fixed/random effects + I²/Q
python shared/scripts/prisma_flow.py     # demo PRISMA flow → prisma_flow.svg
python shared/scripts/prisma_flow.py counts.json --variant scoping|update --out prisma_flow.svg   # ScR terminology / updated review
python shared/scripts/prisma_flow.py --validate prisma_flow.svg    # structural SVG check (XML, not substrings)
python shared/scripts/journal_rank.py --selftest   # journal-fit scorer checks
python shared/scripts/journal_rank.py journals.csv # ranked shortlist from your evidence table
python shared/scripts/verify_refs.py review.md     # reference consistency (add --online for Crossref)
python shared/scripts/protocol.py --template systematic-review > protocol.json   # then: protocol.py protocol.json --out protocol.md
python shared/scripts/check_review.py review.md       # the gate: header, sections, citations, artifacts
python shared/scripts/screening_agreement.py screening_log.csv --long --reviewers alice,bob
python shared/scripts/validate_extraction.py effects.csv  # meta schema + sanity checks
```

In real work, the skill guides you to (a) prepare the inputs (a screening-counts dict for `prisma_flow.py`, or an `effects.csv` for the meta engine), then (b) run the relevant functions. Scripts live under `shared/scripts/` and are referenced from skills as `../shared/scripts/…`.

## The One Rule That Never Changes

masteracademicreview **never fabricates** study counts, effect sizes, or outcomes. Numbers come from your data or the literature; the code only computes. If a number cannot be produced by the code from real inputs, it does not go in the document. You remain the author and answer for every claim.
