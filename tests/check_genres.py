"""Cross-genre test: every skill's Structure block must pass the review gate.

For each of the 13 genres this builds a minimal review.md whose headings come
straight from the skill's own "Structure" block, adds the header, one resolvable
reference and the artifacts the genre requires, and runs ``check_review``.
It then removes each required section in turn and expects the gate to object.
A skill and the validator can therefore no longer drift apart unnoticed.

    python tests/check_genres.py
"""

from __future__ import annotations

import importlib.util
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared" / "scripts"))
spec = importlib.util.spec_from_file_location("check_review", ROOT / "shared" / "scripts" / "check_review.py")
cr = importlib.util.module_from_spec(spec)
sys.modules["check_review"] = cr
spec.loader.exec_module(cr)

REVIEW_TYPE = {                        # a realistic "Review type" line per genre
    "systematic-review": "Systematic review", "meta-analysis": "Systematic review and meta-analysis",
    "scoping-review": "Scoping review", "umbrella-review": "Umbrella review",
    "meta-synthesis": "Qualitative evidence synthesis (meta-synthesis)", "rapid-review": "Rapid review",
    "integrative-review": "Integrative review", "mapping-review": "Systematic mapping review",
    "bibliometric-review": "Bibliometric review", "realist-review": "Realist review",
    "narrative-review": "Narrative literature review", "critical-review": "Critical review",
    "book-review": "Book review",
}
SKIP = re.compile(r"^(title|other)\b", re.I)


def structure_headings(genre: str) -> list[str]:
    text = (ROOT / genre / "SKILL.md").read_text(encoding="utf-8")
    m = re.search(r"^## Structure[^\n]*\n+```\n(.*?)```", text, re.S | re.M)
    if not m:
        return []
    heads = []
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or SKIP.match(line):
            continue
        heads.append(re.sub(r"^\d+\.\s*", "", line).split(":")[0].split(" (")[0].strip())
    return heads


def build_review(genre: str, headings: list[str]) -> str:
    standard = cr.GENRES[genre][1]
    gate = "✓ passed (checklist 27/27)" if genre in cr.REQUIRED_ARTIFACTS else "✓ passed"
    body = [f"# A Test Review ({genre})", "",
            f"**Review type:** {REVIEW_TYPE[genre]}  ", "**Reporting standard:** test  ",
            "**Sources:** Scopus  ", "**Search date:** 2026-01-01  ", f"**Gate:** {gate}", "", "---", ""]
    needed = [h for h in headings if not re.match(r"references?\b", h, re.I)]
    for h in needed:
        body += [f"## {h}", "", "Text (Smith, 2020).", ""]
    if "references" in standard:
        body += ["## References", "",
                 "1. Smith J. A study of things. *Journal of Tests*, 2020. doi:10.1000/abc123", ""]
    return "\n".join(body)


def run() -> int:
    problems = []
    for genre in cr.GENRES:
        heads = structure_headings(genre)
        if not heads:
            problems.append(f"{genre}: SKILL.md has no Structure block")
            continue
        if cr.detect_genre(REVIEW_TYPE[genre], None) != genre:
            problems.append(f"{genre}: '{REVIEW_TYPE[genre]}' is detected as {cr.detect_genre(REVIEW_TYPE[genre], None)}")
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            for name in cr.REQUIRED_ARTIFACTS.get(genre, ()):
                (folder / name).write_text("x", encoding="utf-8")
            review = build_review(genre, heads)
            rep = cr.check_review(review, folder)
            if rep.errors:
                problems.append(f"{genre}: the skill's own Structure fails the gate: {rep.errors[:2]}")
                continue
            for pat in cr.GENRES[genre][1]:                     # drop each required section in turn
                lines = [ln for ln in review.splitlines() if not (ln.startswith("## ") and re.search(pat, ln.lower()))]
                if not any(e.startswith("section") for e in cr.check_review("\n".join(lines), folder).errors):
                    problems.append(f"{genre}: removing the '{pat}' section was not caught")
    for p in problems:
        print("FAIL:", p)
    if problems:
        return 1
    print(f"genre check OK ({len(cr.GENRES)} genres: skill Structure, detection, section and artifact rules agree)")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
