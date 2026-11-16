# End-to-end demo: a systematic review, from database exports to cover letter

> **All data here are synthetic.** Every study, author, journal and DOI is
> fictional (DOIs use the test prefix `10.5555`). The demo shows how the tools
> fit together; it is not evidence about anything.
> *Semua data di sini fiktif. Contoh ini hanya menunjukkan alur kerja alatnya.*

Run it from the repository root:

```bash
python examples/systematic-review-demo/run_demo.py
```

Twelve real tool calls run in order and the demo stops at the first failure.
CI runs it on every push, so the example cannot silently go stale.

## The pipeline

| Step | Tool | Input | Output |
|---|---|---|---|
| 1 | `dedup.py` | `search/scopus.csv`, `search/pubmed.ris`, `search/wos.bib` (11 records) | `dedup_first_pass/`: 3 certain duplicates removed, **1 possible duplicate** listed for a human |
| 2 | `dedup.py --merge-possible` | same exports, after checking the pair by hand | `dedup_out/`: 7 unique records, `prisma_identification.json`, `screening_template.csv` |
| 3 | `screening_agreement.py` | `screening_log.csv` (two reviewers) | `agreement.md` (Cohen's kappa, PABAK) |
| 4 | `validate_extraction.py` | `characteristics.csv` | `extraction_check.md` |
| 5 | `protocol.py --strict` | `protocol.json` | `protocol.md` (no open fields) |
| 6 | `prisma_flow.py --strict` | `dedup_out/prisma_identification.json` + `screening_counts.json` | `prisma_flow.svg` (counts must add up) |
| 7 | `prisma_flow.py --validate` | `prisma_flow.svg` | structural check |
| 8 | `verify_refs.py` | `review.md` | `ref_check.md` |
| 9 | `check_review.py` | `review.md` + artifacts | `review_check.md` (the gate) |
| 10 | `journal_rank.py --explain --json` | `journals.csv` | `journal_shortlist.md` / `.json` (ranked, #1 recommended) |
| 11a | `submission.py cover-letter` | `review.md` + shortlist + gate report | `cover_letter.md` for the #1 journal |
| 11b | `submission.py response` | `reviewer_comments.txt` | `response_to_reviewers.md` (ranked revision plan) |

## What to look at

- **JEV in dedup.** Certain duplicates (same DOI; same title and year) are
  removed automatically. The near-identical pair "Group dance *classes*" /
  "*clases*" is only *recommended* as a duplicate in
  `dedup_first_pass/possible_duplicates.csv`; a person decides.
- **Numbers that add up.** `prisma_flow.py --strict` refuses a diagram whose
  boxes do not reconcile (11 identified − 4 duplicates = 7 screened; 3 + 4 = 7;
  1 + 3 = 4).
- **An honest gate.** `review.md` declares `⚠ partial (PRISMA 24/27)` and names
  the missing items. The cover letter is only produced because the demo passes
  `--allow-partial-gate`, and the checklist under the letter says so.
- **Ranked revision plan.** Major reviewer comments come first in
  `response_to_reviewers.md`.

`verify_refs.py --online` would report the fictional DOIs as `NOT_FOUND`;
that is expected here and is exactly what it should do with invented
references in a real review.
