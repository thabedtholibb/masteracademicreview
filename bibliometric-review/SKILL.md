---
name: bibliometric-review
description: "Conduct a bibliometric review — analyze a body of literature with citation, co-word, and co-authorship methods to map its intellectual structure and trends, using a bundled Python engine. Reported per PRISMA (search) plus bibliometric conventions. Use when the deliverable is a quantitative map of a field (authors, sources, themes) rather than a synthesis of findings. Trigger terms: bibliometric review, bibliometric analysis, citation analysis, co-citation, co-word, science mapping, VOSviewer, bibliometrix."
metadata:
  version: "0.1.0"
  genre: bibliometric-review
  reporting_standard: "PRISMA (search) + bibliometric conventions"
  requires_python: true
---

# Bibliometric Review

You analyze a literature corpus **quantitatively** — through citation, co-word, and co-authorship — to map a field's intellectual structure, influential works, and trends. The unit of analysis is *the record*, not the finding. The numbers are computed by the bundled engine, never guessed.

## Scope

- **In scope:** a large corpus where the question is "who/what/how is this field structured" (authors, journals, themes, trends).
- **Out of scope:** synthesizing findings (→ `systematic-review` / `narrative-review`); small corpora (bibliometrics needs volume).

## Pre-requisites

1. A searchable corpus large enough for bibliometrics (typically hundreds+ of records).
2. A **Scopus CSV export** (recommended) — or a WoS/BibTeX export — with the `Document Type` column.
3. Python 3.10+ with `numpy` and `matplotlib` (no other dependencies).

## Source quality — Scopus-only

Recommend **Scopus (#1)** as the sole source and state it in the methods. Restrict at search time; you cannot reliably verify indexing post-hoc from an export file alone. Then filter record types so the corpus is peer-reviewed:

- **Keep (#1):** `Article`, `Review`.
- **Drop:** `Conference Paper`, `Erratum`, `Note`, `Editorial`, `Letter` — non-indexed venues usually surface as one of these.

## Method (recommendation-first)

1. **Search & collect (Scopus-only)** — restrict to **Scopus** and document it (PRISMA); export records **including `Document Type`**.
2. **Choose the analysis (recommendation-first)** — recommend by goal:
   - **Science mapping (#1)** — co-word and co-authorship → thematic/intellectual structure.
   - **Performance analysis (#2)** — publication counts, citations, h-index, top authors/sources.
   - **Both (#3)** for a full picture. Recommend #3 for a complete bibliometric review.
3. **Filter to quality records (recommendation-first)** — keep **Article + Review (#1)**.
4. **Run the analysis** — use the bundled engine (`shared/scripts/bibliometric/`):
   ```python
   import sys; sys.path.insert(0, "shared/scripts/bibliometric")
   from parsers import load
   from performance import (summary, publications_per_year, top_authors, top_journals,
                            document_type_counts, filter_document_type)
   from mapping import co_occurrence
   from plots import plot_pubs_per_year, plot_top, plot_heatmap

   records = load("scopus.csv")                              # Scopus CSV export
   print(document_type_counts(records))                      # inspect the corpus
   records = filter_document_type(records, ["article", "review"])   # quality gate
   s = summary(records)                                      # n_records, years, h-index, tops
   labels, m = co_occurrence(records, field="keywords", top_n=20)
   plot_pubs_per_year(publications_per_year(records), filename="pubs_per_year.png")
   plot_top(top_authors(records, 10), filename="top_authors.png", xlabel="Papers")
   plot_heatmap(labels, m, filename="cooccurrence.png", title="Keyword co-occurrence")
   ```
5. **Interpret & report** — turn the numbers and maps into a narrative of the field's structure, trends, and gaps; PRISMA for the search, stating Scopus as the sole source.

## What the code does (`shared/scripts/bibliometric/`)

| Task | Function |
|---|---|
| Load corpus (CSV or BibTeX) | `load`, `load_csv`, `load_bibtex` |
| Corpus overview | `summary` |
| Publications per year | `publications_per_year` |
| Top authors / journals / keywords | `top_authors` / `top_journals` / `top_keywords` |
| h-index (corpus or per author) | `h_index` / `author_h_index` |
| Document-type counts / quality filter | `document_type_counts` / `filter_document_type` |
| Co-word / co-authorship matrices | `co_occurrence` / `co_authorship` |
| Trend / top-bar / heatmap plots | `plot_pubs_per_year` / `plot_top` / `plot_heatmap` |

Run the demo end-to-end: `python shared/scripts/bibliometric/example.py`.

## Structure

```
Title
Abstract
1. Introduction — rationale
2. Methods — search (PRISMA, Scopus-only), corpus, document-type filter, techniques
3. Results — performance + science-mapping outputs (trend, top lists, co-occurrence map)
4. Discussion — intellectual structure, trends, limitations
```

## Gate

- [ ] The corpus, its retrieval, and the Scopus-only restriction are documented (PRISMA).
- [ ] The document-type filter (Article/Review) was applied and reported.
- [ ] The analysis method (science mapping / performance) is stated.
- [ ] The numbers are produced by the engine from the corpus — not hand-computed.
- [ ] Maps/clusters are interpreted, not just displayed.

## Guardrails

- Scopus indexing is a *source* claim, not a quality certificate — a Scopus-indexed paper can still be weak; say so rather than equating indexing with correctness.
- The engine covers performance + co-word + co-authorship. Co-citation and bibliographic coupling need citation-reference data; if your export lacks it, use an external tool (VOSviewer/Bibliometrix) or state that the analysis was not run — never fabricate a network.
- Every number in the report must trace to `summary()` / `co_occurrence()` output from the real corpus.
