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
    "load",
    "load_csv",
    "load_bibtex",
    "publications_per_year",
    "top_authors",
    "top_journals",
    "top_keywords",
    "h_index",
    "author_h_index",
    "summary",
    "document_type_counts",
    "filter_document_type",
    "KEYWORD_NOISE",
    "co_occurrence",
    "co_authorship",
    "plot_pubs_per_year",
    "plot_top",
    "plot_heatmap",
]
