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
import contextlib
import importlib.util
import re
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _textio import read_text

HERE = Path(__file__).resolve().parent

IMRAD = ("abstract", "introduction", "methods", "results|findings",
         "discussion", "references")

# genre key -> (names found in "Review type", English and Indonesian; required heading patterns)
GENRES: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "systematic-review": (("systematic review", "systematic literature review", "tinjauan sistematis",
                           "tinjauan pustaka sistematis", "kajian sistematis"), IMRAD),
    "meta-analysis": (("meta-analysis", "meta analysis", "meta-analisis", "meta analisis"), IMRAD),
    "scoping-review": (("scoping", "pemetaan literatur", "tinjauan lingkup"), IMRAD),
    "umbrella-review": (("umbrella", "overview of reviews", "review of reviews"), IMRAD),
    "meta-synthesis": (("meta-synthesis", "meta synthesis", "meta-ethnography", "meta-etnografi",
                        "qualitative synthesis", "qualitative evidence synthesis",
                        "sintesis kualitatif"), IMRAD),
    "rapid-review": (("rapid", "tinjauan cepat"), IMRAD),
    "integrative-review": (("integrative", "tinjauan integratif"), IMRAD),
    "mapping-review": (("mapping review", "systematic map", "evidence map", "gap map",
                        "peta bukti", "tinjauan pemetaan"), IMRAD),
    "bibliometric-review": (("bibliometric", "bibliometrik"), IMRAD),
    "realist-review": (("realist",), IMRAD),
    "narrative-review": (
        ("narrative", "literature review", "state of the art", "tinjauan naratif",
         "tinjauan pustaka", "kajian pustaka", "kajian literatur"),
        ("introduction", "thematic|theme", "contradiction|gap|gaps",
         "conclusion", "references"),
    ),
    "critical-review": (
        ("critical review", "tinjauan kritis", "kajian kritis"),
        ("thesis", "debate", "critique", "alternative", "implications",
         "references"),
    ),
    "book-review": (
        ("book review", "resensi", "ulasan buku"),
        ("overview", "summary", "assessment|critical", "verdict"),
    ),
}

# Detection order: most specific first, because titles combine genres
# ("Systematic review and meta-analysis" is a meta-analysis; "Rapid systematic
# review" is a rapid review; "Systematic mapping review" is a mapping review;
# a "systematic literature review" is not a narrative one).
DETECT_ORDER = (
    "mapping-review", "scoping-review", "rapid-review", "umbrella-review", "meta-analysis",
    "meta-synthesis", "realist-review", "integrative-review", "bibliometric-review",
    "systematic-review", "critical-review", "book-review", "narrative-review",
)

