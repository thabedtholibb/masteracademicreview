"""Performance analysis: counts, trends, rankings, and h-index."""

from collections import Counter, defaultdict


def publications_per_year(records):
    c = Counter()
    for r in records:
        if r.get("year"):
            c[int(r["year"])] += 1
    return dict(sorted(c.items()))


def top_authors(records, n=10):
    c = Counter()
    for r in records:
        for a in r.get("authors", []):
            c[a] += 1
    return c.most_common(n)


def top_journals(records, n=10):
    c = Counter(r["journal"] for r in records if r.get("journal"))
    return c.most_common(n)


def top_keywords(records, n=20):
    c = Counter()
    for r in records:
        for k in r.get("keywords", []):
            c[k] += 1
    return c.most_common(n)


def document_type_counts(records):
    """Count records by document type (e.g. Article, Review, Conference Paper)."""
    c = Counter()
    for r in records:
        dt = (r.get("document_type") or "Unspecified").strip().lower()
        c[dt] += 1
    return c.most_common()


def filter_document_type(records, allowed):
    """Keep only records whose document_type is in `allowed` (case-insensitive)."""
    allowed = {a.strip().lower() for a in allowed}
    return [r for r in records
            if (r.get("document_type") or "").strip().lower() in allowed]


def h_index(citations):
    """h-index from a sequence of citation counts (papers sorted desc)."""
    vals = sorted((int(x) for x in citations if x is not None), reverse=True)
    h = 0
    for i, c in enumerate(vals, start=1):
        if c >= i:
            h = i
        else:
            break
    return h


def author_h_index(records):
    by_author = defaultdict(list)
    for r in records:
        cites = r.get("citations")
        for a in r.get("authors", []):
            by_author[a].append(cites if cites is not None else 0)
    return {a: h_index(v) for a, v in by_author.items()}


def summary(records):
    """One-shot overview of a corpus. Returns a dict of key figures."""
    years = publications_per_year(records)
    authors = {a for r in records for a in r.get("authors", [])}
    journals = {r.get("journal") for r in records if r.get("journal")}
    total_citations = sum(r.get("citations") or 0 for r in records)
    return {
        "n_records": len(records),
        "year_range": (min(years), max(years)) if years else None,
        "n_authors": len(authors),
        "n_journals": len(journals),
        "total_citations": total_citations,
        "top_authors": top_authors(records, 5),
        "top_journals": top_journals(records, 5),
        "top_keywords": top_keywords(records, 10),
        "h_index_corpus": h_index([r.get("citations") for r in records]),
    }


if __name__ == "__main__":
    # quick demo on a tiny synthetic corpus
    from parsers import load_csv
    import os
    demo = os.path.join(os.path.dirname(__file__), "sample.csv")
    if os.path.exists(demo):
        recs = load_csv(demo)
        s = summary(recs)
        for k, v in s.items():
            print(k, "=", v)
