"""Load a bibliographic corpus into uniform record dicts.

Supported inputs:
- CSV (flexible headers; tuned for Scopus and Web of Science exports)
- BibTeX (.bib; works for Zotero/Mendeley/Web of Science exports)

Every record is normalized to:
    {
        "id": str, "title": str, "authors": [str], "year": int|None,
        "journal": str|None, "keywords": [str], "citations": int|None,
        "doi": str|None, "document_type": str|None
    }
"""

import csv
import io
import os
import re


def load(path, encoding="utf-8-sig"):
    """Load a corpus, choosing the parser by file extension."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".bib":
        return load_bibtex(path, encoding=encoding)
    return load_csv(path, encoding=encoding)


# --------------------------------------------------------------------------- #
# CSV
# --------------------------------------------------------------------------- #

# Aliases are ordered: the first matching column wins. Scopus-specific names
# ("Source title", "Author full names", "Cited by", "Author Keywords",
# "Document Type") come first so Scopus exports are read faithfully.
_ALIASES = {
    "title": ["title", "article title", "ti"],
    "authors": ["author full names", "authors", "author", "af"],
    "year": ["year", "publication year", "publication_year", "pub_year", "py"],
    "journal": ["source title", "journal", "source", "publication name", "so"],
    "keywords": ["author keywords", "keywords", "author_keywords", "index keywords", "de", "keyword"],
    "citations": ["cited by", "citations", "times cited", "times_cited", "tc"],
    "doi": ["doi", "digital object identifier"],
    "document_type": ["document type", "document_type", "dt"],
}


def _norm_key(s):
    return re.sub(r"\s+", " ", s.strip().lower())


def _field_of(row, aliases):
    for a in aliases:
        if row.get(a):
            return row[a].strip()
    return None


def _split_names(s):
    parts = re.split(r"\s+and\s+|;|\n", s)
    out = []
    for p in parts:
        p = p.strip().strip(",").strip()
        if p:
            out.append(p)
    return out


def _split_keywords(s):
    parts = re.split(r";|,|\||\n", s)
    return [p.strip().lower() for p in parts if p.strip()]


def _to_int(s):
    if s is None:
        return None
    m = re.search(r"\d+", str(s))
    return int(m.group()) if m else None


def _read_text(path, encoding="utf-8-sig"):
    """Read a file as text, falling back to cp1252/latin-1 for non-UTF-8 exports.

    Scopus CSV exports are frequently cp1252 (Windows-1252) rather than UTF-8,
    so a strict UTF-8 read would fail on names like "Universit\u00e0".
    """
    with open(path, "rb") as f:
        raw = f.read()
    for enc in (encoding, "cp1252", "latin-1"):
        if not enc:
            continue
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1", errors="replace")


def _detect_delimiter(text):
    """Guess the delimiter from the header line (Scopus uses ';', WoS uses tab)."""
    first_line = text.split("\n", 1)[0]
    counts = {d: first_line.count(d) for d in (";", ",", "\t", "|")}
    best = max(counts, key=counts.get)
    return best if counts[best] else ","


def load_csv(path, encoding="utf-8-sig"):
    text = _read_text(path, encoding)
    delimiter = _detect_delimiter(text)
    records = []
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    for row in reader:
        row_norm = {_norm_key(k): v for k, v in row.items() if k is not None and v is not None}
        title = _field_of(row_norm, _ALIASES["title"])
        if not title:
            continue
        authors_raw = _field_of(row_norm, _ALIASES["authors"]) or ""
        kw_raw = _field_of(row_norm, _ALIASES["keywords"]) or ""
        records.append({
            "id": title,
            "title": title,
            "authors": [_normalize_author(a) for a in _split_names(authors_raw)],
            "year": _to_int(_field_of(row_norm, _ALIASES["year"])),
            "journal": _field_of(row_norm, _ALIASES["journal"]),
            "keywords": _split_keywords(kw_raw),
            "citations": _to_int(_field_of(row_norm, _ALIASES["citations"])),
            "doi": _field_of(row_norm, _ALIASES["doi"]),
            "document_type": _field_of(row_norm, _ALIASES["document_type"]),
        })
    return records


# --------------------------------------------------------------------------- #
# BibTeX
# --------------------------------------------------------------------------- #

def _matching_brace(text, start):
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return i
    return len(text) - 1


def _split_top_commas(s):
    parts, cur = [], []
    depth, in_quote, i = 0, False, 0
    while i < len(s):
        c = s[i]
        if c == '"':
            in_quote = not in_quote
        elif c == "{" and not in_quote:
            depth += 1
        elif c == "}" and not in_quote:
            depth -= 1
        elif c == "," and depth == 0 and not in_quote:
            parts.append("".join(cur).strip())
            cur = []
            i += 1
            continue
        cur.append(c)
        i += 1
    if "".join(cur).strip():
        parts.append("".join(cur).strip())
    return parts


def _parse_field(pair):
    m = re.match(r"\s*([a-zA-Z0-9_\-]+)\s*=\s*(.*)", pair, re.S)
    if not m:
        return None, None
    name = m.group(1).lower()
    val = m.group(2).strip()
    if (val.startswith("{") and val.endswith("}")) or (val.startswith('"') and val.endswith('"')):
        val = val[1:-1]
    val = re.sub(r"\s+", " ", val).strip()
    return name, val


def _normalize_author(a):
    a = a.strip()
    # Scopus "Author full names" append numeric IDs: "Iacovanelli, Matteo (59534050000)"
    a = re.sub(r"\s*\(\s*\d+(?:\s*;\s*\d+)*\s*\)\s*$", "", a).strip()
    if "," in a:
        parts = [p.strip() for p in a.split(",")]
        if len(parts) >= 2 and parts[1]:
            return (parts[1] + " " + parts[0]).strip()
    return a


def load_bibtex(path, encoding="utf-8-sig"):
    with open(path, encoding=encoding) as f:
        text = f.read()
    text = re.sub(r"@comment\s*\{.*?\}", "", text, flags=re.I | re.S)
    records = []
    i = 0
    while i < len(text):
        m = re.search(r"@(\w+)\s*\{", text[i:], re.I)
        if not m:
            break
        entry_type = m.group(1).lower()
        start = i + m.end() - 1
        end = _matching_brace(text, start)
        body = text[start + 1:end]
        parts = _split_top_commas(body)
        key = parts[0].strip() if parts else "?"
        fields = {}
        for p in parts[1:]:
            name, val = _parse_field(p)
            if name and val:
                fields[name] = val
        if not fields.get("title"):
            i = end + 1
            continue
        records.append({
            "id": key,
            "title": fields.get("title"),
            "authors": [_normalize_author(a) for a in _split_names(fields.get("author", ""))],
            "year": _to_int(fields.get("year")),
            "journal": fields.get("journal") or fields.get("booktitle"),
            "keywords": _split_keywords(fields.get("keywords", "")),
            "citations": _to_int(fields.get("citations") or fields.get("timescited")),
            "doi": fields.get("doi"),
            "document_type": fields.get("documenttype") or entry_type,
        })
        i = end + 1
    return records
