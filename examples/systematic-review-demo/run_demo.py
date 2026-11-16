#!/usr/bin/env python3
"""Run the whole systematic-review demo, end to end, with every check.

    python examples/systematic-review-demo/run_demo.py

Steps (each is a real tool call; the demo stops at the first failure):

 1. dedup.py            three database exports -> unique records + PRISMA identification
 2. dedup.py again      after the one possible duplicate was checked by hand (--merge-possible)
 3. screening_agreement dual screening log -> kappa / PABAK (agreement.md)
 4. validate_extraction characteristics.csv -> extraction_check.md
 5. protocol.py         protocol.json -> protocol.md (strict: no open fields)
 6. prisma_flow.py      identification + screening counts -> prisma_flow.svg (strict arithmetic)
 7. prisma_flow.py      structural SVG validation
 8. verify_refs.py      reference integrity -> ref_check.md
 9. check_review.py     the gate -> review_check.md
10. journal_rank.py     candidate journals -> ranked shortlist (journal_shortlist.md/.json)
11. submission.py       cover letter for the #1 journal (reads the gate report)
                        + response-to-reviewers skeleton

All data are synthetic. Stdlib only.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

DEMO = Path(__file__).resolve().parent
SCRIPTS = DEMO.parents[1] / "shared" / "scripts"

STEPS = [
    ("1. Deduplicate exports (first pass)", "dedup.py",
     ["--source", "Scopus=search/scopus.csv", "--source", "PubMed=search/pubmed.ris",
      "--source", "WoS=search/wos.bib", "--out-dir", "dedup_first_pass"], 0),
    ("2. Deduplicate after manual check of the possible duplicate", "dedup.py",
     ["--source", "Scopus=search/scopus.csv", "--source", "PubMed=search/pubmed.ris",
      "--source", "WoS=search/wos.bib", "--merge-possible", "--out-dir", "dedup_out"], 0),
    ("3. Screening agreement", "screening_agreement.py",
     ["screening_log.csv", "--out", "agreement.md"], 0),
    ("4. Validate extraction table", "validate_extraction.py",
     ["characteristics.csv", "--profile", "generic", "--required", "study,year,design,n",
      "--key", "study", "--out", "extraction_check.md"], 0),
    ("5. Protocol", "protocol.py", ["protocol.json", "--strict", "--out", "protocol.md"], 0),
    ("6. PRISMA flow", "prisma_flow.py",
     ["dedup_out/prisma_identification.json", "screening_counts.json", "--strict",
      "--out", "prisma_flow.svg"], 0),
    ("7. Validate PRISMA SVG", "prisma_flow.py", ["--validate", "prisma_flow.svg"], 0),
    ("8. Reference integrity", "verify_refs.py", ["review.md", "--out", "ref_check.md"], 0),
    ("9. Review gate", "check_review.py", ["review.md", "--out", "review_check.md"], 0),
    ("10. Rank candidate journals", "journal_rank.py",
     ["journals.csv", "--explain", "--out", "journal_shortlist.md", "--json", "journal_shortlist.json"], 0),
    ("11a. Cover letter for the #1 journal", "submission.py",
     ["cover-letter", "review.md", "--shortlist", "journal_shortlist.json",
      "--gate-report", "review_check.md", "--allow-partial-gate", "--out", "cover_letter.md"], 0),
    ("11b. Response-to-reviewers skeleton", "submission.py",
     ["response", "reviewer_comments.txt", "--review", "review.md", "--out", "response_to_reviewers.md"], 0),
    ("11c. Surat pengantar (Bahasa Indonesia)", "submission.py",
     ["cover-letter", "review.md", "--shortlist", "journal_shortlist.json", "--gate-report",
      "review_check.md", "--allow-partial-gate", "--lang", "id", "--out", "cover_letter.id.md"], 0),
    ("11d. Balasan reviewer (Bahasa Indonesia)", "submission.py",
     ["response", "reviewer_comments.txt", "--review", "review.md", "--lang", "id",
      "--out", "response_to_reviewers.id.md"], 0),
    ("12. Guard: a partial gate without --allow-partial-gate is refused", "submission.py",
     ["cover-letter", "review.md", "--shortlist", "journal_shortlist.json"], 1),
]


def run(label: str, script: str, args: list[str], expected: int) -> bool:
    proc = subprocess.run([sys.executable, str(SCRIPTS / script), *args], cwd=DEMO,
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
    ok = proc.returncode == expected
    print(f'[{"PASS" if ok else "FAIL"}] {label} (exit {proc.returncode:d})')
    if not ok:
        print(proc.stdout[-3000:])
        print(proc.stderr[-3000:])
    return ok


def main() -> int:
    for label, script, args, expected in STEPS:
        if not run(label, script, args, expected):
            return 1
    print("demo OK: every artifact regenerated and every check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
