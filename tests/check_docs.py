"""Repository integrity checks for the skills documentation.

Guards the claims the README makes:
- every review genre has a 'Standards & sources' section and a gate;
- the method-provenance file exists and carries enough verified DOIs;
- the reporting-standards file covers every standard named by a genre skill;
- the journal scorer and the journal-match skill are present;
- the reproducibility tools exist and are wired into the shared documentation.

Stdlib only. Exit 0 on success, 1 on the first broken invariant.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GENRES = [
    "book-review",
    "narrative-review",
    "critical-review",
    "systematic-review",
    "meta-analysis",
    "scoping-review",
    "umbrella-review",
    "meta-synthesis",
    "rapid-review",
    "integrative-review",
    "mapping-review",
    "bibliometric-review",
    "realist-review",
]

errors: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def dois_in(text: str) -> set[str]:
    found = re.findall(r"10\.\d{4,9}/[^\s`<>]+", text)
    return {d.rstrip(".,;)]").lower() for d in found}


source_text = ""
sources = ROOT / "shared" / "method_sources.md"
if not sources.exists():
    fail("shared/method_sources.md missing")
else:
    source_text = sources.read_text(encoding="utf-8")
    source_dois = dois_in(source_text)
    if len(source_dois) < 35:
        fail(f"shared/method_sources.md: only {len(source_dois)} unique DOIs (expected >= 35)")


for genre in GENRES:
    skill = ROOT / genre / "SKILL.md"
    if not skill.exists():
        fail(f"{genre}: SKILL.md missing")
        continue
    text = skill.read_text(encoding="utf-8")
    if "## Standards & sources" not in text:
        fail(f"{genre}: missing '## Standards & sources'")
    if not re.search(r"^## .*gate", text, re.M | re.I):
        fail(f"{genre}: missing a gate section")
    if "shared/method_sources.md" not in text:
        fail(f"{genre}: does not point to shared/method_sources.md")
    if not re.search(r"\b(19|20)\d{2}\b", text.split("## Standards & sources", 1)[-1]):
        fail(f"{genre}: standards section carries no publication year")
    if source_text:
        section = text.split("## Standards & sources", 1)[-1].split("\n## ", 1)[0]
        for doi in sorted(dois_in(section)):
            if doi not in source_dois:
                fail(f"{genre}: DOI not present in method_sources.md: {doi}")
    front = text.split("---", 2)
    if len(front) >= 3 and "reporting_standard:" not in front[1]:
        fail(f"{genre}: frontmatter has no reporting_standard")


standards = ROOT / "shared" / "reporting_standards.md"
if not standards.exists():
    fail("shared/reporting_standards.md missing")
else:
    report = standards.read_text(encoding="utf-8")
    for standard in ("PRISMA 2020", "PRISMA-ScR", "SANRA", "ENTREQ", "PRIOR", "RAMESES", "ROSES", "AMSTAR-2"):
        if standard not in report:
            fail(f"shared/reporting_standards.md: missing {standard}")

for skill in ("journal-match", "brainstorm", "review-router"):
    if not (ROOT / skill / "SKILL.md").exists():
        fail(f"{skill}: SKILL.md missing")

if not (ROOT / "shared" / "scripts" / "journal_rank.py").exists():
    fail("shared/scripts/journal_rank.py missing")

for doc_page in ("DECISION_TREE.md", "FAQ.md", "TROUBLESHOOTING.md"):
    if not (ROOT / "docs" / doc_page).exists():
        fail(f"docs/{doc_page} missing")

for script in ("verify_refs.py", "screening_agreement.py", "validate_extraction.py", "check_review.py", "protocol.py"):
    if not (ROOT / "shared" / "scripts" / script).exists():
        fail(f"shared/scripts/{script} missing")

for doc, needle in {
    "shared/screening.md": "screening_agreement.py",
    "shared/data_extraction.md": "validate_extraction.py",
    "shared/output_spec.md": "verify_refs.py",
    "shared/method_sources.md": "Byrt et al. 1993",
}.items():
    path = ROOT / doc
    if not path.exists():
        fail(f"{doc} missing")
    elif needle not in path.read_text(encoding="utf-8"):
        fail(f"{doc}: does not reference {needle}")

if not (ROOT / "tests" / "run_tool_tests.py").exists():
    fail("tests/run_tool_tests.py missing")

if errors:
    print("documentation checks FAILED:")
    for err in errors:
        print(f"  - {err}")
    sys.exit(1)

print(
    f"documentation checks OK ({len(GENRES)} genres, standards + gates + provenance "
    "+ journal skill + reproducibility tools)"
)
