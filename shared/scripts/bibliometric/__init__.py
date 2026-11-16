"""Bibliometric analysis engine (masteracademicreview).

Public API re-exported so callers can do:

    from bibliometric import load, summary, co_occurrence, plot_pubs_per_year
"""

from .parsers import load, load_csv, load_bibtex
from .performance import (
    publications_per_year,
    top_authors,
    top_journals,
    top_keywords,
    h_index,
    author_h_index,
    summary,
    document_type_counts,
    filter_document_type,
    KEYWORD_NOISE,
)
from .mapping import co_occurrence, co_authorship
from .plots import (
    plot_pubs_per_year,
    plot_top,
    plot_heatmap,
)

__all__ = [
    "KEYWORD_NOISE",
    "author_h_index",
    "co_authorship",
    "co_occurrence",
    "document_type_counts",
    "filter_document_type",
    "h_index",
    "load",
    "load_bibtex",
    "load_csv",
    "plot_heatmap",
    "plot_pubs_per_year",
    "plot_top",
    "publications_per_year",
    "summary",
    "top_authors",
    "top_journals",
    "top_keywords",
]
