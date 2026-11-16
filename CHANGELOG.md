# Changelog

Format: [Keep a Changelog](https://keepachangelog.com). Versioning: SemVer.

## [Unreleased]
### Changed
- Slash commands are prefixed with the suite's initials: `/mar-review`, `/mar-meta-analysis`, `/mar-systematic-review`, ... (type `/mar` to list them all); descriptions start with `MAR ·`. Skill IDs are unchanged. If you copied the old commands into `.claude/commands/`, delete the old unprefixed files and copy `commands/mar-*.md` again.

## [0.1.1] - 2026-11-17
### Changed
- House style: Title Case headings and table headers across all docs, skills and generated reports, enforced by `tests/check_docs.py`; em-dashes used as sentence joiners replaced (385 to 0 outside tables, code blocks and quoted titles).
- Code: one formatting idiom (f-strings), unused imports removed, `ruff` lint job in CI.
- Meta-analysis engine fails early with a readable message when effects and variances differ in length or a variance is not positive (previously `zip` could silently truncate).

### Fixed
- `journal_rank.py` selftest was no longer run by `tests/run_tool_tests.py`; it is again.

## [0.1.0] - 2026-11-16
### Added
- `dedup.py`: deduplicate RIS/CSV/BibTeX exports from several databases (DOI, then title + year; fuzzy near-matches only recommended), with a removal log, PRISMA identification counts and a screening template.
- `submission.py`: cover letter for the #1 clean journal from the `journal_rank.py` shortlist (refused while the gate fails or the journal is flagged) and a ranked point-by-point response to reviewers; English and Indonesian.
- pip package `masteracademicreview` with one command, `mar <tool>` (also `python -m masteracademicreview`); extras `[meta]`, `[bibliometric]`, `[export]`, `[all]`.
- JEV decision protocol (`shared/jev.md`); every genre skill has *Decision points (JEV)*; `check_review.py` prints ranked next steps.
- `prisma_flow.py` merges several counts files and refuses diagrams whose numbers do not add up (`--strict`).
- End-to-end example `examples/systematic-review-demo/` (synthetic data), run in CI.
- Meta-analysis: Doi plot and LFK index (`doi_plot`, `lfk_index`), same algorithm as R `metasens::lfkindex` and cross-checked against it in CI; reported as supplementary only, with the Schwarzer et al. (2024) reliability caveat.
- All 59 DOIs in `shared/method_sources.md` verified against Crossref (title and year).
- Bahasa Indonesia: `README.id.md`, `docs/id/PANDUAN.md`, `docs/id/FAQ.md`, Indonesian letter templates.
- `SECURITY.md`, `CODE_OF_CONDUCT.md`; monthly Crossref verification of every method DOI; manual PyPI publish workflow.
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
- CI on Ubuntu and Windows with Python 3.10-3.13 (cp1252/encoding regression coverage), plus a build-and-install test of the wheel outside the repository.

### Fixed
- `verify_refs.py --online`, found by running it on `shared/method_sources.md`: Crossref subtitles were ignored
  (false DOI_MISMATCH for titles with a subtitle); a page range such as `2000;283(15):2008-2012` was read as
  the year (false YEAR_MISMATCH); Crossref titles with HTML tags, entities or line breaks broke the report
  table. All 54 listed method sources now verify.
- `verify_refs.py` used a backslash inside an f-string expression, a syntax error before Python 3.12; it crashed (and `check_review.py` with it) on Python 3.10 and 3.11.
