# Changelog

Format: [Keep a Changelog](https://keepachangelog.com). Versioning: SemVer.

## [0.1.0] - 2026-11-16
### Added
- 13 review-genre skills, review-router, brainstorm, journal-match.
- Meta-analysis engine, bibliometric engine, PRISMA 2020 flow generator, DOCX/PDF export.
- `verify_refs.py`: reference integrity check (DOI/title/year against Crossref; corporate authors, acronym guidelines, running bibliographies).
- `check_review.py`: review.md gate validator (header, genre sections, citations, artifacts, gate-line consistency).
- `protocol.py`: protocol.md generator for 9 registrable genres (PROSPERO/OSF fields, PRISMA-P), with open-field tracking and an amendments log.
- PRISMA flow variants: `--variant scoping` (PRISMA-ScR/JBI wording) and `--variant update` (updated review: new vs previous studies, total); `--validate` checks SVG structure (boxes, overlaps, arrows, labels) by parsing XML.
- Docs: decision tree, FAQ, troubleshooting (Windows/Pandoc/encoding).
- `screening_agreement.py`: Cohen's kappa / PABAK for dual screening.
- `validate_extraction.py`: extraction CSV schema, duplicate, range and effect-size checks.
- Meta-analysis engine: REML and Paule-Mandel tau², Hartung-Knapp-Sidik-Jonkman option, prediction interval, leave-one-out, subgroup analysis, meta-regression; Egger test now flags k < 10 as inadequate.
- journal-match: 5/3/1/0 scoring anchors (`--rubric`), mandatory `scope_quote` for scope_fit >= 3, `--explain` contributions, `--strict-anchors`, evidence worksheet.
- CI on Ubuntu and Windows (cp1252/encoding regression coverage).
