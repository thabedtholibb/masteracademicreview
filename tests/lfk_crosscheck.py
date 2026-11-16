#!/usr/bin/env python3
"""Compare the Python LFK index with R metasens::lfkindex values.

    Rscript tests/lfk_crosscheck.R                 # writes r_lfk.csv
    python tests/lfk_crosscheck.py r_lfk.csv       # exit 1 on any mismatch

Without an argument it only prints the Python values (no R needed).
Needs numpy/scipy/matplotlib (the meta engine).
"""

from __future__ import annotations

import csv
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared" / "scripts"))

from meta import lfk_index  # noqa: E402

TOL = 1e-8


def python_values() -> OrderedDict[str, float]:
    data: OrderedDict[str, tuple[list[float], list[float]]] = OrderedDict()
    with (ROOT / "tests" / "fixtures" / "lfk_crosscheck.csv").open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            te, var = data.setdefault(row["dataset"], ([], []))
            te.append(float(row["te"]))
            var.append(float(row["var"]))
    return OrderedDict((k, lfk_index(te, var)["lfk"]) for k, (te, var) in data.items())


def main(argv: list[str]) -> int:
    py = python_values()
    if len(argv) < 2:
        for k, v in py.items():
            print(f"{k:<8} python LFK = {v:.10f}")
        return 0
    with open(argv[1], encoding="utf-8") as f:
        r = {row["dataset"]: float(row["lfk"]) for row in csv.DictReader(f)}
    bad = 0
    for k, v in py.items():
        diff = abs(v - r[k])
        ok = diff < TOL
        bad += not ok
        print(f"[{'PASS' if ok else 'FAIL'}] {k:<8} python {v:.10f}  R {r[k]:.10f}  |diff| {diff:.2e}")
    if set(py) != set(r):
        print("dataset mismatch:", sorted(set(py) ^ set(r)))
        return 1
    print("LFK cross-check OK" if not bad else f"{bad} mismatch(es)")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
