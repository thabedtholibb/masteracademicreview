#!/usr/bin/env python3
"""One command for every tool: ``mar <tool> [options]``.

    mar list                         # tools, grouped by the step of a review
    mar dedup --source Scopus=scopus.csv --source PubMed=pubmed.ris
    mar check-review review.md
    mar selftest                     # run every stdlib selftest
    mar --version

Each tool is the same script the skills call as ``python shared/scripts/<tool>.py``;
this dispatcher runs it in-process with the remaining arguments, so options,
output and exit codes are identical.
"""

from __future__ import annotations

import difflib
import re
import runpy
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# name -> (script relative to this folder, one-line description, review step)
COMMANDS: dict[str, tuple[str, str, str]] = {
    "protocol": ("protocol.py", "registration-ready protocol.md per genre (PROSPERO/OSF)", "1. Plan"),
    "dedup": ("dedup.py", "deduplicate RIS/CSV/BibTeX exports; PRISMA identification counts", "2. Search"),
    "bib-validate": ("bibliometric/validate_export.py", "check a Scopus/WoS export parses correctly", "2. Search"),
    "screening-agreement": ("screening_agreement.py", "Cohen's kappa and PABAK for dual screening", "3. Screen"),
    "prisma": ("prisma_flow.py", "PRISMA 2020 flow diagram (systematic / scoping / update) + checks", "3. Screen"),
    "validate-extraction": ("validate_extraction.py", "check extraction tables before synthesis", "4. Extract"),
    "meta-selftest": ("meta/selftest.py", "verify the meta-analysis engine (needs numpy, scipy)", "5. Synthesise"),
    "meta-demo": ("meta/example.py", "pooled estimate + forest/funnel plots demo (needs [meta])", "5. Synthesise"),
    "verify-refs": ("verify_refs.py", "reference integrity, offline or against Crossref (--online)", "6. Check"),
    "check-review": ("check_review.py", "the review gate: header, sections, citations, artifacts", "6. Check"),
    "journal-rank": ("journal_rank.py", "ranked journal shortlist from your verified evidence", "7. Submit"),
    "submission": ("submission.py", "cover letter for the #1 journal; response to reviewers", "7. Submit"),
    "export": ("export.py", "review.md -> DOCX / PDF (Pandoc or built-in; needs [export])", "7. Submit"),
}

# stdlib-only selftests run by `mar selftest`
SELFTESTS = ("dedup", "protocol", "prisma", "verify-refs", "check-review", "screening-agreement",
             "validate-extraction", "journal-rank", "submission")


def version() -> str:
    m = re.search(r'__version__\s*=\s*"([^"]+)"', (HERE / "__init__.py").read_text(encoding="utf-8"))
    return m.group(1) if m else "unknown"


def usage() -> str:
    lines = [f"masteracademicreview {version()}: tools for writing academic reviews", "",
             "usage: mar <tool> [options]     (mar <tool> --help for a tool's options)", ""]
    step = None
    for name, (_, desc, stage) in COMMANDS.items():
        if stage != step:
            step = stage
            lines.append(f"  {stage}")
        lines.append(f"    {name:<22}{desc}")
    lines += ["", "  other", "    list                  this overview",
              "    selftest              run every stdlib selftest",
              "    --version             print the version", "",
              "Docs: https://github.com/thabedtholibb/masteracademicreview"]
    return "\n".join(lines)


def run_tool(name: str, args: list[str]) -> int:
    script = HERE / COMMANDS[name][0]
    old_argv, old_path = sys.argv[:], sys.path[:]
    sys.argv = [f"mar {name}", *args]
    sys.path.insert(0, str(script.parent))   # tools with flat sibling imports
    try:
        runpy.run_path(str(script), run_name="__main__")
    except SystemExit as exc:
        code = exc.code
        if code is None:
            return 0
        if isinstance(code, int):
            return code
        print(code, file=sys.stderr)
        return 1
    finally:
        sys.argv, sys.path[:] = old_argv, old_path
    return 0


def selftest_all() -> int:
    failed = []
    for name in SELFTESTS:
        proc = subprocess.run([sys.executable, str(HERE / COMMANDS[name][0]), "--selftest"],
                              capture_output=True, text=True, encoding="utf-8", errors="replace")
        ok = proc.returncode == 0
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
        if not ok:
            failed.append(name)
            print((proc.stdout + proc.stderr)[-1500:])
    print(f"{len(SELFTESTS) - len(failed)} passed, {len(failed)} failed")
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] in ("-h", "--help", "help", "list"):
        print(usage())
        return 0
    if argv[0] in ("-V", "--version", "version"):
        print(f"masteracademicreview {version()}")
        return 0
    if argv[0] == "selftest":
        return selftest_all()
    name = argv[0]
    if name not in COMMANDS:
        close = difflib.get_close_matches(name, [*list(COMMANDS), "list", "selftest"], n=1)
        hint = f" Did you mean '{close[0]}'?" if close else " Run 'mar list'."
        print(f"mar: unknown tool '{name}'.{hint}", file=sys.stderr)
        return 2
    return run_tool(name, argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
