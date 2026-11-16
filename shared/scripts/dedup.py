#!/usr/bin/env python3
"""Deduplicate search results from several databases (RIS / CSV / BibTeX).

The most time-consuming step before screening, made deterministic and
auditable. Feed it one export per database; it returns the unique records,
a log of every removal with its rule, a list of *possible* duplicates for a
human to decide, and the PRISMA identification counts.

    python dedup.py --source Scopus=scopus.csv --source PubMed=pubmed.ris \\
                    --source WoS=wos.bib --out-dir dedup_out
    python dedup.py scopus.csv pubmed.ris           # source = file name
    python dedup.py --selftest

Matching rules, applied in priority order (JEV: certain matches are removed
automatically, uncertain ones are only recommended):

1. ``doi``          same normalized DOI                        -> removed
2. ``title-year``   same normalized title, same year (or one   -> removed
                    missing) and no conflicting first author
3. ``fuzzy``        title similarity >= threshold (0.93) and   -> listed in
                    years within 1                                possible_duplicates.csv
                                                                  (removed only with
                                                                  --merge-possible)

Which copy is kept (JEV, #1 first): the most complete record (DOI, authors,
year, journal), then the source listed first in --priority (or the order of
--source), then the first record read. Missing DOI/journal/year on the kept
record are filled from its duplicates.

Outputs in --out-dir:
    deduplicated.csv         unique records with stable record_id (R0001...)
    duplicates.csv           every removed record: kept_id, removed record, rule
    possible_duplicates.csv  pairs to check by hand (not removed)
    screening_template.csv   record_id,stage,reviewer1,reviewer2 for screening_agreement.py
    prisma_identification.json  identification counts for prisma_flow.py
    dedup_report.md          counts per source and rule + ranked next steps

Stdlib only. Exit codes: 0 = done, 2 = unreadable input.
"""

from __future__ import annotations

import argparse
import csv
import difflib
import importlib.util
import json
import re
import sys
import tempfile
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIELDS = ("title", "authors", "year", "journal", "doi", "document_type")
STOPWORDS = {"with", "from", "into", "among", "between", "their", "this", "that", "study",
             "review", "effect", "effects", "analysis", "based", "using", "toward", "towards",
             "versus", "about", "after", "under", "over", "through", "during", "within"}


class DedupError(Exception):
    pass


def _parsers():
    """Load bibliometric/parsers.py by path (its package __init__ needs numpy)."""
    spec = importlib.util.spec_from_file_location("_mar_parsers", HERE / "bibliometric" / "parsers.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------------- #
# Reading
# --------------------------------------------------------------------------- #

RIS_TAG = re.compile(r"^([A-Z][A-Z0-9])  -(?: (.*))?$")


def parse_ris(text: str) -> list[dict]:
    """Minimal RIS reader (EndNote, Zotero, PubMed, Scopus, WoS exports)."""
    records, cur = [], {}
    last = None
    for line in text.splitlines():
        m = RIS_TAG.match(line.rstrip())
        if not m:
            if last and line.strip() and cur.get(last):
                cur[last][-1] += " " + line.strip()   # continuation line
            continue
        tag, value = m.group(1), (m.group(2) or "").strip()
        if tag == "ER":
            if cur:
                records.append(cur)
            cur, last = {}, None
            continue
        cur.setdefault(tag, []).append(value)
        last = tag
    if cur:
        records.append(cur)

    def first(rec, *tags):
        for t in tags:
            for v in rec.get(t, []):
                if v:
                    return v
        return None

    out = []
    for rec in records:
        title = first(rec, "TI", "T1", "CT", "BT")
        if not title:
            continue
        year_raw = first(rec, "PY", "Y1", "DA", "Y2") or ""
        ym = re.search(r"(1[89]|20)\d{2}", year_raw)
        authors = rec.get("AU", []) + rec.get("A1", [])
        out.append({
            "title": title,
            "authors": [a for a in authors if a],
            "year": int(ym.group()) if ym else None,
            "journal": first(rec, "JO", "T2", "JF", "JA", "J2"),
            "doi": first(rec, "DO"),
            "document_type": first(rec, "TY"),
        })
    return out


def read_records(path: Path) -> list[dict]:
    if not path.is_file():
        raise DedupError(f"file not found: {path}")
    parsers = _parsers()
    text = parsers._read_text(str(path))
    head = text.lstrip("﻿")[:4000]
    if re.search(r"^TY  - ", head, re.M):
        recs = parse_ris(text)
    elif path.suffix.lower() == ".bib" or head.lstrip().startswith("@"):
        recs = parsers.load_bibtex(str(path))
    else:
        recs = parsers.load_csv(str(path))
    if not recs:
        raise DedupError(f"no records with a title found in {path}")
    return [{k: r.get(k) for k in FIELDS} for r in recs]


# --------------------------------------------------------------------------- #
# Normalization
# --------------------------------------------------------------------------- #

def norm_doi(doi) -> str:
    if not doi:
        return ""
    d = str(doi).strip().lower()
    d = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", d)
    return d.rstrip(" .;,")


def norm_text(s) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r"<[^>]+>|[{}\\]", " ", s)          # html/latex braces
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def first_author_key(authors) -> str:
    if not authors:
        return ""
    a = str(authors[0]).strip()
    if "," in a:                       # "Smith, J." -> smith
        surname = a.split(",")[0]
    else:                              # "John Smith" / "Smith J" -> best guess
        parts = a.split()
        surname = parts[-1] if parts and len(parts[-1]) > 2 else (parts[0] if parts else "")
    return norm_text(surname)


