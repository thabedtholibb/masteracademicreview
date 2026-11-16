"""Science mapping: co-occurrence and co-authorship matrices."""

from collections import Counter

import numpy as np

try:  # package import
    from .performance import KEYWORD_NOISE
except ImportError:  # direct script import
    from performance import KEYWORD_NOISE


def _index_and_matrix(records, field, top_n, undirected, exclude=None):
    counter = Counter()
    for r in records:
        for item in r.get(field, []):
            if exclude and item in exclude:
                continue
            counter[item] += 1
    labels = [k for k, _ in counter.most_common(top_n)]
    idx = {lab: i for i, lab in enumerate(labels)}
    n = len(labels)
    m = np.zeros((n, n), dtype=int)
    for r in records:
        items = [it for it in r.get(field, []) if it in idx]
        for it in items:
            m[idx[it], idx[it]] += 1
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                m[idx[items[i]], idx[items[j]]] += 1
                if undirected:
                    m[idx[items[j]], idx[items[i]]] += 1
    return labels, m


def co_occurrence(records, field="keywords", top_n=20, exclude="auto"):
    """Co-occurrence matrix over a list-valued field (default: keywords).

    Diagonal = number of records containing the item; off-diagonal = number of
    records containing both items. Index-keyword noise is excluded by default
    for keywords; pass ``exclude=None`` to keep everything.
    """
    if exclude == "auto":
        exclude = KEYWORD_NOISE if field == "keywords" else None
    return _index_and_matrix(records, field, top_n, undirected=True, exclude=exclude)


def co_authorship(records, top_n=20):
    """Co-authorship matrix over the most frequent authors.

    Off-diagonal = number of papers co-authored by both authors.
    """
    return _index_and_matrix(records, "authors", top_n, undirected=True)
