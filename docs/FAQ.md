# FAQ

## Scope

**Does it write my whole paper?**
No. It writes **review documents** (13 genres) and the auditable artifacts that
back them. It does not design experiments or generate new findings.

**Does it guarantee acceptance in a Q1 journal?**
No. `journal-match` ranks journals on evidence you verify; the score is a fit
measure, not an acceptance probability. Reporting standards and the gate raise
the floor on rigor, they do not decide peer review.

**Can I use it in a language other than English?**
The skills respond in the language you use. Reporting standards, DOIs and
database names stay as published.

## Evidence and references

**Can the AI invent references?**
It can, which is why `verify_refs.py` exists. Run it on every review. Offline it
catches duplicates, citations with no reference and orphan references; with
`--online` it checks DOI, title and year against Crossref. A reference that
cannot be resolved is fixed or removed, never left in the list.

**`verify_refs.py` says AMBIGUOUS or NO_MATCH for a real source. Why?**
Books, reports, standards and acronym-named guidelines (PRISMA, GRADE) are often
not in Crossref under the title you cited. Check them by hand against the
publisher or the guideline's own site, then keep or fix the entry.

**May I scrape Scopus to fill the journal table?**
No. That violates the terms of service. Look values up manually and record the
source and date in the evidence worksheet (`journal-match/evidence_worksheet.md`).

## Methods

**How many studies do I need for a meta-analysis?**
Pooling works from two studies, but heterogeneity estimates are unstable with
very few. The engine warns for k < 10 on Egger's test, subgroup analysis and
meta-regression, and the prediction interval needs k >= 3.

**Which random-effects estimator should I use?**
For small k or heterogeneous studies, REML with the Hartung-Knapp-Sidik-Jonkman
adjustment (`random_effects(..., method="reml", hksj=True)`). DerSimonian-Laird
is the default for backward compatibility; report it as a sensitivity analysis
if your field expects it. State the estimator in the Methods.

**Why does the gate fail even though my text looks complete?**
`check_review.py` is deliberately strict: missing header fields, missing genre
sections, citations with no reference, referenced artifacts that do not exist,
leftover `TODO` or `[citation needed]`, or a "passed" gate with an incomplete
checklist score. The report lists each finding.

**Do I need to register a protocol?**
For systematic reviews, meta-analyses, umbrella, rapid, realist and
meta-synthesis, yes where the venue expects it (PROSPERO or OSF); scoping and
mapping reviews register on OSF. `protocol.py` produces the document. Narrative,
critical, book and bibliometric reviews do not have a registration step.

## Files and output

**Where do the output files go?**
Next to `review.md`: `prisma_flow.svg`, `forest.png`, `screening_log.csv` and the
reports (`ref_check.md`, `agreement.md`, `extraction_check.md`, `review_check.md`).
See `shared/output_spec.md` for the full list.

**My Word/PDF export looks wrong.**
See `docs/TROUBLESHOOTING.md` (Pandoc and fallback converter).

**Which PRISMA diagram do I use?**
`prisma_flow.py` (default) for new systematic reviews, `--variant scoping` for
scoping reviews, `--variant update` for an updated review.