def completeness(rec: dict) -> int:
    return (3 * bool(norm_doi(rec.get("doi"))) + bool(rec.get("authors"))
            + bool(rec.get("year")) + bool(rec.get("journal")))


# --------------------------------------------------------------------------- #
# Dedup
# --------------------------------------------------------------------------- #

class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))

    def find(self, i):
        while self.parent[i] != i:
            self.parent[i] = self.parent[self.parent[i]]
            i = self.parent[i]
        return i

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[max(ra, rb)] = min(ra, rb)


def deduplicate(sources: list[tuple[str, list[dict]]], threshold: float = 0.93,
                merge_possible: bool = False, priority: list[str] | None = None) -> dict:
    """Pure function: sources = [(name, records)] -> result dict (no I/O)."""
    recs = []
    for src_rank, (name, records) in enumerate(sources):
        for rec in records:
            r = dict(rec)
            r["source"] = name
            r["_src_rank"] = src_rank
            r["_doi"] = norm_doi(r.get("doi"))
            r["_title"] = norm_text(r.get("title"))
            r["_fa"] = first_author_key(r.get("authors"))
            recs.append(r)
    if priority:
        order = {s.lower(): i for i, s in enumerate(priority)}
        for r in recs:
            r["_src_rank"] = order.get(r["source"].lower(), len(order) + r["_src_rank"])

    n = len(recs)
    uf = UnionFind(n)
    rule_of: dict[int, tuple[str, float]] = {}

    def link(i, j, rule, sim=1.0):
        if uf.find(i) != uf.find(j):
            uf.union(i, j)
            rule_of.setdefault(j, (rule, sim))

    # 1. DOI
    by_doi: dict[str, int] = {}
    for i, r in enumerate(recs):
        if r["_doi"]:
            if r["_doi"] in by_doi:
                link(by_doi[r["_doi"]], i, "doi")
            else:
                by_doi[r["_doi"]] = i

    # 2. exact title + compatible year/author
    by_title: dict[str, list[int]] = {}
    for i, r in enumerate(recs):
        if r["_title"]:
            by_title.setdefault(r["_title"], []).append(i)
    for idxs in by_title.values():
        for a_pos, i in enumerate(idxs):
            for j in idxs[a_pos + 1:]:
                a, b = recs[i], recs[j]
                if a["_doi"] and b["_doi"] and a["_doi"] != b["_doi"]:
                    continue  # different DOIs: e.g. erratum or a series with one title
                year_ok = not a.get("year") or not b.get("year") or a["year"] == b["year"]
                fa_ok = not a["_fa"] or not b["_fa"] or a["_fa"] == b["_fa"]
                if year_ok and fa_ok:
                    link(i, j, "title-year")

    # 3. fuzzy candidates. Blocking keeps this fast: two records are compared
    # only if they share the first, last or longest title word, so a typo in
    # one word does not hide a duplicate.
    possible = []
    blocks: dict[str, list[int]] = {}
    for i, r in enumerate(recs):
        words = [w for w in r["_title"].split() if len(w) > 3 and w not in STOPWORDS]
        words = words or r["_title"].split()
        if words:
            for key in {words[0], words[-1], max(words, key=len)}:
                blocks.setdefault(key, []).append(i)
    seen_pairs: set[tuple[int, int]] = set()
    for idxs in blocks.values():
        for a_pos, i in enumerate(idxs):
            for j in idxs[a_pos + 1:]:
                if (i, j) in seen_pairs or uf.find(i) == uf.find(j):
                    continue
                seen_pairs.add((i, j))
                a, b = recs[i], recs[j]
                if a["_doi"] and b["_doi"] and a["_doi"] != b["_doi"]:
                    continue
                ya, yb = a.get("year"), b.get("year")
                if ya and yb and abs(ya - yb) > 1:
                    continue
                matcher = difflib.SequenceMatcher(None, a["_title"], b["_title"])
                if matcher.real_quick_ratio() < threshold or matcher.quick_ratio() < threshold:
                    continue
                sim = matcher.ratio()
                if sim >= threshold:
                    possible.append((i, j, sim))
    if merge_possible:
        for i, j, sim in possible:
            link(i, j, "fuzzy", sim)

    # clusters and the kept record per cluster (JEV ranking)
    clusters: dict[int, list[int]] = {}
    for i in range(n):
        clusters.setdefault(uf.find(i), []).append(i)
    kept_rows, removed_rows = [], []
    kept_of: dict[int, int] = {}
    for members in clusters.values():
        best = min(members, key=lambda k: (-completeness(recs[k]), recs[k]["_src_rank"], k))
        keep = dict(recs[best])
        for k in members:
            if k == best:
                continue
            for field in ("doi", "journal", "year"):
                if not keep.get(field) and recs[k].get(field):
                    keep[field] = recs[k][field]
            if not keep.get("authors") and recs[k].get("authors"):
                keep["authors"] = recs[k]["authors"]
        keep["_members"] = members
        keep["_best"] = best
        kept_rows.append(keep)
    kept_rows.sort(key=lambda r: r["_best"])
    for pos, keep in enumerate(kept_rows, 1):
        keep["record_id"] = f"R{pos:04d}"
        keep["n_copies"] = len(keep["_members"])
        for k in keep["_members"]:
            kept_of[k] = pos - 1
            if k != keep["_best"]:
                rule, sim = rule_of.get(k, ("doi", 1.0))
                if k not in rule_of:   # k was the root; the best one got the rule
                    rule, sim = rule_of.get(keep["_best"], ("title-year", 1.0))
                removed_rows.append({
                    "kept_id": keep["record_id"], "kept_source": keep["source"],
                    "removed_source": recs[k]["source"], "rule": rule,
                    "similarity": round(sim, 3), "title": recs[k].get("title") or "",
                    "year": recs[k].get("year") or "", "doi": recs[k].get("doi") or "",
                })

    possible_rows = []
    if not merge_possible:
        reported: set[tuple[int, int]] = set()
        for i, j, sim in sorted(possible, key=lambda t: (-t[2], t[0], t[1])):
            pair = tuple(sorted((kept_of[i], kept_of[j])))
            if pair[0] == pair[1] or pair in reported:
                continue  # one row per pair of unique records, highest similarity
            reported.add(pair)
            possible_rows.append({
                "record_a": kept_rows[kept_of[i]]["record_id"],
                "record_b": kept_rows[kept_of[j]]["record_id"],
                "similarity": round(sim, 3),
                "title_a": recs[i].get("title") or "", "title_b": recs[j].get("title") or "",
                "year_a": recs[i].get("year") or "", "year_b": recs[j].get("year") or "",
                "source_a": recs[i]["source"], "source_b": recs[j]["source"],
                "recommendation": "#1 likely duplicate: check DOI/authors, then remove one"
                                  if sim >= 0.97 else "#1 check full record before removing",
            })

    per_source = [(name, len(records)) for name, records in sources]
    by_rule: dict[str, int] = {}
    for row in removed_rows:
        by_rule[row["rule"]] = by_rule.get(row["rule"], 0) + 1
    return {
        "kept": kept_rows, "removed": removed_rows, "possible": possible_rows,
        "per_source": per_source, "by_rule": by_rule,
        "total_in": n, "total_out": len(kept_rows),
    }


