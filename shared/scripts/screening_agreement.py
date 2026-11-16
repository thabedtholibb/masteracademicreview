#!/usr/bin/env python3
"""Inter-rater agreement for dual screening (Cohen's kappa + PABAK).

Reads a screening log with one row per record and two reviewers' decisions:

    record_id,stage,reviewer1,reviewer2
    R001,title_abstract,include,include
    R002,title_abstract,include,exclude
    ...

Accepted decisions: include/included/i/1/yes/y/true/in and
exclude/excluded/e/0/no/n/false/out.

Outputs observed agreement, Cohen's kappa, the prevalence-adjusted and
bias-adjusted kappa (PABAK), the prevalence index and the bias index, overall
and per screening stage. Disagreements can be exported for adjudication.

Stdlib only. Exit codes: 0 = agreement meets the threshold (or no threshold
was set), 1 = below threshold, 2 = invalid input.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

INCLUDE = {"include", "included", "i", "1", "yes", "y", "true", "in"}
EXCLUDE = {"exclude", "excluded", "e", "0", "no", "n", "false", "out"}


class AgreementError(Exception):
    pass


@dataclass
class Pair:
    stage: str
    record_id: str
    left: bool  # True = include
    right: bool


@dataclass
class Stats:
    stage: str
    n: int
    both_include: int
    left_only: int
    right_only: int
    both_exclude: int
    agreement: float
    kappa: float | None
    pabak: float
    prevalence_index: float
    bias_index: float

    @property
    def interpretation(self) -> str:
        if self.kappa is None:
            return "undefined (no variance)"
        value = self.kappa
        if value < 0:
            return "poor"
        if value <= 0.20:
            return "slight"
        if value <= 0.40:
            return "fair"
        if value <= 0.60:
            return "moderate"
        if value <= 0.80:
            return "substantial"
        return "almost perfect"


def normalize_decision(value: str, row: int) -> bool:
    token = (value or "").strip().lower()
    if token in INCLUDE:
        return True
    if token in EXCLUDE:
        return False
    raise AgreementError(
        f"row {row}: unrecognised decision {value!r}; use include/exclude (or 1/0)"
    )


def compute(pairs: list[Pair], stage: str) -> Stats:
    n = len(pairs)
    if n == 0:
        raise AgreementError(f"stage {stage!r}: no records")
    both_include = sum(1 for p in pairs if p.left and p.right)
    left_only = sum(1 for p in pairs if p.left and not p.right)
    right_only = sum(1 for p in pairs if not p.left and p.right)
    both_exclude = n - both_include - left_only - right_only

    agreement = (both_include + both_exclude) / n
    expected = (
        (both_include + left_only) * (both_include + right_only)
        + (right_only + both_exclude) * (left_only + both_exclude)
    ) / (n * n)
    if expected >= 1:
        kappa = None  # both reviewers used a single category: no variance
    else:
        kappa = (agreement - expected) / (1 - expected)
    pabak = 2 * agreement - 1
    prevalence_index = abs(both_include - both_exclude) / n
    bias_index = abs(left_only - right_only) / n

    return Stats(
        stage=stage,
        n=n,
        both_include=both_include,
        left_only=left_only,
        right_only=right_only,
        both_exclude=both_exclude,
        agreement=round(agreement, 4),
        kappa=round(kappa, 4) if kappa is not None else None,
        pabak=round(pabak, 4),
        prevalence_index=round(prevalence_index, 4),
        bias_index=round(bias_index, 4),
    )


def summarize(pairs: list[Pair]) -> tuple[Stats, list[Stats]]:
    overall = compute(pairs, "overall")
    stages = list(dict.fromkeys(p.stage for p in pairs))
    per_stage = [compute([p for p in pairs if p.stage == stage], stage) for stage in stages]
    return overall, per_stage


def load_rows(path: Path, delimiter: str | None) -> tuple[list[dict], set[str]]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except FileNotFoundError as exc:
        raise AgreementError(f"file not found: {path}") from exc

    lines = text.splitlines()
    sample = lines[0] if lines else ""
    if delimiter:
        chosen = delimiter
    else:
        try:
            chosen = csv.Sniffer().sniff(sample, delimiters=",;\t").delimiter
        except csv.Error:
            chosen = ","

    reader = csv.DictReader(lines, delimiter=chosen)
    if not reader.fieldnames:
        raise AgreementError("the file has no header row")
    fields = {name.strip() for name in reader.fieldnames if name}
    rows = [
        {key.strip(): (value or "").strip() for key, value in row.items() if key}
        for row in reader
        if any((value or "").strip() for value in row.values() if value is not None)
    ]
    return rows, fields


def resolve_id_col(id_col: str, fields: set[str]) -> str:
    if id_col in fields:
        return id_col
    for candidate in ("record_id", "id", "study_id"):
        if candidate in fields:
            return candidate
    raise AgreementError(f"missing ID column; found: {', '.join(sorted(fields))}")


def read_pairs(
    path: Path,
    id_col: str,
    reviewers: tuple[str, str],
    stage_col: str,
    delimiter: str | None,
) -> list[Pair]:
    rows, fields = load_rows(path, delimiter)
    left_col, right_col = reviewers
    id_col = resolve_id_col(id_col, fields)
    if left_col not in fields or right_col not in fields:
        raise AgreementError(
            f"missing reviewer columns {left_col!r}/{right_col!r}; found: {', '.join(sorted(fields))}"
        )
    has_stage = stage_col in fields

    pairs: list[Pair] = []
    seen: set[tuple[str, str]] = set()
    for row_number, row in enumerate(rows, 2):
        record_id = row.get(id_col, "").strip()
        if not record_id:
            raise AgreementError(f"row {row_number}: empty {id_col}")
        stage = (row.get(stage_col) or "all").strip() if has_stage else "all"
        key = (stage, record_id)
        if key in seen:
            raise AgreementError(f"row {row_number}: duplicate record {record_id!r} in stage {stage!r}")
        seen.add(key)
        pairs.append(
            Pair(
                stage=stage or "all",
                record_id=record_id,
                left=normalize_decision(row.get(left_col, ""), row_number),
                right=normalize_decision(row.get(right_col, ""), row_number),
            )
        )
    if not pairs:
        raise AgreementError("the file has no data rows")
    return pairs


def read_long_pairs(
    path: Path,
    id_col: str,
    reviewers: tuple[str, str],
    stage_col: str,
    reviewer_col: str,
    decision_col: str,
    delimiter: str | None,
) -> list[Pair]:
    """Pivot a long screening log (one row per record-reviewer) into pairs."""
    rows, fields = load_rows(path, delimiter)
    id_col = resolve_id_col(id_col, fields)
    missing = [name for name in (reviewer_col, decision_col) if name not in fields]
    if missing:
        raise AgreementError(
            f"missing long-format column(s): {', '.join(missing)}; "
            f"found: {', '.join(sorted(fields))}"
        )
    has_stage = stage_col in fields
    left_id, right_id = reviewers

    grouped: dict[tuple[str, str], dict[str, bool]] = {}
    order: list[tuple[str, str]] = []
    for row_number, row in enumerate(rows, 2):
        record_id = row.get(id_col, "").strip()
        if not record_id:
            raise AgreementError(f"row {row_number}: empty {id_col}")
        stage = (row.get(stage_col) or "all").strip() if has_stage else "all"
        stage = stage or "all"
        reviewer = row.get(reviewer_col, "").strip()
        if not reviewer:
            raise AgreementError(f"row {row_number}: empty {reviewer_col}")
        key = (stage, record_id)
        if key not in grouped:
            grouped[key] = {}
            order.append(key)
        if reviewer in grouped[key]:
            raise AgreementError(
                f"row {row_number}: duplicate decision by {reviewer!r} "
                f"for {record_id!r} in stage {stage!r}"
            )
        grouped[key][reviewer] = normalize_decision(row.get(decision_col, ""), row_number)

    pairs: list[Pair] = []
    for stage, record_id in order:
        decisions = grouped[(stage, record_id)]
        absent = [name for name in (left_id, right_id) if name not in decisions]
        if absent:
            raise AgreementError(
                f"record {record_id!r} in stage {stage!r}: no decision from {', '.join(absent)}"
            )
        extra = [name for name in decisions if name not in (left_id, right_id)]
        if extra:
            raise AgreementError(
                f"record {record_id!r} in stage {stage!r}: unexpected reviewer(s) {', '.join(extra)}"
            )
        pairs.append(
            Pair(
                stage=stage,
                record_id=record_id,
                left=decisions[left_id],
                right=decisions[right_id],
            )
        )
    if not pairs:
        raise AgreementError("the file has no data rows")
    return pairs


def render(stats: Stats, per_stage: list[Stats], pairs: list[Pair], source: str) -> str:
    lines = [
        "# Screening Agreement Report",
        "",
        f"**Source:** `{source}`  ",
        f"**Records:** {stats.n}  ",
        f"**Overall agreement:** {stats.agreement * 100:.1f}%  ",
        f"**Cohen's kappa:** {stats.kappa if stats.kappa is not None else 'undefined'} "
        f"({stats.interpretation})  ",
        f"**PABAK:** {stats.pabak:.3f}",
        "",
        "| Stage | N | Both Include | R1 Only | R2 Only | Both Exclude | Agreement | Kappa | PABAK |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in per_stage:
        kappa = f"{item.kappa:.3f}" if item.kappa is not None else "n/a"
        lines.append(
            f"| {item.stage} | {item.n} | {item.both_include} | {item.left_only} | "
            f"{item.right_only} | {item.both_exclude} | {item.agreement * 100:.1f}% | "
            f"{kappa} | {item.pabak:.3f} |"
        )
    lines += [
        "",
        "Interpretation (Landis & Koch, 1977): <0 poor, 0-0.20 slight, 0.21-0.40 fair, "
        "0.41-0.60 moderate, 0.61-0.80 substantial, 0.81-1.00 almost perfect.",
        "",
        f"Prevalence index: {stats.prevalence_index:.3f}; bias index: {stats.bias_index:.3f}. "
        "PABAK is reported because kappa falls when one decision dominates (high prevalence).",
        "",
    ]

    disagreements = [p for p in pairs if p.left != p.right]
    lines += [f"## Disagreements ({len(disagreements)})", ""]
    if disagreements:
        lines += ["| Record | Stage | Reviewer 1 | Reviewer 2 |", "|---|---|---|---|"]
        for pair in disagreements[:200]:
            lines.append(
                f"| {pair.record_id} | {pair.stage} | "
                f"{'include' if pair.left else 'exclude'} | "
                f"{'include' if pair.right else 'exclude'} |"
            )
        if len(disagreements) > 200:
            lines.append(f"| ... | | | ({len(disagreements) - 200} more) |")
        lines += ["", "Adjudicate every disagreement; never default to include."]
    else:
        lines.append("No disagreements.")
    lines += [
        "",
        "---",
        "",
        "**Gate:** report agreement for each dual-screened stage and resolve every "
        "disagreement before the PRISMA counts are final.",
        "",
    ]
    return "\n".join(lines)


def write_disagreements(path: Path, pairs: list[Pair]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["record_id", "stage", "reviewer1", "reviewer2"])
        for pair in pairs:
            if pair.left != pair.right:
                writer.writerow(
                    [
                        pair.record_id,
                        pair.stage,
                        "include" if pair.left else "exclude",
                        "include" if pair.right else "exclude",
                    ]
                )


def selftest() -> None:
    pairs = (
        [Pair("title_abstract", f"A{i}", True, True) for i in range(10)]
        + [Pair("title_abstract", f"B{i}", True, False) for i in range(2)]
        + [Pair("title_abstract", f"C{i}", False, True) for i in range(1)]
        + [Pair("title_abstract", f"D{i}", False, False) for i in range(7)]
    )
    stats = compute(pairs, "title_abstract")
    assert stats.n == 20
    assert stats.agreement == 0.85, stats.agreement
    assert abs(stats.kappa - 0.6939) < 0.001, stats.kappa
    assert stats.pabak == 0.70, stats.pabak
    assert stats.prevalence_index == 0.15, stats.prevalence_index
    assert stats.bias_index == 0.05, stats.bias_index
    assert stats.interpretation == "substantial", stats.interpretation

    assert normalize_decision("Include", 1) is True
    assert normalize_decision("0", 1) is False

    overall, per_stage = summarize(
        [*pairs, Pair("full_text", "E1", True, True), Pair("full_text", "E2", False, False)]
    )
    assert overall.n == 22
    assert len(per_stage) == 2 and per_stage[1].stage == "full_text"

    # One-category data: kappa is undefined, PABAK is 1.
    uniform = compute([Pair("s", "x", True, True), Pair("s", "y", True, True)], "s")
    assert uniform.kappa is None and uniform.pabak == 1.0

    try:
        normalize_decision("maybe", 3)
    except AgreementError:
        pass
    else:
        raise AssertionError("unknown decision must fail")

    # Long format: one row per record-reviewer, pivoted into pairs.
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "long.csv"
        path.write_text(
            "record_id,stage,reviewer,decision\n"
            "A,title_abstract,alice,include\n"
            "A,title_abstract,bob,include\n"
            "B,title_abstract,alice,include\n"
            "B,title_abstract,bob,exclude\n",
            encoding="utf-8",
        )
        long_pairs = read_long_pairs(
            path, "record_id", ("alice", "bob"), "stage", "reviewer", "decision", None
        )
        assert len(long_pairs) == 2, long_pairs
        assert long_pairs[0].left and long_pairs[0].right
        assert long_pairs[1].left and not long_pairs[1].right

    print(
        "screening_agreement selftest OK "
        "(kappa, PABAK, indices, stages, long format, validation)"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Cohen's kappa and PABAK for dual screening.")
    parser.add_argument("csv", nargs="?", help="screening log CSV/TSV")
    parser.add_argument("--id-col", default="record_id")
    parser.add_argument(
        "--reviewers",
        help="wide: two column names (default reviewer1,reviewer2); long: two reviewer IDs",
    )
    parser.add_argument("--stage-col", default="stage")
    parser.add_argument("--long", action="store_true", help="long log: one row per record-reviewer")
    parser.add_argument("--reviewer-col", default="reviewer", help="long format: reviewer column")
    parser.add_argument("--decision-col", default="decision", help="long format: decision column")
    parser.add_argument("--delimiter", help="override delimiter (default: auto)")
    parser.add_argument("--min-kappa", type=float, help="fail if overall kappa is below this")
    parser.add_argument("--out", type=Path, help="write the Markdown report")
    parser.add_argument("--json", dest="json_out", type=Path, help="write statistics as JSON")
    parser.add_argument("--disagreements", type=Path, help="write disagreements to CSV")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)

    if args.selftest:
        selftest()
        return 0
    if not args.csv:
        parser.error("provide a screening CSV (or --selftest)")

    if args.long and not args.reviewers:
        print(
            "error: --long requires --reviewers with the two reviewer IDs, e.g. --reviewers alice,bob",
            file=sys.stderr,
        )
        return 2
    raw_reviewers = args.reviewers or "reviewer1,reviewer2"
    reviewers = tuple(part.strip() for part in raw_reviewers.split(","))
    if len(reviewers) != 2 or not all(reviewers):
        print("error: --reviewers must name exactly two columns or reviewer IDs", file=sys.stderr)
        return 2

    try:
        if args.long:
            pairs = read_long_pairs(
                Path(args.csv),
                args.id_col,
                (reviewers[0], reviewers[1]),
                args.stage_col,
                args.reviewer_col,
                args.decision_col,
                args.delimiter,
            )
        else:
            pairs = read_pairs(
                Path(args.csv),
                args.id_col,
                (reviewers[0], reviewers[1]),
                args.stage_col,
                args.delimiter,
            )
        overall, per_stage = summarize(pairs)
    except AgreementError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    report = render(overall, per_stage, pairs, Path(args.csv).name)
    if args.out:
        args.out.write_text(report, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(report)

    if args.json_out:
        payload = {
            "overall": overall.__dict__,
            "per_stage": [item.__dict__ for item in per_stage],
        }
        args.json_out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"wrote {args.json_out}")
    if args.disagreements:
        write_disagreements(args.disagreements, pairs)
        print(f"wrote {args.disagreements}")

    if args.min_kappa is not None:
        if overall.kappa is None:
            print("RESULT: FAIL (kappa undefined; both reviewers used one category)", file=sys.stderr)
            return 1
        if overall.kappa < args.min_kappa:
            print(
                f"RESULT: FAIL (kappa {overall.kappa:.3f} < {args.min_kappa:.3f})",
                file=sys.stderr,
            )
            return 1
        for item in per_stage:
            if item.n >= 2 and item.kappa is not None and item.kappa < args.min_kappa:
                print(
                    f"RESULT: FAIL (stage {item.stage}: kappa {item.kappa:.3f} "
                    f"< {args.min_kappa:.3f})",
                    file=sys.stderr,
                )
                return 1
    print(
        f"RESULT: PASS (n={overall.n}, agreement={overall.agreement * 100:.1f}%, "
        f"kappa={'undefined' if overall.kappa is None else f'{overall.kappa:.3f}'}, "
        f"PABAK={overall.pabak:.3f})",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
