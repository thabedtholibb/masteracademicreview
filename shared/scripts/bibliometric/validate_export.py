"""Validate a real bibliographic export end-to-end (regression harness).

This is the guard that keeps the parser honest against real-world exports:
semicolon-delimited Scopus CSV, cp1252 encoding, author IDs in parentheses,
index-keyword noise, and missing columns.

Usage:
    python validate_export.py path/to/scopus.csv
    python validate_export.py path/to/scopus.csv --plots out_dir

Exit code 0 when every check passes, 1 otherwise. Warnings do not fail the run.
"""

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parsers import load
from performance import (KEYWORD_NOISE, document_type_counts, filter_document_type,
                         summary, top_keywords)
from mapping import co_occurrence


class Report:
    def __init__(self):
        self.rows = []

    def _add(self, level, name, detail=""):
        self.rows.append((level, name, detail))

    def check(self, ok, name, detail=""):
        self._add("PASS" if ok else "FAIL", name, detail)

    def warn(self, ok, name, detail=""):
        self._add("PASS" if ok else "WARN", name, detail)

    def note(self, name, detail=""):
        self._add("PASS", name, detail)

    def failures(self):
        return sum(1 for level, _, _ in self.rows if level == "FAIL")

    def warnings(self):
        return sum(1 for level, _, _ in self.rows if level == "WARN")

    def render(self, path):
        print(f"Export validation: {path}")
        width = max(len(name) for _, name, _ in self.rows) + 2
        for level, name, detail in self.rows:
            mark = {"PASS": "[PASS]", "WARN": "[WARN]", "FAIL": "[FAIL]"}[level]
            line = f"  {mark} {name.ljust(width)}"
            if detail:
                line += f" {detail}"
            print(line.rstrip())
        result = "PASS" if self.failures() == 0 else "FAIL"
        print(f"\nRESULT: {result} ({len(self.rows)} checks, "
              f"{self.warnings()} warnings, {self.failures()} failures)")
        return self.failures() == 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", help="path to a Scopus/WoS CSV or BibTeX export")
    ap.add_argument("--plots", metavar="DIR",
                    help="also write plots into DIR")
    ap.add_argument("--min-keyword-coverage", type=float, default=0.5,
                    help="warn below this share of records with keywords (default 0.5)")
    args = ap.parse_args(argv)

    rep = Report()
    path = args.csv

    rep.check(os.path.exists(path), "file exists", path)
    if not os.path.exists(path):
        rep.render(path)
        return 1

    try:
        records = load(path)
    except Exception as exc:  # noqa: BLE001 - report any parse failure
        rep.check(False, "parses without error", f"{type(exc).__name__}: {exc}")
        rep.render(path)
        return 1
    rep.check(bool(records), "parses without error", f"{len(records)} records")
    if not records:
        rep.render(path)
        return 1

    # --- structural integrity ------------------------------------------------
    rep.check(all(r["title"] for r in records), "every record has a title",
              f"{sum(1 for r in records if not r['title'])} empty")

    id_leaks = [a for r in records for a in r["authors"] if re.search(r"\d", a)]
    rep.check(not id_leaks, "author names carry no numeric IDs",
              f"{len(id_leaks)} leaks" + (f", e.g. {id_leaks[0]!r}" if id_leaks else ""))

    with_year = sum(1 for r in records if r["year"])
    rep.warn(with_year / len(records) >= 0.9, "year parsed for >= 90% of records",
             f"{with_year}/{len(records)}")

    with_kw = sum(1 for r in records if r["keywords"])
    rep.warn(with_kw / len(records) >= args.min_keyword_coverage,
             "keywords parsed for >= {:.0%} of records".format(args.min_keyword_coverage),
             f"{with_kw}/{len(records)}")

    with_cites = sum(1 for r in records if r["citations"] is not None)
    rep.warn(with_cites / len(records) >= 0.9, "citations parsed for >= 90% of records",
             f"{with_cites}/{len(records)}")

    # --- document types (the Scopus quality gate) ---------------------------
    doc_types = document_type_counts(records)
    rep.warn(all(dt != "unspecified" for dt, _ in doc_types),
             "document type present (quality filter possible)",
             ", ".join(f"{dt}={n}" for dt, n in doc_types))
    kept = filter_document_type(records, {"article", "review"})
    rep.warn(bool(kept), "Article/Review filter keeps records", f"{len(kept)} kept")

    # --- keyword analysis ----------------------------------------------------
    top = top_keywords(records, 10)
    leaked = [k for k, _ in top if k in KEYWORD_NOISE]
    rep.check(not leaked, "top keywords contain no index-keyword noise",
              f"leaked: {leaked}" if leaked else "clean")

    labels, matrix = co_occurrence(records, field="keywords", top_n=10)
    shape_ok = bool(labels) and getattr(matrix, "shape", None) == (len(labels), len(labels))
    rep.check(shape_ok, "co-occurrence matrix is square and matches labels",
              f"{getattr(matrix, 'shape', None)}")
    if shape_ok:
        diag_ok = all(matrix[i, i] >= matrix[i, j]
                      for i in range(len(labels)) for j in range(len(labels)))
        rep.check(diag_ok, "diagonal >= off-diagonal (document counts)")

    # --- optional artifacts --------------------------------------------------
    if args.plots:
        os.makedirs(args.plots, exist_ok=True)
        from plots import plot_heatmap, plot_pubs_per_year, plot_top
        from performance import publications_per_year, top_journals
        plot_pubs_per_year(publications_per_year(kept or records),
                           os.path.join(args.plots, "pubs_per_year.png"))
        plot_top(top_journals(kept or records, 10),
                 os.path.join(args.plots, "top_journals.png"),
                 xlabel="Documents", title="Top journals")
        plot_heatmap(labels, matrix, os.path.join(args.plots, "cooccurrence.png"))
        rep.note("plots written", args.plots)

    # --- corpus overview -----------------------------------------------------
    s = summary(kept or records)
    print("\nCorpus overview (Article/Review when available):")
    print(f"  records={s['n_records']}  years={s['year_range']}  "
          f"authors={s['n_authors']}  sources={s['n_journals']}  "
          f"citations={s['total_citations']}  h={s['h_index_corpus']}")
    print(f"  top keywords: {[k for k, _ in s['top_keywords'][:5]]}\n")

    ok = rep.render(path)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
