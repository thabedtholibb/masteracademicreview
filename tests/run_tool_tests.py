#!/usr/bin/env python3
"""End-to-end checks for the shared scripts (stdlib only, no network).

Run locally with ``python tests/run_tool_tests.py``; CI runs the same command.
Each case asserts the exit code and a few key strings, so a regression in the
CLI surface fails the build, not only the unit selftest.
"""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "shared" / "scripts"
FIXTURES = ROOT / "tests" / "fixtures"


@dataclass
class Case:
    name: str
    script: str
    args: tuple[str, ...]
    expected: int
    contains: tuple[str, ...] = ()
    missing: tuple[str, ...] = ()


CASES = [
    Case("journal_rank rubric", "journal_rank.py", ("--rubric",), 0, ("Scoring anchors", "OFF_ANCHOR")),
    Case(
        "journal_rank explain",
        "journal_rank.py",
        (str(FIXTURES / "journals_example.csv"), "--explain"),
        0,
        ("Largest loss", "#1 recommended"),
    ),
    Case(
        "journal_rank requires scope_quote",
        "journal_rank.py",
        (str(FIXTURES / "journals_noquote.csv"),),
        2,
        ("requires a scope_quote",),
    ),
    Case("protocol selftest", "protocol.py", ("--selftest",), 0, ("protocol selftest OK",)),
    Case(
        "protocol complete (strict)",
        "protocol.py",
        (str(FIXTURES / "protocol_complete.json"), "--strict"),
        0,
        ("# Protocol:", "Amendments log", "PRISMA-P"),
        ("TO COMPLETE",),
    ),
    Case(
        "protocol template",
        "protocol.py",
        ("--template", "scoping-review"),
        0,
        ('"concept"', '"genre": "scoping-review"'),
    ),
    Case(
        "protocol incomplete (strict)",
        "protocol.py",
        (str(FIXTURES / "protocol_incomplete.json"), "--strict"),
        1,
        ("TO COMPLETE: title", "Open fields"),
    ),
    Case("prisma_flow selftest", "prisma_flow.py", ("--selftest",), 0, ("prisma_flow selftest OK", "update")),
    Case("check_review selftest", "check_review.py", ("--selftest",), 0, ("selftest OK",)),
    Case(
        "check_review valid review",
        "check_review.py",
        (str(FIXTURES / "review_ok" / "review.md"),),
        0,
        ("RESULT: PASS", "systematic-review"),
    ),
    Case(
        "check_review broken review",
        "check_review.py",
        (str(FIXTURES / "review_bad" / "review.md"),),
        1,
        ("RESULT: FAIL", "missing field 'sources'", "missing field 'search date'",
         "placeholders", "20/27", "discussion", "prisma_flow.svg"),
    ),
    Case("verify_refs selftest", "verify_refs.py", ("--selftest",), 0, ("selftest OK",)),
    Case(
        "verify_refs clean review",
        "verify_refs.py",
        (str(FIXTURES / "review_refs_clean.md"),),
        0,
        ("RESULT: PASS", "Citation style:** mixed"),
    ),
    Case(
        "verify_refs broken review",
        "verify_refs.py",
        (str(FIXTURES / "review_refs_broken.md"),),
        1,
        ("RESULT: FAIL", "duplicate DOI", "no matching reference", "never cited"),
    ),
    Case(
        "verify_refs running bibliography",
        "verify_refs.py",
        (str(FIXTURES / "review_refs_bibliography.md"),),
        0,
        ("running bibliography", "RESULT: PASS"),
    ),
    Case(
        "verify_refs gate note is not a reference",
        "verify_refs.py",
        (str(FIXTURES / "review_refs_bibliography.md"), "--strict"),
        0,
        ("References parsed:** 3", "RESULT: PASS"),
    ),
    Case(
        "verify_refs missing file",
        "verify_refs.py",
        (str(FIXTURES / "does_not_exist.md"),),
        2,
        ("error: file not found",),
    ),
    Case(
        "screening_agreement selftest",
        "screening_agreement.py",
        ("--selftest",),
        0,
        ("selftest OK",),
    ),
    Case(
        "screening_agreement fixture",
        "screening_agreement.py",
        (str(FIXTURES / "screening_two_reviewers.csv"),),
        0,
        ("0.6939", "0.700", "substantial", "RESULT: PASS"),
    ),
    Case(
        "screening_agreement threshold fails",
        "screening_agreement.py",
        (str(FIXTURES / "screening_two_reviewers.csv"), "--min-kappa", "0.9"),
        1,
        ("RESULT: FAIL", "kappa 0.694"),
    ),
    Case(
        "screening_agreement long format",
        "screening_agreement.py",
        (
            str(FIXTURES / "screening_log_long.csv"),
            "--long",
            "--reviewers",
            "alice,bob",
        ),
        0,
        ("0.6939", "0.700", "RESULT: PASS"),
    ),
    Case(
        "validate_extraction selftest",
        "validate_extraction.py",
        ("--selftest",),
        0,
        ("selftest OK",),
    ),
    Case(
        "validate_extraction valid effects",
        "validate_extraction.py",
        (str(FIXTURES / "effects_valid.csv"),),
        0,
        ("RESULT: PASS", "k = 6", "underpowered"),
    ),
    Case(
        "validate_extraction invalid effects",
        "validate_extraction.py",
        (str(FIXTURES / "effects_invalid.csv"),),
        1,
        ("RESULT: FAIL", "variance must be > 0", "empty 'study'", "not a number"),
    ),
    Case(
        "validate_extraction strict warnings",
        "validate_extraction.py",
        (str(FIXTURES / "effects_valid.csv"), "--strict"),
        1,
        ("RESULT: FAIL",),
    ),
    Case(
        "validate_extraction generic characteristics",
        "validate_extraction.py",
        (
            str(FIXTURES / "characteristics_valid.csv"),
            "--profile",
            "generic",
            "--required",
            "study,year,design",
            "--key",
            "study",
        ),
        0,
        ("RESULT: PASS", "required columns"),
    ),
    Case(
        "validate_extraction missing column",
        "validate_extraction.py",
        (
            str(FIXTURES / "characteristics_valid.csv"),
            "--profile",
            "generic",
            "--required",
            "study,not_a_column",
        ),
        2,
        ("missing required column",),
    ),
]


def run(case: Case) -> tuple[bool, str]:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    completed = subprocess.run(
        [sys.executable, str(SCRIPTS / case.script), *case.args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    output = (completed.stdout or "") + (completed.stderr or "")
    problems: list[str] = []
    if completed.returncode != case.expected:
        problems.append(f"exit {completed.returncode}, expected {case.expected}")
    for text in case.contains:
        if text not in output:
            problems.append(f"missing output: {text!r}")
    for text in case.missing:
        if text in output:
            problems.append(f"unexpected output: {text!r}")
    if problems:
        return False, "\n".join(problems) + "\n--- output ---\n" + output
    return True, ""


def main() -> int:
    failures = 0
    for case in CASES:
        ok, detail = run(case)
        print(f"[{'PASS' if ok else 'FAIL'}] {case.name}")
        if not ok:
            failures += 1
            print(detail)
    print(f"\n{len(CASES) - failures} passed, {failures} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
