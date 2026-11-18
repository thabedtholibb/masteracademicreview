---
name: bibliometric-review
description: "Conduct a bibliometric review: analyze a body of literature with citation, co-word, and co-authorship methods to map its intellectual structure and trends, using a bundled Python engine. Reported per PRISMA 2020 (search) plus bibliometric conventions. Use when the deliverable is a quantitative map of a field (authors, sources, themes) rather than a synthesis of findings. Trigger terms: bibliometric review, bibliometric analysis, citation analysis, co-citation, co-word, science mapping, VOSviewer, bibliometrix."
metadata:
  version: "0.1.0"
  genre: bibliometric-review
  reporting_standard: "PRISMA 2020 (search) + Donthu et al. (2021)"
  requires_python: true
---

# Bibliometric Review

You analyze a literature corpus **quantitatively**, through citation, co-word and co-authorship analysis, to map a field's intellectual structure, influential works, and trends. The unit of analysis is *the record*, not the finding. The numbers are computed by the bundled engine, never guessed.

## Scope

- **In scope:** a large corpus where the question is "who/what/how is this field structured" (authors, journals, themes, trends).
- **Out of scope:** synthesizing findings (→ `systematic-review` / `narrative-review`); small corpora (bibliometrics needs volume).

## Pre-Requisites

1. A searchable corpus large enough for bibliometrics (typically hundreds+ of records).
2. A **Scopus CSV export** (recommended), or a WoS/BibTeX export, with the `Document Type` column. The loader auto-detects the delimiter (`;` for Scopus, tab for WoS) and the encoding (`UTF-8` or `cp1252`), so the raw export can be used as-is.
3. Python 3.10+ with `numpy` and `matplotlib` (no other dependencies).

## Source Quality: Scopus-Only

Recommend **Scopus (#1)** as the sole source and state it in the methods. Restrict at search time; you cannot reliably verify indexing post-hoc from an export file alone. Then filter record types so the corpus is peer-reviewed:

- **Keep (#1):** `Article`, `Review`.
- **Drop:** `Conference Paper`, `Erratum`, `Note`, `Editorial`, `Letter`: non-indexed venues usually surface as one of these.

## Method (JEV)

1. **Search & collect (Scopus-only):** restrict to **Scopus** and document it (PRISMA); export records **including `Document Type`**.
2. **Choose the analysis (JEV):** recommend by goal:
   - **Science mapping (#1):** co-word and co-authorship → thematic/intellectual structure.
   - **Performance analysis (#2):** publication counts, citations, h-index, top authors/sources.
   - **Both (#3)** for a full picture. Recommend #3 for a complete bibliometric review.
3. **Filter to quality records (JEV):** keep **Article + Review (#1)**.
4. **Run the analysis:** use the bundled engine (`shared/scripts/bibliometric/`):
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
5. **Interpret & report:** turn the numbers and maps into a narrative of the field's structure, trends, and gaps; PRISMA for the search, stating Scopus as the sole source.

## What The Code Does (`shared/scripts/bibliometric/`)

| Task | Function |
|---|---|
| Load corpus (CSV or BibTeX) | `load`, `load_csv`, `load_bibtex` |
| Corpus overview | `summary` |
| Publications per year | `publications_per_year` |
| Top authors / journals / keywords | `top_authors` / `top_journals` / `top_keywords` (index-keyword noise filtered via `KEYWORD_NOISE`; pass `exclude=None` to keep all) |
| h-index (corpus or per author) | `h_index` / `author_h_index` |
| Document-type counts / quality filter | `document_type_counts` / `filter_document_type` |
| Co-word / co-authorship matrices | `co_occurrence` / `co_authorship` |
| Trend / top-bar / heatmap plots | `plot_pubs_per_year` / `plot_top` / `plot_heatmap` |

Run the demo end-to-end: `python shared/scripts/bibliometric/example.py`.

## Structure

```
Title
Abstract
1. Introduction: rationale
2. Methods: search (PRISMA, Scopus-only), corpus, document-type filter, techniques
3. Results: performance + science-mapping outputs (trend, top lists, co-occurrence map)
4. Discussion: intellectual structure, trends, limitations
References
```

## Decision Points (JEV)

Every decision here follows the JEV protocol (`../shared/jev.md`): ranked options, **#1 recommended**, one line of evidence each, what would change the ranking, and the author approves. Approved choices go into `decisions.md`.

- **Source.** **#1 recommended:** Scopus only (see Source quality). #2: Scopus plus Web of Science merged with `dedup.py`, only when coverage demands it, with the merge reported.
- **Record types.** **#1 recommended:** Article + Review.
- **Thresholds.** **#1 recommended:** report every threshold (minimum keyword frequency, minimum documents per author) and re-run one alternative threshold as a sensitivity check.

## Standards & Sources

Reporting: **PRISMA 2020** for the search (Page et al., 2021, doi:10.1136/bmj.n71). Method sources: Donthu et al. 2021 (doi:10.1016/j.jbusres.2021.04.070), Zupic & Čater 2015 (doi:10.1177/1094428114562629), van Eck & Waltman 2010 (doi:10.1007/s11192-009-0146-3), Aria & Cuccurullo 2017 (doi:10.1016/j.joi.2017.08.007). Full citations and the Q1-readiness checklist: `shared/method_sources.md`.

## Gate

- [ ] The corpus, its retrieval, and the Scopus-only restriction are documented (PRISMA).
- [ ] The document-type filter (Article/Review) was applied and reported.
- [ ] The analysis method (science mapping / performance) is stated.
- [ ] The numbers are produced by the engine from the corpus, not hand-computed.
- [ ] Maps/clusters are interpreted, not just displayed.

**Automated Gate:** run these before you call the review done. Both are offline; `pip install masteracademicreview` provides `mar`.

- [ ] `mar check-review review.md` reports **0 errors**: header fields, the sections this genre needs, citations matched to references, referenced and required artifacts present, no placeholders, and a gate line that matches the checklist. It ranks what to fix first.
- [ ] `mar verify-refs review.md` finds no unresolved citation or duplicate DOI; add `--online` before submission to check every reference against Crossref.

## Guardrails

- Scopus indexing is a *source* claim, not a quality certificate: a Scopus-indexed paper can still be weak; say so rather than equating indexing with correctness.
- The engine covers performance + co-word + co-authorship. Co-citation and bibliographic coupling need citation-reference data; if your export lacks it, use an external tool (VOSviewer/Bibliometrix) or state that the analysis was not run: never fabricate a network.
- **Keyword variants are not merged automatically** ("digital twin" vs "digital twins"). For a clean map, merge plurals/synonyms with a thesaurus (VOSviewer/Bibliometrix export) and report the merge rule; do not silently hand-edit counts.
- Every number in the report must trace to `summary()` / `co_occurrence()` output from the real corpus.
