#!/usr/bin/env python3
"""Deterministic validator for review.md (the gate, made testable).

Checks, per the output spec (shared/output_spec.md):

1. the metadata header (Review type, Reporting standard, Sources,
   Search date, Gate), including hard line breaks;
2. the mandatory sections for the review genre;
3. in-text citations <-> reference list (delegates to verify_refs.py);
4. artifacts referenced in the text exist, and the artifacts a genre
   requires are present next to the review;
5. the gate line is consistent: "passed" needs a complete checklist
   score, no reference errors and no placeholders; "partial"/"failed"
   must list what is missing.

Stdlib only; offline. Exit codes: 0 = pass, 1 = errors, 2 = cannot read.
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
import contextlib

HERE = Path(__file__).resolve().parent

IMRAD = ("abstract", "introduction", "methods", "results|findings",
         "discussion", "references")

# genre key -> (aliases found in "Review type", required heading patterns)
GENRES: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "systematic-review": (("systematic review",), IMRAD),
    "meta-analysis": (("meta-analysis", "meta analysis"), IMRAD),
    "scoping-review": (("scoping review",), IMRAD),
    "umbrella-review": (("umbrella", "overview of reviews"), IMRAD),
    "meta-synthesis": (("meta-synthesis", "meta synthesis", "meta-ethnography"), IMRAD),
    "rapid-review": (("rapid review",), IMRAD),
    "integrative-review": (("integrative review",), IMRAD),
    "mapping-review": (("mapping review", "systematic map"), IMRAD),
    "bibliometric-review": (("bibliometric",), IMRAD),
    "realist-review": (("realist",), IMRAD),
    "narrative-review": (
        ("narrative review",),
        ("introduction", "thematic|theme", "contradiction|gap|gaps",
         "conclusion", "references"),
    ),
    "critical-review": (
        ("critical review",),
        ("thesis", "debate", "critique", "alternative", "implications",
         "references"),
    ),
    "book-review": (
        ("book review",),
        ("overview", "summary", "assessment|critical", "verdict"),
    ),
}

# artifacts that must sit next to review.md for the genre
REQUIRED_ARTIFACTS = {
    "systematic-review": ("prisma_flow.svg", "screening_log.csv", "characteristics.csv"),
    "meta-analysis": ("prisma_flow.svg", "screening_log.csv", "effects.csv",
                      "forest.png", "funnel.png"),
    "scoping-review": ("prisma_flow.svg", "screening_log.csv", "characteristics.csv"),
    "mapping-review": ("prisma_flow.svg", "screening_log.csv", "characteristics.csv"),
}

META_FIELDS = ("review type", "reporting standard", "sources", "search date", "gate")

ARTIFACT_NAMES = {
    "prisma_flow.svg", "forest.png", "funnel.png", "effects.csv",
    "characteristics.csv", "screening_log.csv", "conflicts.csv",
    "agreement.md", "extraction_check.md", "ref_check.md",
}
PLACEHOLDER_RE = re.compile(
    r"\[citation needed\]|\bTODO\b|\bTBD\b|\bXXX\b|lorem ipsum", re.I)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
GATE_STATUS_RE = re.compile(r"(✓|✔|✗|✘|⚠)\s*(passed|partial|failed)", re.I)
SCORE_RE = re.compile(r"(\d+)\s*/\s*(\d+)")


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    infos: list[str] = field(default_factory=list)
    genre: str = "unknown"

    @property
    def ok(self) -> bool:
        return not self.errors


def _load_verify_refs():
    spec = importlib.util.spec_from_file_location("verify_refs", HERE / "verify_refs.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["verify_refs"] = module
    spec.loader.exec_module(module)
    return module


def parse_metadata(lines: list[str]) -> tuple[dict[str, str], dict[str, bool]]:
    """Read ``**Field:** value`` lines from the header (before the first rule/section)."""
    meta: dict[str, str] = {}
    hard_break: dict[str, bool] = {}
    seen_title = False
    for raw in lines[:40]:
        if raw.startswith("#") and not seen_title:
            seen_title = True
            continue
        if raw.strip() == "---" or raw.startswith("##"):
            break
        m = re.match(r"\*\*\s*([^*:]+?)\s*:?\s*\*\*\s*:?\s*(.*)$", raw.strip())
        if m:
            key = m.group(1).strip().lower().rstrip(":")
            meta[key] = m.group(2).strip()
            hard_break[key] = raw.endswith("  ") or raw.rstrip().endswith("\\")
    return meta, hard_break


def detect_genre(review_type: str, override: str | None) -> str:
    if override:
        return override
    rt = review_type.lower()
    for genre, (aliases, _) in GENRES.items():
        if any(a in rt for a in aliases):
            return genre
    return "unknown"


def check_review(text: str, directory: Path, genre: str | None = None,
                 check_artifacts: bool = True) -> Report:
    rep = Report()
    lines = text.splitlines()
    meta, hard = parse_metadata(lines)

    # 1. metadata header
    for f in META_FIELDS:
        if f not in meta or not meta[f]:
            rep.errors.append(f"metadata: missing field '{f}'")
    no_break = [k for k in META_FIELDS[:-1] if k in hard and not hard[k]]
    if no_break:
        rep.warnings.append(
            "metadata: {} lack a hard line break (two trailing spaces); "
            "fields will merge in DOCX/PDF".format(", ".join(no_break)))

    rep.genre = detect_genre(meta.get("review type", ""), genre)
    if rep.genre == "unknown":
        rep.errors.append("metadata: 'Review type' does not match a known genre "
                          "(pass --genre to override)")

    # 2. mandatory sections
    headings = []
    for line in lines:
        m = HEADING_RE.match(line)
        if m:
            headings.append(m.group(2).lower())
    if rep.genre in GENRES:
        for pat in GENRES[rep.genre][1]:
            if not any(re.search(pat, h) for h in headings):
                rep.errors.append("section: no heading matching '{}'".format(pat.replace("|", "' or '")))

    # 3. citations <-> references (offline verify_refs)
    ref_errors: list[str] = []
    if any(re.match(r"references?\b|bibliography|works cited", h) for h in headings):
        vr = _load_verify_refs()
        try:
            body, refs = vr.parse_markdown(text)
            res = vr.check_offline(body, refs)
            ref_errors = list(res.errors)
            rep.errors.extend("references: " + e for e in res.errors)
            rep.warnings.extend("references: " + w for w in res.warnings)
            rep.infos.append(f"references parsed: {len(refs):d}, citation style: {res.style}")
        except vr.ParseError as exc:
            rep.errors.append(f"references: {exc}")

    # 4. artifacts
    if check_artifacts:
        base = re.split(r"\n#{1,6}\s+references?\b", text, maxsplit=1, flags=re.I)[0]
        referenced: set[str] = set()
        for m in re.finditer(r"!?\[[^\]]*\]\(([^)\s]+)\)", base):
            target = m.group(1)
            if not re.match(r"[a-z]+://|#|mailto:", target, re.I):
                referenced.add(target)
        for m in re.finditer(r"`([\w./-]+\.(?:svg|png|csv|md|bib))`", base):
            if Path(m.group(1)).name in ARTIFACT_NAMES:
                referenced.add(m.group(1))
        for target in sorted(referenced):
            if not (directory / target).exists():
                rep.errors.append(f"artifact: '{target}' is referenced but not found")
        for name in REQUIRED_ARTIFACTS.get(rep.genre, ()):
            if not (directory / name).exists():
                rep.errors.append(f"artifact: required file '{name}' is missing next to the review")

    # 5. placeholders and gate consistency
    found = {p.upper() for p in PLACEHOLDER_RE.findall(text)}
    if found:
        rep.errors.append("placeholders left in text: {}".format(", ".join(sorted(found))))

    gate = meta.get("gate", "")
    m = GATE_STATUS_RE.search(gate)
    if gate and not m:
        rep.errors.append("gate: line must start with '✓ passed', '⚠ partial' or '✗ failed'")
    elif m:
        status = m.group(2).lower()
        score = SCORE_RE.search(gate)
        if status == "passed":
            if ref_errors:
                rep.errors.append("gate: marked passed while reference errors exist")
            if score and score.group(1) != score.group(2):
                rep.errors.append("gate: marked passed but checklist is {}/{}".format(*score.groups()))
            if not score and rep.genre in REQUIRED_ARTIFACTS:
                rep.errors.append("gate: passed needs a checklist score (e.g. 'PRISMA 27/27')")
        elif not re.search(r"missing|not met|outstanding|waiver|waived", text.lower()):
            rep.errors.append(f"gate: '{status}' must list what is missing or waived")
    return rep


# JEV priority of work (shared/jev.md): integrity first, polish last.
PRIORITY = (("references", 1), ("artifact", 2), ("section", 2), ("gate", 3),
            ("placeholders", 4), ("metadata", 4))


def ranked_steps(rep: Report) -> list[tuple[int, str]]:
    """Errors and warnings in the order they should be fixed (stable within a priority)."""
    steps = []
    for msg in rep.errors:
        prio = next((p for prefix, p in PRIORITY if msg.startswith(prefix)), 3)
        steps.append((prio, msg))
    steps += [(5, "warning: " + w) for w in rep.warnings]
    return sorted(steps, key=lambda s: s[0])


def render(rep: Report, name: str) -> str:
    out = [f"# Review Check: {name}", "",
           f"**Genre:** {rep.genre}  ",
           f"**Errors:** {len(rep.errors):d}  ",
           f"**Warnings:** {len(rep.warnings):d}", ""]
    steps = ranked_steps(rep)
    if steps:
        out += ["## Next Steps (JEV, Ranked)", "",
                "Fix in this order: integrity first, polish last (see `shared/jev.md`).", ""]
        for i, (prio, msg) in enumerate(steps, 1):
            lead = "**#1 recommended:** " if i == 1 else ""
            out.append(f"{i:d}. {lead}{msg} _(priority {prio:d})_")
        out.append("")
    for title, items in (("Errors", rep.errors), ("Warnings", rep.warnings), ("Info", rep.infos)):
        if items:
            out.append(f"## {title}")
            out.extend(f"- {i}" for i in items)
            out.append("")
    return "\n".join(out)


def selftest() -> None:
    refs = ("## References\n\n1. Smith J. A study of things. *Journal of Tests*, 2020. "
            "doi:10.1000/abc123\n")
    base = ("# T\n\n**Review type:** book review  \n**Reporting standard:** none  \n"
            "**Sources:** the book  \n**Search date:** 2026  \n**Gate:** ✓ passed\n\n---\n\n")
    book = base + ("## Overview\n\nx\n\n## Summary\n\nx\n\n"
                   "## Critical assessment\n\nx\n\n## Verdict\n\nx\n")
    with tempfile.TemporaryDirectory() as d:
        dp = Path(d)
        assert check_review(book, dp).ok, check_review(book, dp).errors
        assert any("verdict" in e for e in check_review(book.replace("## Verdict", "## Notes"), dp).errors)
        assert any("metadata" in e for e in check_review(book.replace("**Gate:** ✓ passed", ""), dp).errors)
        assert any("placeholders" in e for e in check_review(book + "\nTODO\n", dp).errors)
        sysrev = base.replace("book review", "systematic review").replace(
            "✓ passed", "✓ passed (PRISMA 27/27)")
        sysrev += ("## Abstract\n\na\n\n## 1. Introduction\n\na\n\n## 2. Methods\n\na\n\n"
                   "## 3. Results\n\nSee `prisma_flow.svg`.\n\n## 4. Discussion\n\na\n\n" + refs)
        errs = check_review(sysrev, dp).errors
        assert any("prisma_flow.svg" in e for e in errs), errs
        for n in REQUIRED_ARTIFACTS["systematic-review"]:
            (dp / n).write_text("x", encoding="utf-8")
        assert check_review(sysrev, dp).ok, check_review(sysrev, dp).errors
        assert any("27" in e for e in check_review(sysrev.replace("27/27", "20/27"), dp).errors)
    print("check_review selftest OK")


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        with contextlib.suppress(AttributeError, ValueError):
            stream.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description="Validate a review.md against the output spec.")
    p.add_argument("input", nargs="?", help="review.md")
    p.add_argument("--genre", choices=sorted(GENRES), help="override genre detection")
    p.add_argument("--artifacts-dir", type=Path, help="where artifacts live (default: next to the review)")
    p.add_argument("--no-artifacts", action="store_true", help="skip artifact existence checks")
    p.add_argument("--strict", action="store_true", help="treat warnings as failures")
    p.add_argument("--out", type=Path, help="write the Markdown report here")
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args(argv)
    if a.selftest:
        selftest()
        return 0
    if not a.input:
        p.error("provide review.md (or --selftest)")
    path = Path(a.input)
    if not path.is_file():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2
    text = path.read_text(encoding="utf-8-sig")
    rep = check_review(text, a.artifacts_dir or path.parent, a.genre, not a.no_artifacts)
    report = render(rep, path.name)
    if a.out:
        a.out.write_text(report, encoding="utf-8")
        print(f"wrote {a.out}")
    else:
        print(report)
    failed = bool(rep.errors) or (a.strict and bool(rep.warnings))
    print(f'RESULT: {"FAIL" if failed else "PASS"} ({len(rep.errors):d} errors, {len(rep.warnings):d} warnings)')
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
