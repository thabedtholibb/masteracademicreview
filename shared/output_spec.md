# Output specification

The deliverable of a masteracademicreview run. Every genre follows this convention, so
the user always knows what they will receive.

## The deliverable

One review document + supporting artifacts + optional export:

```
protocol.md          ← registration-ready protocol (protocol.py; registrable genres)
review.md            ← the review (single source of truth)
prisma_flow.svg      ← systematic / scoping / mapping reviews
forest.png           ← meta-analysis
funnel.png           ← meta-analysis
effects.csv          ← meta-analysis (the extracted effect sizes)
characteristics.csv  ← systematic / scoping / mapping (study table)
screening_log.csv    ← systematic / meta / scoping / mapping
conflicts.csv        ← disagreements for adjudication (screening_agreement.py)
agreement.md         ← dual-screening κ/PABAK report (screening_agreement.py)
extraction_check.md  ← extraction validation report (validate_extraction.py)
ref_check.md         ← reference integrity report (verify_refs.py)
review_check.md      ← gate validation report (check_review.py)
review.docx          ← optional, via export.py (Word)
review.pdf           ← optional, via export.py (needs a PDF engine)
```

`review.md` is the review. The other files are the **auditable artifacts** that
back its numbers and flow; they are referenced from the review, not separate
documents.

## `review.md` — standard layout

```markdown
# <Title of the review>

**Review type:** meta-analysis··
**Reporting standard:** PRISMA 2020 + MOOSE··
**Sources:** Scopus (only)··
**Search date:** 2026-11-16··
**Gate:** ✓ passed (PRISMA 27/27)

---

## Abstract

## 1. Introduction

## 2. Methods

## 3. Results

## 4. Discussion

## References
```

- The **metadata header** (review type, reporting standard, sources, search date,
  gate) is mandatory for every genre. End each line with **two spaces** (`··` above)
  so Markdown treats it as a hard break; otherwise the fields collapse into one
  paragraph in DOCX/PDF.
- The **section headings** follow the genre's `Structure` block in its `SKILL.md`.
- **References** follow the genre's citation practice (a running bibliography, a
  `refs.bib`, or inline citations).

## Gate status

Every review ends with a gate check. The status line is one of:

- `✓ passed` — every checklist item present.
- `⚠ partial` — some items partial; the missing ones are listed at the end.
- `✗ failed` — not done; missing items are listed with what is needed.

`python shared/scripts/check_review.py review.md` automates this gate: header fields, genre sections, citations, artifacts and gate-line consistency. A review is not "done" unless the gate line says `✓ passed` (or a waiver is
recorded with a reason).

For **every** genre, the gate cannot pass while `verify_refs.py` reports an error
(an unresolved citation or a duplicate DOI). Systematic and meta reviews also run
`screening_agreement.py` and `validate_extraction.py`; their reports are the
artifacts listed above. A reference that cannot be resolved is fixed or removed,
never left in the list.

## Export to Word / PDF

```
python shared/scripts/export.py review.md                 # → review.docx + review.pdf
python shared/scripts/export.py review.md --formats docx  # → review.docx only
```

One command, works everywhere:

- If **Pandoc** is installed, it is used (best fidelity).
- If not, `export.py` falls back to the built-in converter (`mdconvert.py`:
  `python-docx` for Word, `reportlab` for PDF) — no extra tools required.