# Header labels in Indonesian map to the English field names the checks use.
FIELD_ALIASES = {
    "jenis review": "review type", "jenis tinjauan": "review type", "tipe review": "review type",
    "jenis artikel": "review type",
    "standar pelaporan": "reporting standard", "pedoman pelaporan": "reporting standard",
    "sumber": "sources", "sumber data": "sources", "basis data": "sources", "database": "sources",
    "tanggal pencarian": "search date", "tanggal pencarian terakhir": "search date",
    "tanggal penelusuran": "search date", "tgl pencarian": "search date",
    "status gate": "gate", "gerbang": "gate",
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
# A placeholder is something an author has to fill in, not a word that may appear in prose.
# Bracketed markers (including the ones this suite's own tools write), a "TODO:"-style
# note, a marker alone on its line, and filler text. Code blocks are ignored.
PLACEHOLDER_RE = re.compile(
    r"\[\s*citation needed\s*\]"
    r"|\[\s*(?:TO COMPLETE|LENGKAPI|TODO|TBD|FIXME|XXX)\b[^\]]*\]"
    r"|\b(?:TODO|FIXME)\s*:"
    r"|^\s*(?:TODO|TBD|XXX|FIXME)\s*$"
    r"|lorem ipsum",
    re.I | re.M)
CODE_RE = re.compile(r"```.*?```|`[^`\n]*`", re.S)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
# status word, optionally preceded by a symbol or checkbox; Indonesian words accepted
GATE_STATUS_RE = re.compile(
    r"(?:^|[\s(\[])(?:[✓✔✗✘⚠]|\[[xX ]\])?\s*(pass(?:ed)?|partial|fail(?:ed)?|lulus|sebagian|gagal)\b",
    re.I)
GATE_CANON = {"pass": "passed", "passed": "passed", "lulus": "passed", "partial": "partial",
              "sebagian": "partial", "fail": "failed", "failed": "failed", "gagal": "failed"}
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
            key = FIELD_ALIASES.get(key, key)
            meta[key] = m.group(2).strip()
            hard_break[key] = raw.endswith("  ") or raw.rstrip().endswith("\\")
    return meta, hard_break


def detect_genre(review_type: str, override: str | None) -> str:
    """Genre from the 'Review type' line, most specific name first (see DETECT_ORDER)."""
    if override:
        return override
    rt = re.sub(r"\s+", " ", review_type.lower())
    for genre in DETECT_ORDER:
        names = GENRES[genre][0]
        if any(name in rt for name in names) or (genre == "systematic-review" and re.search(r"\bslr\b", rt)):
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
    prose = CODE_RE.sub(" ", text)
    found = sorted({" ".join(m.group(0).split()).lower()[:40] for m in PLACEHOLDER_RE.finditer(prose)})
    if found:
        rep.errors.append("placeholders left in text: {}".format("; ".join(found)))

    gate = meta.get("gate", "")
    m = GATE_STATUS_RE.search(gate)
    if gate and not m:
        rep.errors.append("gate: write a status: 'passed', 'partial' or 'failed' "
                          "(a leading ✓ ⚠ ✗ is optional; lulus, sebagian, gagal also work)")
    elif m:
        status = GATE_CANON[m.group(1).lower()]
        score = SCORE_RE.search(gate)
        if status == "passed":
            if ref_errors:
                rep.errors.append("gate: marked passed while reference errors exist")
            if score and score.group(1) != score.group(2):
                rep.errors.append("gate: marked passed but checklist is {}/{}".format(*score.groups()))
            if not score and rep.genre in REQUIRED_ARTIFACTS:
                rep.errors.append("gate: passed needs a checklist score (e.g. 'PRISMA 27/27')")
        elif not re.search(r"missing|not met|outstanding|waiver|waived|belum|kurang|tidak terpenuhi|dikecualikan",
                           text.lower()):
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

        # Regressions found by auditing realistic titles, labels and prose.
        wanted = {
            "Systematic review and meta-analysis": "meta-analysis",
            "Systematic Review And Meta-Analysis": "meta-analysis",
            "Rapid systematic review": "rapid-review",
            "Systematic mapping review": "mapping-review",
            "Systematic literature review": "systematic-review",
            "Narrative literature review": "narrative-review",
            "Literature review": "narrative-review",
            "Tinjauan sistematis": "systematic-review",
            "Tinjauan pustaka": "narrative-review",
            "Evidence and gap map": "mapping-review",
            "Scoping Review (PRISMA-ScR)": "scoping-review",
            "Overview of reviews": "umbrella-review",
            "Qualitative evidence synthesis (meta-synthesis)": "meta-synthesis",
            "Resensi buku": "book-review",
            "Critical review": "critical-review",
            "Something else entirely": "unknown",
        }
        for title, genre in wanted.items():
            assert detect_genre(title, None) == genre, (title, detect_genre(title, None), genre)

        for gate in ("passed", "PASSED", "[x] passed", "✓ passed", "Lulus", "pass"):
            assert check_review(book.replace("✓ passed", gate), dp).ok, gate
        assert any("gate" in e for e in check_review(book.replace("✓ passed", "maybe"), dp).errors)
        indonesian = (book.replace("**Review type:**", "**Jenis review:**")
                      .replace("**Reporting standard:**", "**Standar pelaporan:**")
                      .replace("**Sources:**", "**Sumber:**").replace("**Search date:**", "**Tanggal pencarian:**"))
        assert check_review(indonesian, dp).ok, check_review(indonesian, dp).errors

        for prose in ("The TODO app study (Lee, 2020) tested it.", "Tools for todo lists.",
                      "A TBD protocol is described by Lee.", "```\nTODO\n```", "Use `XXX` as a marker."):
            assert check_review(book + "\n" + prose + "\n", dp).ok, prose
        for marker in ("[TO COMPLETE: funding]", "[LENGKAPI: pendanaan]", "[citation needed]",
                       "TODO: add figure", "\nTBD\n", "lorem ipsum"):
            assert any("placeholders" in e for e in check_review(book + "\n" + marker + "\n", dp).errors), marker
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
    text = read_text(path)
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