# --------------------------------------------------------------------------- #
# Writing
# --------------------------------------------------------------------------- #

def _write_csv(path: Path, rows: list[dict], header: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow(row)


def prisma_identification(result: dict) -> dict:
    removed = result["total_in"] - result["total_out"]
    return {
        "database_records": [[name, count] for name, count in result["per_source"]],
        "removed_before_screening": [["Duplicate records removed", removed]],
        "after_dedup": result["total_out"],
        "screened": result["total_out"],
    }


def report(result: dict) -> str:
    removed = result["total_in"] - result["total_out"]
    lines = [
        "# Deduplication report", "",
        "**Records identified:** %d  " % result["total_in"],
        "**Duplicates removed:** %d  " % removed,
        "**Unique records (to screen):** %d  " % result["total_out"],
        "**Possible duplicates to check by hand:** %d" % len(result["possible"]), "",
        "## Records per source", "", "| Source | Records |", "|---|---:|",
    ]
    lines += ["| %s | %d |" % (s, c) for s, c in result["per_source"]]
    lines += ["", "## Removed by rule", "", "| Rule | Removed |", "|---|---:|"]
    lines += ["| %s | %d |" % (r, c) for r, c in sorted(result["by_rule"].items())] or ["| — | 0 |"]
    lines += ["", "## Next steps (JEV, ranked)", ""]
    steps = []
    if result["possible"]:
        steps.append("Resolve `possible_duplicates.csv` by hand (highest similarity first); "
                     "re-run with `--merge-possible` only if every pair is a true duplicate.")
    steps.append("Screen `deduplicated.csv`; record decisions in `screening_template.csv` "
                 "(two reviewers) and run `screening_agreement.py`.")
    steps.append("Merge `prisma_identification.json` with your screening counts and run "
                 "`prisma_flow.py prisma_identification.json screening_counts.json`.")
    steps.append("Report the deduplication method (this tool, rules, threshold) in Methods.")
    lines += ["%d. %s%s" % (i, "**#1 recommended:** " if i == 1 else "", s)
              for i, s in enumerate(steps, 1)]
    lines.append("")
    return "\n".join(lines)


def write_outputs(result: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    kept = []
    for r in result["kept"]:
        kept.append({
            "record_id": r["record_id"], "source": r["source"], "n_copies": r["n_copies"],
            "title": r.get("title") or "", "authors": "; ".join(r.get("authors") or []),
            "year": r.get("year") or "", "journal": r.get("journal") or "",
            "doi": r.get("doi") or "", "document_type": r.get("document_type") or "",
        })
    _write_csv(out_dir / "deduplicated.csv", kept,
               ["record_id", "source", "n_copies", "title", "authors", "year", "journal",
                "doi", "document_type"])
    _write_csv(out_dir / "duplicates.csv", result["removed"],
               ["kept_id", "kept_source", "removed_source", "rule", "similarity", "title",
                "year", "doi"])
    _write_csv(out_dir / "possible_duplicates.csv", result["possible"],
               ["record_a", "record_b", "similarity", "recommendation", "title_a", "title_b",
                "year_a", "year_b", "source_a", "source_b"])
    _write_csv(out_dir / "screening_template.csv",
               [{"record_id": k["record_id"], "stage": "title_abstract"} for k in kept],
               ["record_id", "stage", "reviewer1", "reviewer2"])
    (out_dir / "prisma_identification.json").write_text(
        json.dumps(prisma_identification(result), indent=2), encoding="utf-8")
    (out_dir / "dedup_report.md").write_text(report(result), encoding="utf-8")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def selftest() -> None:
    ris = ("TY  - JOUR\nTI  - Exercise and depression in older adults\nAU  - Smith, John\n"
           "PY  - 2020\nJO  - Journal of Tests\nDO  - 10.1000/ABC\nER  - \n"
           "TY  - JOUR\nTI  - A completely different topic\nAU  - Lee, Ann\nPY  - 2019\nER  - \n")
    sources = [
        ("PubMed", parse_ris(ris)),
        ("Scopus", [
            {"title": "Exercise and Depression in Older Adults.", "authors": ["John Smith"],
             "year": 2020, "journal": None, "doi": "https://doi.org/10.1000/abc"},
            {"title": "A completely different topic", "authors": ["Ann Lee"], "year": 2019,
             "journal": "J X", "doi": None},
            {"title": "Excercise and depression in older adult", "authors": ["Smith J"],
             "year": 2021, "journal": None, "doi": None},
        ]),
    ]
    res = deduplicate(sources)
    assert res["total_in"] == 5 and res["total_out"] == 3, (res["total_in"], res["total_out"])
    assert res["by_rule"] == {"doi": 1, "title-year": 1}, res["by_rule"]
    assert len(res["possible"]) == 1, res["possible"]
    merged = deduplicate(sources, merge_possible=True)
    assert merged["total_out"] == 2 and merged["by_rule"].get("fuzzy") == 1
    kept = {r["title"]: r for r in res["kept"]}
    assert kept["A completely different topic"]["journal"] == "J X"  # filled from duplicate
    assert norm_doi("DOI: 10.1/X.") == "10.1/x"
    same_title_diff_doi = [("A", [{"title": "Erratum", "year": 2020, "doi": "10.1/a", "authors": []}]),
                           ("B", [{"title": "Erratum", "year": 2020, "doi": "10.1/b", "authors": []}])]
    assert deduplicate(same_title_diff_doi)["total_out"] == 2
    ident = prisma_identification(res)
    assert ident["after_dedup"] == 3 and ident["removed_before_screening"][0][1] == 2
    with tempfile.TemporaryDirectory() as d:
        write_outputs(res, Path(d))
        assert (Path(d) / "deduplicated.csv").read_text(encoding="utf-8").count("\n") == 4
        assert "#1 recommended" in (Path(d) / "dedup_report.md").read_text(encoding="utf-8")
    print("dedup selftest OK (doi, title-year, fuzzy, merge, keep-rule, outputs)")


def _parse_sources(items: list[str], positional: list[str]) -> list[tuple[str, Path]]:
    out = []
    for item in items:
        if "=" not in item:
            raise DedupError(f"--source needs NAME=FILE (got {item!r})")
        name, path = item.split("=", 1)
        out.append((name.strip(), Path(path.strip())))
    for p in positional:
        out.append((Path(p).stem, Path(p)))
    return out


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    p = argparse.ArgumentParser(description="Deduplicate RIS/CSV/BibTeX exports from several databases.")
    p.add_argument("files", nargs="*", help="export files (source name = file name)")
    p.add_argument("--source", action="append", default=[], metavar="NAME=FILE",
                   help="named source, repeatable (e.g. --source Scopus=scopus.csv)")
    p.add_argument("--out-dir", type=Path, default=Path("dedup_out"))
    p.add_argument("--threshold", type=float, default=0.93,
                   help="title similarity for possible duplicates (default 0.93)")
    p.add_argument("--merge-possible", action="store_true",
                   help="also remove fuzzy matches (only after checking them)")
    p.add_argument("--priority", help="comma list of sources to keep first, e.g. Scopus,PubMed")
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args(argv)
    if a.selftest:
        selftest()
        return 0
    try:
        named = _parse_sources(a.source, a.files)
        if not named:
            p.error("give at least one export file (or --selftest)")
        sources = [(name, read_records(path)) for name, path in named]
    except DedupError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if not 0.5 <= a.threshold <= 1.0:
        p.error("--threshold must be between 0.5 and 1.0")
    priority = [s.strip() for s in a.priority.split(",")] if a.priority else None
    result = deduplicate(sources, a.threshold, a.merge_possible, priority)
    write_outputs(result, a.out_dir)
    print(report(result))
    print(f"wrote {a.out_dir}/ (deduplicated.csv, duplicates.csv, possible_duplicates.csv, "
          "screening_template.csv, prisma_identification.json, dedup_report.md)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
