# Search Strategy (Shared Core)

Use this for any review that requires a reproducible literature search (`systematic-review`, `meta-analysis`, and, adapted, `narrative-review`). The goal is a search that another researcher could rerun and get the same records.

## 1. Frame The Question First

Convert the research question into a structured frame before touching a database:

- **PICO** (quantitative): Population, Intervention, Comparison, Outcome
- **PICo** (qualitative): Population, phenomenon of Interest, Context
- **PICOT**: + Timeframe (for prognosis/incidence questions)
- **SPIDER** (qualitative/mixed): Sample, Phenomenon of Interest, Design, Evaluation, Research type

Write the frame down. It drives every query and every screening criterion.

## 2. Select Databases (Justify The Choice)

Pick databases relevant to the field and **state why**:

| Field | Primary Databases |
|---|---|
| Health/medicine | PubMed/MEDLINE, Embase, Cochrane CENTRAL, CINAHL |
| Multidisciplinary | Scopus, Web of Science |
| Social science | PsycINFO, ERIC, Sociological Abstracts |
| Engineering/CS | IEEE Xplore, ACM DL, Scopus |
| Grey literature | OpenGrey, ProQuest Dissertations, Google Scholar, institutional repositories |

**Recommendation-first:** propose the 1–2 best databases for the field as **#1/#2** with a one-line reason, rather than listing every option and asking the author to pick. Record the **platform**, **date searched**, and **full query string** for each database: verbatim. This is a PRISMA-S item.

**Source restriction for quality (JEV):** for bibliometric and systematic reviews, recommend a single curated index (**Scopus (#1)** or Web of Science (#2)) and document the restriction in PRISMA. A Scopus-only search means every record comes from a Scopus-indexed source; exclude non-indexed venues *at search time*, since indexing cannot be reliably verified post-hoc from an export file alone.

## 3. Build The Query (Document It)

- Break the frame into concepts; for each concept list synonyms, controlled vocabulary (MeSH/Emtree), and free-text terms.
- Combine within a concept with `OR`, across concepts with `AND`.
- Use truncation (`child*`), wildcards, phrase quotes, and field tags (`ti,ab`).
- Example skeleton (PICO):
  ```
  (population terms) AND (intervention terms) AND (comparison terms) AND (outcome terms)
  ```

**Store the exact query string per database.** Translate syntax between platforms (MeSH vs Emtree): do not copy-paste blindly.

## 4. Grey Literature & Supplementary Search

- Search trial/protocol registries (ClinicalTrials.gov, OSF, PROSPERO) where relevant.
- **Snowballing**: backward (scan reference lists of included studies) and forward (who cites the included studies).
- Contact field experts for unpublished work when the question demands it.
- Record every supplementary source and its yield.

## 5. Document The Search (PRISMA-S)

At minimum, record: databases + platform, date, full query per database, filters/limits applied (language, date, study type), and the number of records returned per database **before** deduplication. This feeds directly into `shared/scripts/prisma_flow.py`.

## Guardrails

- Do not claim a search is "comprehensive" if you searched one database.
- Record the *raw* count per database; deduplication happens next, before screening.
- Export every database in a format `dedup.py` reads (RIS, CSV or BibTeX) and run `python shared/scripts/dedup.py --source <Name>=<file> ...`. It removes certain duplicates (DOI; title + year), lists near-matches for a human (`possible_duplicates.csv`), and writes `prisma_identification.json` for the flow diagram.
- If the author cannot access a database, say so: do not fabricate record counts.
