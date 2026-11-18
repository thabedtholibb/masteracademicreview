"""Deterministic journal-fit scorer for the `journal-match` skill (stdlib only).

Turns a candidate-journal table into a ranked, auditable shortlist. The model
supplies the evidence (scope quotes, verified metrics); this script does the
arithmetic, so the ranking cannot drift between runs.

Input: a CSV/TSV with one row per candidate journal. Required columns:

    journal, scope_fit, article_fit, method_fit, indexing, speed, cost,
    audience, risk

Each score is 0–5 (5 = best). Optional columns:

    issn, publisher, tier, verified, scope_quote, evidence_url, notes

`verified` is a semicolon-separated list of criteria whose value was checked
against a primary source (e.g. "scope_fit;indexing;cost"). Unverified criteria
still count toward the score but lower the row's confidence.

Scoring: weighted mean of the eight 0–5 scores, scaled to 0–100.
Confidence: share of the eight criteria marked verified, as a percentage.
Ranking: score descending, then confidence, then journal name.

CLI:
    python journal_rank.py journals.csv
    python journal_rank.py journals.csv --json shortlist.json
    python journal_rank.py journals.csv --weights scope_fit=40,article_fit=10
    python journal_rank.py --template > journals.csv
    python journal_rank.py --selftest
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _textio import read_text

CRITERIA = (
    "scope_fit",
    "article_fit",
    "method_fit",
    "indexing",
    "speed",
    "cost",
    "audience",
    "risk",
)

DEFAULT_WEIGHTS = {
    "scope_fit": 30,
    "article_fit": 15,
    "method_fit": 15,
    "indexing": 10,
    "speed": 10,
    "cost": 10,
    "audience": 5,
    "risk": 5,
}

LABELS = {
    "scope_fit": "Scope Fit",
    "article_fit": "Article-Type Fit",
    "method_fit": "Method Acceptance",
    "indexing": "Indexing/Quartile",
    "speed": "Decision Speed",
    "cost": "Cost/APC",
    "audience": "Audience/Reach",
    "risk": "Legitimacy/Ethics",
}

TIERS = ("", "reach", "target", "safety")

ANCHOR_SCORES = (0, 1, 3, 5)

# Scoring anchors: what a 5 / 3 / 1 / 0 must look like, so two runs (or two
# people) score the same evidence the same way. 2 and 4 are only allowed as
# "between anchors" and are flagged OFF_ANCHOR.
ANCHORS = {
    "scope_fit": {
        5: "aims & scope name this topic AND this article type (quoted)",
        3: "scope covers the field broadly; topic is plausible but not named",
        1: "only tangential overlap; no scope sentence supports it",
        0: "outside scope",
    },
    "article_fit": {
        5: "published >= 3 reviews of this type in the last 2 years",
        3: "accepts reviews in the author guide but few recent examples",
        1: "reviews only on invitation / exceptional",
        0: "does not publish reviews",
    },
    "method_fit": {
        5: "recent articles use this method at this rigour (named examples)",
        3: "method appears occasionally; reporting expectations unclear",
        1: "method is unusual for the journal; desk-reject risk",
        0: "method explicitly unsuitable",
    },
    "indexing": {
        5: "indexed (Scopus/WoS) and Q1 in the stated metric, verified",
        3: "indexed and Q2, or Q1 in a different metric than stated",
        1: "indexed but Q3/Q4, or indexing only partly verified",
        0: "not indexed / unverified",
    },
    "speed": {
        5: "published first decision <= deadline with margin",
        3: "published times roughly meet the deadline",
        1: "published times exceed the deadline",
        0: "no evidence of decision time",
    },
    "cost": {
        5: "free, or APC fully within budget",
        3: "APC within budget with waiver/discount uncertainty",
        1: "APC at or above budget limit",
        0: "APC far over budget",
    },
    "audience": {
        5: "core readership the author needs",
        3: "adjacent readership",
        1: "weak overlap with intended readers",
        0: "wrong audience",
    },
    "risk": {
        5: "indexed, COPE member, transparent peer review and fees",
        3: "legitimate but one item unverified",
        1: "one or more red flags (opaque fees, vague scope, no board)",
        0: "predatory indicators",
    },
}


class JournalError(Exception):
    pass


def _num(row: dict, key: str, lineno: int) -> float:
    raw = str(row.get(key, "")).strip()
    if raw == "":
        raise JournalError(f"row {lineno}: missing required score '{key}'")
    try:
        value = float(raw)
    except ValueError as exc:
        raise JournalError(f"row {lineno}: '{key}' is not a number ({raw!r})") from exc
    if not 0 <= value <= 5:
        raise JournalError(f"row {lineno}: '{key}' must be between 0 and 5 (got {value})")
    return value


def _verified(row: dict) -> set[str]:
    raw = str(row.get("verified", "") or "")
    parts = [p.strip().lower() for p in raw.replace("|", ";").replace(",", ";").split(";")]
    return {p for p in parts if p}


def score_row(row: dict, weights: dict[str, float], lineno: int = 1,
              require_quote: bool = True, strict_anchors: bool = False) -> dict:
    """Score one journal row. Pure function: no I/O, no globals mutated."""
    scores = {key: _num(row, key, lineno) for key in CRITERIA}
    total_weight = sum(weights.values())
    if total_weight <= 0:
        raise JournalError("weights must sum to a positive number")

    fit = sum(weights[key] * scores[key] / 5.0 for key in CRITERIA) / total_weight * 100.0
    contributions = {
        key: {
            "weight_pct": round(weights[key] / total_weight * 100.0, 1),
            "score": scores[key],
            "points": round(weights[key] * scores[key] / 5.0 / total_weight * 100.0, 2),
            "lost": round(weights[key] * (5 - scores[key]) / 5.0 / total_weight * 100.0, 2),
        }
        for key in CRITERIA
    }
    off_anchor = [k for k in CRITERIA if scores[k] not in ANCHOR_SCORES]
    if strict_anchors and off_anchor:
        raise JournalError(
            f"row {lineno}: scores must be 0/1/3/5 (anchored); off-anchor: "
            + ", ".join(off_anchor))
    quote = str(row.get("scope_quote", "") or "").strip()
    if require_quote and scores["scope_fit"] >= 3 and not quote:
        raise JournalError(
            f"row {lineno}: scope_fit >= 3 requires a scope_quote from the "
            "journal's own aims & scope (or lower the score)")

    verified = _verified(row)
    unknown = verified - set(CRITERIA)
    verified_known = verified & set(CRITERIA)
    confidence = round(100.0 * len(verified_known) / len(CRITERIA), 1)

    flags = []
    if scores["risk"] <= 2:
        flags.append("LEGITIMACY RISK")
    if scores["scope_fit"] <= 2:
        flags.append("SCOPE MISMATCH")
    if scores["article_fit"] <= 2:
        flags.append("ARTICLE-TYPE RISK")
    if scores["method_fit"] <= 2:
        flags.append("METHOD MISMATCH")
    if scores["indexing"] <= 1:
        flags.append("NOT INDEXED / UNVERIFIED")
    if confidence < 50:
        flags.append("LOW EVIDENCE")
    if off_anchor:
        flags.append("OFF_ANCHOR")

    tier = str(row.get("tier", "") or "").strip().lower()
    if tier not in TIERS:
        raise JournalError(f"row {lineno}: tier must be reach/target/safety (got {tier!r})")

    return {
        "journal": str(row.get("journal", "")).strip(),
        "issn": str(row.get("issn", "") or "").strip(),
        "publisher": str(row.get("publisher", "") or "").strip(),
        "tier": tier,
        "scores": scores,
        "fit": round(fit, 1),
        "confidence": confidence,
        "verified": sorted(verified_known),
        "unknown_verified_fields": sorted(unknown),
        "gaps": [key for key in CRITERIA if key not in verified_known],
        "flags": flags,
        "off_anchor": off_anchor,
        "contributions": contributions,
        "scope_quote": str(row.get("scope_quote", "") or "").strip(),
        "evidence_url": str(row.get("evidence_url", "") or "").strip(),
        "notes": str(row.get("notes", "") or "").strip(),
    }


def rank(rows: list[dict], weights: dict[str, float] | None = None,
         require_quote: bool = True, strict_anchors: bool = False) -> list[dict]:
    weights = dict(DEFAULT_WEIGHTS if weights is None else weights)
    scored = [score_row(row, weights, i + 2, require_quote, strict_anchors)
              for i, row in enumerate(rows)]
    missing = [s["journal"] for s in scored if not s["journal"]]
    if missing:
        raise JournalError("every row needs a non-empty 'journal'")
    return sorted(scored, key=lambda s: (-s["fit"], -s["confidence"], s["journal"].lower()))


def _md_cell(text: str) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def rubric_markdown() -> str:
    lines = ["# Scoring Anchors", "",
             "Score only 5 / 3 / 1 / 0 against these descriptions; 2 and 4 are "
             "flagged OFF_ANCHOR (use `--strict-anchors` to forbid them).", ""]
    for key in CRITERIA:
        lines.append(f"## {LABELS[key]} (`{key}`)")
        for s in (5, 3, 1, 0):
            lines.append(f"- **{s}:** {ANCHORS[key][s]}")
        lines.append("")
    return "\n".join(lines)


def to_markdown(scored: list[dict], weights: dict[str, float], source: str = "",
                explain: bool = False) -> str:
    total_weight = sum(weights.values())
    weight_line = " · ".join(
        f"{LABELS[k]} {weights[k] / total_weight * 100:.0f}%" for k in CRITERIA
    )
    lines = [
        "# Journal Shortlist: Ranked (#1 Recommended)",
        "",
        "**Decision record (JEV).** "
        f"{len(scored)} candidate journal(s) scored on eight criteria"
        + (f" from `{source}`" if source else "")
        + ".",
        "",
        f"**Weights:** {weight_line}.",
        "",
        "**Scoring:** weighted mean of the 0–5 scores, scaled to 0–100. "
        "**Confidence:** share of the eight criteria whose value is marked verified.",
        "",
        "| # | Journal | Fit | Confidence | Tier | Flags | Evidence Gaps |",
        "|---|---|---:|---:|---|---|---|",
    ]
    for i, row in enumerate(scored, 1):
        tier = row["tier"] or "n/a"
        flags = ", ".join(row["flags"]) or "none"
        gaps = ", ".join(row["gaps"]) or "none"
        lines.append(
            f"| {i} | {_md_cell(row['journal'])} | {row['fit']:.1f} | "
            f"{row['confidence']:.0f}% | {tier} | {_md_cell(flags)} | {_md_cell(gaps)} |"
        )

    lines += ["", "## Evidence Detail", ""]
    for i, row in enumerate(scored, 1):
        head = f"### #{i} {row['journal']}: {row['fit']:.1f}/100, Confidence {row['confidence']:.0f}%"
        lines.append(head)
        meta = []
        if row["tier"]:
            meta.append(f"tier: **{row['tier']}**")
        if row["issn"]:
            meta.append(f"ISSN {row['issn']}")
        if row["publisher"]:
            meta.append(row["publisher"])
        if meta:
            lines.append("- " + " · ".join(meta))
        if row["scope_quote"]:
            lines.append(f"- Scope quote: “{row['scope_quote']}”")
        if row["evidence_url"]:
            lines.append(f"- Evidence: {row['evidence_url']}")
        lines.append("- Verified: " + (", ".join(row["verified"]) or "**none**"))
        if row["gaps"]:
            lines.append("- Unverified (do not state as fact): " + ", ".join(row["gaps"]))
        if row["unknown_verified_fields"]:
            lines.append("- Ignored `verified` fields: " + ", ".join(row["unknown_verified_fields"]))
        if row["flags"]:
            lines.append("- Flags: " + ", ".join(row["flags"]))
        if row["notes"]:
            lines.append(f"- Notes: {row['notes']}")
        if explain:
            lines += ["", "| Criterion | Weight | Score | Points | Lost |",
                      "|---|---:|---:|---:|---:|"]
            for key in CRITERIA:
                c = row["contributions"][key]
                lines.append(f"| {LABELS[key]} | {c['weight_pct']:.0f}% | {c['score']:g}/5 | "
                             f"{c['points']:.1f} | {c['lost']:.1f} |")
            biggest = max(CRITERIA, key=lambda k: row["contributions"][k]["lost"])
            lines.append("")
            lines.append(f"- Largest loss: **{LABELS[biggest]}** "
                         f"(-{row['contributions'][biggest]['lost']:.1f} points)")
        lines.append("")

    lines += [
        "---",
        "",
        "**Next step:** the skill assigns `reach / target / safety` tiers with the author, "
        "writes the submission cascade, and verifies every gap before submission. "
        "A score is not an acceptance probability.",
        "",
    ]
    return "\n".join(lines)


def _read_table(path: Path) -> list[dict]:
    delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
    try:
        with io.StringIO(read_text(path), newline="") as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            if not reader.fieldnames:
                raise JournalError("file has no header row")
            required = {"journal", *CRITERIA}
            missing = required - {name.strip() for name in reader.fieldnames if name}
            if missing:
                raise JournalError("missing required columns: " + ", ".join(sorted(missing)))
            return [
                row for row in reader
                if any((value or "").strip() for value in row.values() if value is not None)
            ]
    except FileNotFoundError as exc:
        raise JournalError(f"file not found: {path}") from exc


def _parse_weights(raw: str | None) -> dict[str, float]:
    weights = dict(DEFAULT_WEIGHTS)
    if not raw:
        return weights
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        if "=" not in part:
            raise JournalError(f"bad weight {part!r}; expected criterion=number")
        key, value = part.split("=", 1)
        key = key.strip()
        if key not in CRITERIA:
            raise JournalError(f"unknown criterion {key!r}; choose from {', '.join(CRITERIA)}")
        try:
            weights[key] = float(value)
        except ValueError as exc:
            raise JournalError(f"weight for {key} is not a number") from exc
        if weights[key] < 0:
            raise JournalError(f"weight for {key} cannot be negative")
    if sum(weights.values()) <= 0:
        raise JournalError("weights must sum to a positive number")
    return weights


def _template() -> str:
    header = ["journal", "issn", "publisher", "tier", *CRITERIA,
              "verified", "scope_quote", "evidence_url", "notes"]
    return ",".join(header)


def _selftest() -> None:
    weights = dict(DEFAULT_WEIGHTS)
    assert sum(weights.values()) == 100, "default weights must sum to 100"

    base = {key: "5" for key in CRITERIA}
    base["scope_quote"] = "aims and scope sentence"
    perfect = score_row({**base, "journal": "Perfect", "verified": ";".join(CRITERIA)}, weights)
    assert perfect["fit"] == 100.0, perfect["fit"]
    assert perfect["confidence"] == 100.0
    assert perfect["flags"] == [], perfect["flags"]

    zero = score_row({**{k: "0" for k in CRITERIA}, "journal": "Zero"}, weights)
    assert zero["fit"] == 0.0
    assert zero["confidence"] == 0.0

    risky = score_row({**base, "journal": "Risky", "risk": "1"}, weights)
    assert "LEGITIMACY RISK" in risky["flags"]

    dim = score_row({**base, "journal": "Dim", "scope_fit": "2"}, weights)
    assert "SCOPE MISMATCH" in dim["flags"]

    rows = [
        {**base, "journal": "A", "verified": ";".join(CRITERIA)},
        {**{k: "4" for k in CRITERIA}, "journal": "B", "verified": "scope_fit;indexing", "scope_quote": "q"},
        {**{k: "3" for k in CRITERIA}, "journal": "C", "scope_quote": "q"},
    ]
    ranked = rank(rows, weights)
    assert [r["journal"] for r in ranked] == ["A", "B", "C"], [r["journal"] for r in ranked]
    assert ranked[1]["confidence"] == 25.0, ranked[1]["confidence"]

    try:
        score_row({**base, "journal": "Bad", "scope_fit": "9"}, weights)
    except JournalError:
        pass
    else:
        raise AssertionError("out-of-range score must fail")

    # Anchors, scope_quote rule and explain breakdown.
    assert set(ANCHORS) == set(CRITERIA)
    assert all(set(v) == {0, 1, 3, 5} for v in ANCHORS.values())
    mid = score_row({**base, "journal": "Mid", "scope_fit": "4"}, weights)
    assert "OFF_ANCHOR" in mid["flags"], mid["flags"]
    noq = {k: v for k, v in base.items() if k != "scope_quote"}
    try:
        score_row({**noq, "journal": "NoQ"}, weights)
    except JournalError:
        pass
    else:
        raise AssertionError("scope_fit >= 3 without scope_quote must fail")
    assert score_row({**noq, "journal": "NoQ"}, weights, require_quote=False)["fit"] == 100.0
    total = sum(c["points"] for c in mid["contributions"].values())
    assert abs(total - mid["fit"]) < 0.1, (total, mid["fit"])
    assert "Largest loss" in to_markdown([mid], weights, explain=True)

    # Markdown must render without raising and must contain the recommendation.
    md = to_markdown(ranked, weights, "selftest")
    assert "#1 Recommended" in md and "A" in md

    print("journal_rank selftest OK (weights, scoring, confidence, flags, ranking, validation)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Rank candidate journals deterministically.")
    parser.add_argument("csv", nargs="?", help="candidate CSV/TSV")
    parser.add_argument("--weights", help="criterion=number,... (merged with defaults)")
    parser.add_argument("--json", dest="json_out", help="write the scored table as JSON")
    parser.add_argument("--out", help="write the Markdown shortlist to a file")
    parser.add_argument("--explain", action="store_true", help="per-criterion points contributed and lost")
    parser.add_argument("--rubric", action="store_true", help="print the 5/3/1/0 scoring anchors and exit")
    parser.add_argument("--strict-anchors", action="store_true", help="reject scores other than 0/1/3/5")
    parser.add_argument("--allow-missing-quote", action="store_true",
                        help="do not require scope_quote when scope_fit >= 3")
    parser.add_argument("--template", action="store_true", help="print the CSV header and exit")
    parser.add_argument("--selftest", action="store_true", help="run internal checks and exit")
    args = parser.parse_args(argv)

    if args.selftest:
        _selftest()
        return 0
    if args.template:
        print(_template())
        return 0
    if args.rubric:
        print(rubric_markdown())
        return 0
    if not args.csv:
        parser.error("provide a CSV file (or --template / --selftest)")

    try:
        weights = _parse_weights(args.weights)
        rows = _read_table(Path(args.csv))
        if not rows:
            raise JournalError("the file has no data rows")
        scored = rank(rows, weights, not args.allow_missing_quote, args.strict_anchors)
    except JournalError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    markdown = to_markdown(scored, weights, Path(args.csv).name, args.explain)
    if args.out:
        Path(args.out).write_text(markdown, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(markdown)

    if args.json_out:
        payload = {
            "weights": {k: weights[k] / sum(weights.values()) * 100 for k in CRITERIA},
            "candidates": scored,
        }
        Path(args.json_out).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"wrote {args.json_out}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
