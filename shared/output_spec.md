# Output specification

The deliverable of a masteracademicreview run. Every genre follows this convention, so
the user always knows what they will receive.

## The deliverable

One review document + supporting artifacts + optional export:

```
review.md            ← the review (single source of truth)
prisma_flow.svg      ← systematic / scoping / mapping reviews
forest.png           ← meta-analysis
funnel.png           ← meta-analysis
effects.csv          ← meta-analysis (the extracted effect sizes)
characteristics.csv  ← systematic / scoping / mapping (study table)
screening_log.csv    ← systematic / meta / scoping / mapping
review.docx          ← optional, via export.py (Word)
review.pdf           ← optional, via export.py (needs a PDF engine)
```

`review.md` is the review. The other files are the **auditable artifacts** that
back its numbers and flow; they are referenced from the review, not separate
documents.

## `review.md` — standard layout

```markdown
# <Title of the review>

**Review type:** meta-analysis
**Reporting standard:** PRISMA 2020 + MOOSE
**Sources:** Scopus (only)
**Search date:** 2026-11-16
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
  gate) is mandatory for every genre.
- The **section headings** follow the genre's `Structure` block in its `SKILL.md`.
- **References** follow the genre's citation practice (a running bibliography, a
  `refs.bib`, or inline citations).

## Gate status

Every review ends with a gate check. The status line is one of:

- `✓ passed` — every checklist item present.
- `⚠ partial` — some items partial; the missing ones are listed at the end.
- `✗ failed` — not done; missing items are listed with what is needed.

A review is not "done" unless the gate line says `✓ passed` (or a waiver is
recorded with a reason).

## Export to Word / PDF

```
python shared/scripts/export.py review.md                 # → review.docx + review.pdf
python shared/scripts/export.py review.md --formats docx  # → review.docx only
```

One command, works everywhere:

- If **Pandoc** is installed, it is used (best fidelity).
- If not, `export.py` falls back to the built-in converter (`mdconvert.py`:
  `python-docx` for Word, `reportlab` for PDF) — no extra tools required.
