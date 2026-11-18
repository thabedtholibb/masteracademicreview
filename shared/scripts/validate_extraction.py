#!/usr/bin/env python3
"""Validate an extraction table before synthesis or meta-analysis.

Two profiles:

- ``meta`` (default): requires ``study,effect,variance``. Checks numeric and
  finite effects, strictly positive variances, optional sample sizes and years,
  confidence-interval consistency, duplicate study/outcome keys, and warns when
  there are too few studies to pool (k < 2) or to test small-study effects
  (k < 10, where Egger's test is underpowered).
- ``generic``: checks that the required columns exist and are non-empty, and
  optionally that a key column is unique. Use it for ``characteristics.csv`` or
  any custom extraction sheet.

Stdlib only. Exit codes: 0 = pass, 1 = data errors (or warnings with --strict),
2 = schema/usage error.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _textio import read_text


class ExtractionError(Exception):
    pass


@dataclass
class Report:
    profile: str
    rows: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def read_table(path: Path, delimiter: str | None = None) -> tuple[list[dict], list[str]]:
    try:
        text = read_text(path)
    except FileNotFoundError as exc:
        raise ExtractionError(f"file not found: {path}") from exc
    lines = text.splitlines()
    if not lines:
        raise ExtractionError("the file is empty")
    if delimiter is None:
        try:
            delimiter = csv.Sniffer().sniff(lines[0], delimiters=",;\t").delimiter
        except csv.Error:
            delimiter = ","
    reader = csv.DictReader(lines, delimiter=delimiter)
    if not reader.fieldnames:
        raise ExtractionError("the file has no header row")
    fieldnames = [name.strip() for name in reader.fieldnames if name]
    rows = [
        {key.strip(): (value or "").strip() for key, value in row.items() if key}
        for row in reader
        if any((value or "").strip() for value in row.values() if value is not None)
    ]
    return rows, fieldnames


def require_columns(fieldnames: list[str], required: list[str]) -> None:
    missing = [name for name in required if name not in fieldnames]
    if missing:
        raise ExtractionError(
            "missing required column(s): " + ", ".join(missing)
            + f"; found: {', '.join(fieldnames)}"
        )


def as_float(value: str, label: str, row: int, errors: list[str]) -> float | None:
    try:
        number = float(value)
    except ValueError:
        errors.append(f"row {row}: {label} is not a number ({value!r})")
        return None
    if not math.isfinite(number):
        errors.append(f"row {row}: {label} is not finite ({value!r})")
        return None
    return number


def validate_meta(rows: list[dict], fieldnames: list[str]) -> Report:
    require_columns(fieldnames, ["study", "effect", "variance"])
    report = Report(profile="meta", rows=len(rows))
    if not rows:
        report.errors.append("the file has no data rows")
        return report

    keys: dict[str, int] = {}
    has_outcome = "outcome" in fieldnames
    for index, row in enumerate(rows, 2):
        study = row.get("study", "").strip()
        if not study:
            report.errors.append(f"row {index}: empty 'study'")
        effect = as_float(row.get("effect", ""), "effect", index, report.errors)
        variance = as_float(row.get("variance", ""), "variance", index, report.errors)
        if variance is not None and variance <= 0:
            report.errors.append(f"row {index}: variance must be > 0 (got {variance})")

        if row.get("n"):
            sample = as_float(row["n"], "n", index, report.errors)
            if sample is not None and (sample <= 0 or not sample.is_integer()):
                report.errors.append(f"row {index}: n must be a positive integer (got {row['n']})")

        if row.get("year"):
            year = as_float(row["year"], "year", index, report.errors)
            if year is not None and not (1800 <= year <= date.today().year + 1):
                report.errors.append(f"row {index}: implausible year ({row['year']})")

        low = row.get("ci_low", "")
        high = row.get("ci_high", "")
        if low or high:
            if not (low and high):
                report.warnings.append(f"row {index}: only one of ci_low/ci_high is present")
            else:
                low_value = as_float(low, "ci_low", index, report.errors)
                high_value = as_float(high, "ci_high", index, report.errors)
                if low_value is not None and high_value is not None:
                    if low_value >= high_value:
                        report.errors.append(
                            f"row {index}: ci_low ({low_value}) must be below ci_high ({high_value})"
                        )
                    elif effect is not None and not (low_value <= effect <= high_value):
                        report.warnings.append(
                            f"row {index}: effect ({effect}) lies outside its CI "
                            f"[{low_value}, {high_value}]"
                        )

        key = f"{study.strip().lower()}|{row.get('outcome', '').strip().lower()}" if has_outcome else study.strip().lower()
        if study:
            if key in keys:
                report.warnings.append(
                    f"row {index}: duplicate study/outcome key {key.split('|')[0]!r} "
                    f"(first seen in row {keys[key]})"
                )
            else:
                keys[key] = index

    if len(rows) < 2:
        report.errors.append("k < 2: at least two studies are required to pool")
    elif len(rows) < 10:
        report.warnings.append(
            f"k = {len(rows)}: small-study effects (Egger) are underpowered below 10 studies"
        )

    if has_outcome:
        outcomes = {
            row.get("outcome", "").strip().lower()
            for row in rows
            if row.get("outcome", "").strip()
        }
        if len(outcomes) > 1:
            report.warnings.append(
                f"{len(outcomes)} outcomes present: pool and test one outcome at a time "
                "(filter the CSV to a single outcome)"
            )

    report.notes.append(f"{len(keys)} unique study/outcome key(s)")
    report.notes.append(f"k = {len(rows)}")
    return report


def validate_generic(rows: list[dict], fieldnames: list[str], required: list[str], key: str | None) -> Report:
    require_columns(fieldnames, required)
    report = Report(profile="generic", rows=len(rows))
    if not rows:
        report.errors.append("the file has no data rows")
        return report

    seen: dict[str, int] = {}
    for index, row in enumerate(rows, 2):
        for column in required:
            if not row.get(column, "").strip():
                report.errors.append(f"row {index}: empty required field {column!r}")
        if key:
            value = row.get(key, "").strip().lower()
            if value:
                if value in seen:
                    report.warnings.append(
                        f"row {index}: duplicate key {value!r} in {key!r} (first seen in row {seen[value]})"
                    )
                else:
                    seen[value] = index

    report.notes.append(f"required columns: {', '.join(required)}")
    if key:
        report.notes.append(f"key column: {key}")
    return report


def render(report: Report, source: str) -> str:
    lines = [
        "# Extraction Validation Report",
        "",
        f"**Source:** `{source}`  ",
        f"**Profile:** {report.profile}  ",
        f"**Rows:** {report.rows}  ",
        f"**Errors:** {len(report.errors)} · **Warnings:** {len(report.warnings)}",
        "",
        "## Findings",
        "",
    ]
    if not (report.errors or report.warnings or report.notes):
        lines += ["No issues found.", ""]
    else:
        if report.errors:
            lines += [f"### Errors ({len(report.errors)})", ""]
            lines += [f"- {item}" for item in report.errors] + [""]
        if report.warnings:
            lines += [f"### Warnings ({len(report.warnings)})", ""]
            lines += [f"- {item}" for item in report.warnings] + [""]
        if report.notes:
            lines += ["### Notes", ""]
            lines += [f"- {item}" for item in report.notes] + [""]
    lines += [
        "---",
        "",
        "**Gate:** fix every error before pooling or charting. Warnings require a "
        "sentence in the methods or limitations, not silence.",
        "",
    ]
    return "\n".join(lines)


def selftest() -> None:
    rows = [
        {"study": "A", "effect": "0.4", "variance": "0.03", "n": "120", "year": "2018"},
        {"study": "B", "effect": "0.2", "variance": "0.04", "n": "98", "year": "2019"},
    ]
    report = validate_meta(rows, ["study", "effect", "variance", "n", "year"])
    assert report.ok, report.errors
    assert any("underpowered" in warning for warning in report.warnings), report.warnings

    broken = [
        {"study": "A", "effect": "abc", "variance": "0.03"},
        {"study": "B", "effect": "0.2", "variance": "0"},
        {"study": "C", "effect": "0.2", "variance": "-0.1"},
        {"study": "", "effect": "0.2", "variance": "0.1"},
    ]
    report = validate_meta(broken, ["study", "effect", "variance"])
    assert any("not a number" in error for error in report.errors), report.errors
    assert any("variance must be > 0" in error for error in report.errors)
    assert any("empty 'study'" in error for error in report.errors)

    single = validate_meta([{"study": "A", "effect": "0.4", "variance": "0.03"}], ["study", "effect", "variance"])
    assert any("k < 2" in error for error in single.errors), single.errors

    generic = validate_generic(
        [{"study": "A", "year": "2020", "design": "RCT"}],
        ["study", "year", "design"],
        ["study", "year", "design"],
        "study",
    )
    assert generic.ok, generic.errors

    try:
        require_columns(["study"], ["study", "design"])
    except ExtractionError:
        pass
    else:
        raise AssertionError("missing columns must fail")

    print("validate_extraction selftest OK (meta, generic, ranges, duplicates, k guards)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate an extraction CSV before synthesis.")
    parser.add_argument("csv", nargs="?", help="effects.csv or characteristics.csv")
    parser.add_argument("--profile", choices=("meta", "generic"), default="meta")
    parser.add_argument("--required", help="generic profile: comma-separated required columns")
    parser.add_argument("--key", help="generic profile: column that must be unique")
    parser.add_argument("--delimiter", help="override delimiter (default: auto)")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    parser.add_argument("--out", type=Path, help="write the Markdown report")
    parser.add_argument("--json", dest="json_out", type=Path, help="write findings as JSON")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)

    if args.selftest:
        selftest()
        return 0
    if not args.csv:
        parser.error("provide an extraction CSV (or --selftest)")

    try:
        rows, fieldnames = read_table(Path(args.csv), args.delimiter)
        if args.profile == "meta":
            report = validate_meta(rows, fieldnames)
        else:
            required = [name.strip() for name in (args.required or "study").split(",") if name.strip()]
            report = validate_generic(rows, fieldnames, required, args.key)
    except ExtractionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.out:
        args.out.write_text(render(report, Path(args.csv).name), encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(render(report, Path(args.csv).name))

    if args.json_out:
        payload = {
            "profile": report.profile,
            "rows": report.rows,
            "errors": report.errors,
            "warnings": report.warnings,
            "notes": report.notes,
        }
        args.json_out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"wrote {args.json_out}")

    failed = bool(report.errors) or (args.strict and bool(report.warnings))
    print(
        f"RESULT: {'FAIL' if failed else 'PASS'} "
        f"({len(report.errors)} errors, {len(report.warnings)} warnings)",
        file=sys.stderr,
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
