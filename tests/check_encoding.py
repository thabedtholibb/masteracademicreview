"""Regression: tools must read files saved by Excel and Notepad, not crash.

Writes the same small table as UTF-8, UTF-8 with BOM, UTF-16 ("Unicode Text") and
cp1252 ("CSV (comma delimited)" on Windows) and runs the real tools on each.
Every run must succeed without a traceback.

    python tests/check_encoding.py
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "shared" / "scripts"
ENCODINGS = ("utf-8", "utf-8-sig", "utf-16", "cp1252")

SCREENING = "record_id,stage,reviewer1,reviewer2\nR1,ta,include,exclude\nR2,ta,include,include\nR3,ta,exclude,exclude\n"
EFFECTS = "study,effect,variance,n,design\nAne é,0.2,0.04,30,RCT\nBudi,0.3,0.05,40,RCT\nCitra,0.1,0.06,35,RCT\n"
JOURNALS = ("journal,scope_fit,article_fit,method_fit,indexing,speed,cost,audience,risk,scope_quote\n"
            "Journal é,3,3,3,3,3,3,3,3,Publishes reviews\n")
REVIEW = ("# Tést\n\n**Review type:** Book review  \n**Reporting standard:** none  \n**Sources:** the book  \n"
          "**Search date:** 2026  \n**Gate:** passed\n\n---\n\n## Overview\n\nx\n\n## Summary\n\nx\n\n"
          "## Critical assessment\n\nx\n\n## Verdict\n\nx\n")
COUNTS = '{"database_records": [["Scopus", 5]], "after_dedup": 5, "screened": 5, "excluded_title_abstract": 3, "sought_retrieval": 2, "not_retrieved": 0, "assessed": 2, "included": 2}\n'
JOBS = (
    ("screening_agreement.py", "screening.csv", SCREENING, ["screening.csv"]),
    ("validate_extraction.py", "effects.csv", EFFECTS, ["effects.csv"]),
    ("journal_rank.py", "journals.csv", JOURNALS, ["journals.csv"]),
    ("check_review.py", "review.md", REVIEW, ["review.md", "--no-artifacts"]),
    ("prisma_flow.py", "counts.json", COUNTS, ["counts.json", "--out", "p.svg"]),
)


def main() -> int:
    bad = []
    for script, name, content, args in JOBS:
        for enc in ENCODINGS:
            with tempfile.TemporaryDirectory() as d:
                (Path(d) / name).write_bytes(content.encode(enc))
                proc = subprocess.run([sys.executable, str(SCRIPTS / script), *args], cwd=d,
                                      capture_output=True, text=True, encoding="utf-8", errors="replace")
                if "Traceback" in proc.stderr + proc.stdout or proc.returncode not in (0, 1):
                    bad.append(f"{script} on {enc}: exit {proc.returncode} {proc.stderr.strip()[-120:]}")
    for line in bad:
        print("FAIL:", line)
    if bad:
        return 1
    print(f"encoding check OK ({len(JOBS)} tools x {len(ENCODINGS)} encodings, no tracebacks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
