#!/usr/bin/env python3
"""Reference integrity checker for masteracademicreview.

Two modes:

1. **Offline (default, deterministic).** Parses a Markdown review (or a
   .bib / .ris / .txt reference list) and checks that the reference list is
   internally consistent:

   - duplicate DOIs;
   - references without a year or title;
   - numeric citations that point outside the reference list;
   - author-year citations with no matching reference;
   - references that are never cited (warning; skipped when the review uses a
     running bibliography with no in-text citations, as bibliometric reviews do).

2. **Online (`--online`, Crossref).** Verifies each reference against Crossref:
   DOI lookup when a DOI is present, bibliographic search otherwise. Compares the
   title and year, and classifies each reference as VERIFIED, YEAR_MISMATCH,
   AMBIGUOUS, NO_MATCH, DOI_MISMATCH, NOT_FOUND or ERROR.

The online mode is opt-in because it needs network access. CI runs the offline
mode only, so the reproducible checks never depend on the internet.

Exit codes: 0 = pass, 1 = errors found, 2 = cannot parse the input.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path

DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"'<>]+", re.I)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
REF_HEADING_RE = re.compile(
    r"^(references?|bibliography|works cited|daftar pustaka|rujukan)$", re.I
)
NUMBERED_RE = re.compile(r"^\s*(?:\[(\d+)\]|(\d+)[.)])\s+(.*)$")
BULLET_RE = re.compile(r"^\s*[-*+]\s+(.*)$")
YEAR_PAREN_RE = re.compile(r"\(((?:19|20)\d{2})[a-z]?\)")

CURRENT_YEAR = date.today().year
UA = "masteracademicreview-verify-refs/1.0"
ORG_SUFFIXES = {
    "administration", "agency", "association", "bank", "center", "centre",
    "commission", "committee", "consortium", "council", "department",
    "federation", "foundation", "group", "institute", "ministry", "network",
    "office", "organisation", "organization", "program", "programme",
    "service", "services", "society", "university",
}
METHOD_CITATION_NAMES = {
    "amstar", "casp", "cochrane", "consort", "coreq", "equator", "grade",
    "jbi", "moose", "prisma", "prismascr", "prismas", "prior", "rameses",
    "rob", "robins", "roses", "sanra", "spider", "strobe", "trend",
}


@dataclass
class Reference:
    index: int
    raw: str
    number: int | None = None
    doi: str = ""
    year: int | None = None
    title: str = ""
    surname: str = ""


@dataclass
class OfflineResult:
    refs: list[Reference]
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    infos: list[str] = field(default_factory=list)
    style: str = "unknown"
    n_citations: int = 0
    n_with_doi: int = 0

    @property
    def ok(self) -> bool:
        return not self.errors


class ParseError(Exception):
    pass


# --------------------------------------------------------------------------
# Text helpers
# --------------------------------------------------------------------------

def strip_markup(text: str) -> str:
    text = html.unescape(text)
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]*)\)", r"\1", text)
    for token in ("**", "__", "*", "_", "`"):
        text = text.replace(token, "")
    return re.sub(r"\s+", " ", text).strip()


def extract_doi(text: str) -> str:
    match = DOI_RE.search(text)
    if not match:
        return ""
    doi = match.group(0).rstrip(".,;")
    # Drop a wrapping closing parenthesis, but keep balanced parentheses that
    # belong to the DOI itself (e.g. 10.1016/0197-2456(86)90046-2).
    while doi.endswith(")") and doi[:-1].count("(") == doi[:-1].count(")"):
        doi = doi[:-1]
    return doi


def extract_year(text: str, doi: str = "") -> int | None:
    clean = text.replace(doi, "") if doi else text
    match = YEAR_PAREN_RE.search(clean)
    if match:
        return int(match.group(1))
    # Skip numbers inside page ranges or volume:page tails ("283(15):2008-2012"),
    # which look like years; prefer the Vancouver "2000;283(15)" position.
    cands = [m for m in re.finditer(r"(?<![\d:\-\u2013/])((?:19|20)\d{2})(?![\d\-\u2013])", clean)
             if 1800 <= int(m.group(1)) <= CURRENT_YEAR + 1]
    vancouver = [int(m.group(1)) for m in cands if clean[m.end():m.end() + 1] == ";"]
    if vancouver:
        return vancouver[0]
    if cands:
        return int(cands[-1].group(1))
    years = [int(y) for y in re.findall(r"\b((?:19|20)\d{2})\b", clean)]
    years = [y for y in years if 1800 <= y <= CURRENT_YEAR + 1]
    return years[-1] if years else None


def extract_title(text: str, doi: str = "", year: int | None = None) -> str:
    clean = text.replace(doi, "") if doi else text
    clean = re.sub(r"\bdoi:\s*", "", clean, flags=re.I).strip()
    match = YEAR_PAREN_RE.search(clean)
    if match:
        after = clean[match.end():].lstrip(" .,:;")
        title = re.split(r"\.\s", after, maxsplit=1)[0].strip(" .")
        if title and not re.match(r"^(19|20)\d{2}\b", title):
            return title
    parts = [p.strip(" .") for p in re.split(r"\.\s+", clean) if p.strip(" .")]
    candidates = parts[1:4] if len(parts) > 1 else parts
    for candidate in candidates:
        if re.match(r"^(19|20)\d{2}\b", candidate):
            continue
        if re.match(r"^[A-Z][^,]{0,60},\s*(19|20)\d{2}$", candidate):
            continue
        if len(candidate) >= 12:
            return candidate
    return ""


def surname_from_phrase(phrase: str) -> str:
    phrase = phrase.strip(" .,:;")
    tokens = [token for token in phrase.split() if token]
    if not tokens:
        return ""
    # Corporate authors are cited by their full name (World Health Organization).
    if tokens[-1].strip(".").lower() in ORG_SUFFIXES:
        return " ".join(tokens).strip(" .")
    trailing_initials: list[str] = []
    while tokens and re.fullmatch(r"[A-Z]{1,3}\.?", tokens[-1]):
        trailing_initials.append(tokens.pop())
    if trailing_initials and tokens:
        # Vancouver: "van Eck NJ" -> "van Eck"; "Smith J" -> "Smith".
        return " ".join(tokens).strip(" .")
    return tokens[-1].strip(" .") if tokens else ""


def extract_surname(text: str) -> str:
    clean = re.sub(r"^\[\d+\]\s*|^\d+[.)]\s*", "", text).strip()
    match = YEAR_PAREN_RE.search(clean)
    prefix = clean[: match.start()] if match else clean.split(". ")[0]
    prefix = prefix.strip(" .,:;")
    if not prefix:
        return ""
    if "," in prefix:
        return surname_from_phrase(prefix.split(",")[0])
    return surname_from_phrase(prefix)


def normalize_name(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z]", "", text.lower())


def normalize_title(text: str) -> str:
    text = html.unescape(re.sub(r"<[^>]+>", " ", text or ""))
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def method_like(display: str) -> bool:
    """True for guideline/tool mentions that are not personal authors."""
    normalized = normalize_name(display)
    return (
        display.isupper()
        or bool(re.search(r"\d", display))
        or normalized in METHOD_CITATION_NAMES
    )


def title_similarity(left: str, right: str) -> float:
    a, b = normalize_title(left), normalize_title(right)
    if not a or not b:
        return 0.0
    ratio = SequenceMatcher(None, a, b).ratio()
    a_tokens, b_tokens = set(a.split()), set(b.split())
    jaccard = len(a_tokens & b_tokens) / len(a_tokens | b_tokens) if a_tokens | b_tokens else 0.0
    return round(max(ratio, jaccard), 3)


# --------------------------------------------------------------------------
# Parsers
# --------------------------------------------------------------------------

def build_reference(index: int, raw: str, number: int | None = None) -> Reference:
    clean = strip_markup(raw)
    doi = extract_doi(clean)
    year = extract_year(clean, doi)
    return Reference(
        index=index,
        raw=clean,
        number=number,
        doi=doi,
        year=year,
        title=extract_title(clean, doi, year),
        surname=extract_surname(clean),
    )


def split_entries(block: str) -> list[Reference]:
    entries: list[tuple[int | None, str]] = []
    current: str | None = None
    current_number: int | None = None

    def flush() -> None:
        nonlocal current, current_number
        if current and current.strip():
            entries.append((current_number, current.strip()))
        current, current_number = None, None

    for line in block.splitlines():
        if re.fullmatch(r"\s*(?:-{3,}|\*{3,}|_{3,})\s*", line):
            # A horizontal rule ends the reference list; anything after it is
            # gate text or a note, not a reference entry.
            flush()
            break
        if not line.strip():
            flush()
            continue
        numbered = NUMBERED_RE.match(line)
        if numbered:
            flush()
            current_number = int(numbered.group(1) or numbered.group(2))
            current = numbered.group(3).strip()
            continue
        bullet = BULLET_RE.match(line)
        if bullet:
            flush()
            current = bullet.group(1).strip()
            continue
        if current is not None:
            current += " " + line.strip()
        else:
            current = line.strip()
    flush()

    return [build_reference(i, raw, number) for i, (number, raw) in enumerate(entries, 1)]


def parse_markdown(text: str, section: str | None = None) -> tuple[str, list[Reference]]:
    lines = text.splitlines()
    ref_index = None
    ref_level = None
    for i, line in enumerate(lines):
        match = HEADING_RE.match(line)
        if not match:
            continue
        title = match.group(2).strip()
        if (section and title.lower() == section.lower()) or (
            not section and REF_HEADING_RE.match(title)
        ):
            ref_index, ref_level = i, len(match.group(1))
            break
    if ref_index is None:
        raise ParseError(
            "no references heading found; add '## References' or pass --section NAME"
        )

    end = len(lines)
    for j in range(ref_index + 1, len(lines)):
        match = HEADING_RE.match(lines[j])
        if match and len(match.group(1)) <= ref_level:
            end = j
            break

    body = "\n".join(lines[:ref_index] + lines[end:])
    block = "\n".join(lines[ref_index + 1 : end])
    return body, split_entries(block)


def parse_bib(text: str) -> list[Reference]:
    refs: list[Reference] = []
    entries = list(re.finditer(r"@\w+\s*\{\s*([^,]+),", text))
    for i, match in enumerate(entries, 1):
        start = match.end()
        nxt = text.find("@", start)
        block = text[start : nxt if nxt != -1 else len(text)]
        fields = {
            key.lower(): strip_markup(value)
            for key, value in re.findall(
                r"(\w+)\s*=\s*[\{\"]((?:[^{}\"]|\{[^{}]*\})*)[\}\"]", block, re.S
            )
        }
        year_raw = re.search(r"(?:19|20)\d{2}", fields.get("year", ""))
        authors = fields.get("author", "")
        surname = authors.split(",")[0].strip() if authors else ""
        refs.append(
            Reference(
                index=i,
                raw=" ".join(filter(None, [fields.get("title", ""), fields.get("doi", "")])),
                number=i,
                doi=extract_doi(fields.get("doi", "")),
                year=int(year_raw.group(0)) if year_raw else None,
                title=fields.get("title", ""),
                surname=surname,
            )
        )
    return refs


def parse_ris(text: str) -> list[Reference]:
    refs: list[Reference] = []
    current: dict = {}

    def flush() -> None:
        nonlocal current
        if not current:
            return
        authors = current.get("AU", [])
        surname = authors[0].split(",")[0].strip() if authors else ""
        refs.append(
            Reference(
                index=len(refs) + 1,
                raw=" ".join(filter(None, [current.get("title", ""), current.get("doi", "")])),
                number=len(refs) + 1,
                doi=current.get("doi", ""),
                year=current.get("year"),
                title=current.get("title", ""),
                surname=surname,
            )
        )
        current = {}

    for line in text.splitlines():
        match = re.match(r"^([A-Z][A-Z0-9])  - (.*)$", line)
        if not match:
            continue
        tag, value = match.group(1), match.group(2).strip()
        if tag == "TY":
            flush()
            current = {"AU": []}
        elif tag == "ER":
            flush()
        elif tag in {"AU", "A1"}:
            current.setdefault("AU", []).append(value)
        elif tag in {"TI", "T1"}:
            current["title"] = strip_markup(value)
        elif tag in {"PY", "Y1"}:
            year = re.search(r"(?:19|20)\d{2}", value)
            current["year"] = int(year.group(0)) if year else None
        elif tag == "DO":
            current["doi"] = extract_doi(value)
    flush()
    return refs


def parse_plain(text: str) -> list[Reference]:
    return split_entries(text)


def load_references(path: Path, section: str | None) -> tuple[str, list[Reference]]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except FileNotFoundError as exc:
        raise ParseError(f"file not found: {path}") from exc
    suffix = path.suffix.lower()
    if suffix in {".bib", ".bibtex"}:
        return "", parse_bib(text)
    if suffix == ".ris":
        return "", parse_ris(text)
    if suffix in {".md", ".markdown"}:
        return parse_markdown(text, section)
    return "", parse_plain(text)


# --------------------------------------------------------------------------
# Citation extraction
# --------------------------------------------------------------------------

def expand_numeric(group: str) -> set[int]:
    numbers: set[int] = set()
    for part in re.split(r"\s*[,;]\s*", group):
        part = part.strip()
        if not part:
            continue
        span = re.fullmatch(r"(\d+)\s*[-\u2013]\s*(\d+)", part)
        if span:
            low, high = int(span.group(1)), int(span.group(2))
            if low <= high and high - low <= 50:
                numbers.update(range(low, high + 1))
            else:
                numbers.update({low, high})
        elif part.isdigit():
            numbers.add(int(part))
    return numbers


def numeric_citations(body: str) -> set[int]:
    keys: set[int] = set()
    for match in re.finditer(r"\[(\d+(?:\s*[,;\u2013-]\s*\d+)*)\]", body):
        keys |= expand_numeric(match.group(1))
    return keys


def authoryear_citations(body: str) -> dict[tuple[str, int], str]:
    """Map (normalised citation name, year) to the name as written."""
    keys: dict[tuple[str, int], str] = {}

    def add(names: str, year: int) -> None:
        display = names.strip()
        display = re.sub(r"^(see|e\.g\.|i\.e\.|cf\.)[,:\s]+", "", display, flags=re.I).strip()
        display = re.sub(r"\bet al\.?$", "", display, flags=re.I).strip()
        if not display or len(display) > 120 or display[0].isdigit():
            return
        if not re.search(r"[A-Za-z]", display):
            return
        keys[(normalize_name(display), year)] = display

    for group in re.finditer(r"\(([^()]*)\)", body):
        for part in group.group(1).split(";"):
            match = re.match(
                r"\s*(.+?),\s*((?:19|20)\d{2})[a-z]?"
                r"(?:,\s*pp?\.?\s*\d+(?:\s*[-\u2013]\s*\d+)?)?\s*$",
                part,
            )
            if match:
                add(match.group(1), int(match.group(2)))

    for match in re.finditer(
        r"\b([A-Z][\w'\u2019-]+)(?:\s+et al\.?)?\s*"
        r"\(((?:19|20)\d{2})[a-z]?"
        r"(?:,\s*pp?\.?\s*\d+(?:\s*[-\u2013]\s*\d+)?)?\)",
        body,
    ):
        keys[(normalize_name(match.group(1)), int(match.group(2)))] = match.group(1)

    return keys


def check_offline(body: str, refs: list[Reference]) -> OfflineResult:
    result = OfflineResult(refs=refs, n_with_doi=sum(1 for r in refs if r.doi))
    if not refs:
        result.errors.append("no reference entries were parsed")
        return result

    by_number: dict[int, Reference] = {}
    for ref in refs:
        number = ref.number if ref.number is not None else ref.index
        if number in by_number:
            result.warnings.append(f"duplicate reference number [{number}]")
        by_number[number] = ref

    doi_index: dict[str, list[int]] = {}
    for ref in refs:
        if ref.doi:
            doi_index.setdefault(ref.doi.lower(), []).append(ref.index)
    for doi, indexes in doi_index.items():
        if len(indexes) > 1:
            result.errors.append(f"duplicate DOI {doi} in references {indexes}")

    for ref in refs:
        if not ref.year:
            result.warnings.append(f"reference {ref.index}: no publication year parsed")
        if not ref.title:
            result.warnings.append(f"reference {ref.index}: no title parsed")

    numeric = numeric_citations(body)
    authoryear = authoryear_citations(body)
    result.n_citations = len(numeric) + len(authoryear)

    if not numeric and not authoryear:
        result.style = "running bibliography (no in-text citations found)"
        result.infos.append(
            "No in-text citations were detected, so citation-list matching was skipped. "
            "Structural checks (duplicates, metadata) still ran."
        )
        return result

    if numeric and authoryear:
        result.style = "mixed"
    elif numeric:
        result.style = "numeric"
    else:
        result.style = "author-year"

    if numeric:
        missing_numbers = sorted(n for n in numeric if n not in by_number)
        if missing_numbers:
            result.errors.append(
                "numeric citation(s) with no reference: "
                + ", ".join(f"[{n}]" for n in missing_numbers[:15])
                + (" ..." if len(missing_numbers) > 15 else "")
            )

    resolved_ref_indexes: set[int] = set()
    if authoryear:
        refs_by_year: dict[int, list[Reference]] = {}
        for ref in refs:
            if ref.surname and ref.year:
                refs_by_year.setdefault(ref.year, []).append(ref)
        unresolved: list[tuple[str, int]] = []
        for (name, year), display in sorted(authoryear.items()):
            tokens = {
                normalize_name(part)
                for part in re.split(r"[\s,&]+", display)
                if normalize_name(part)
            }
            matches = []
            for ref in refs_by_year.get(year, []):
                candidate = normalize_name(ref.surname)
                title_tokens = set(normalize_title(ref.title).split())
                # Direct match for a single/corporate author, a token match
                # inside a multi-author citation ("Smith & Jones" -> Smith),
                # or an acronym used in the reference title ("PRISMA (2021)").
                if candidate and (
                    candidate == name or candidate in tokens or name in title_tokens
                ):
                    matches.append(ref)
            if matches:
                resolved_ref_indexes.update(ref.index for ref in matches)
            else:
                unresolved.append((display, year))
        personal = [(display, year) for display, year in unresolved if not method_like(display)]
        methods = [(display, year) for display, year in unresolved if method_like(display)]
        if personal:
            formatted = ", ".join(f"({display}, {year})" for display, year in personal[:15])
            result.errors.append(
                "author-year citation(s) with no matching reference: "
                + formatted
                + (" ..." if len(personal) > 15 else "")
            )
        if methods:
            formatted = ", ".join(f"({display}, {year})" for display, year in methods[:15])
            result.warnings.append(
                "guideline/tool mention(s) with no obvious reference (verify manually): "
                + formatted
                + (" ..." if len(methods) > 15 else "")
            )

    # Orphans: a reference cited by neither mechanism. Refs whose author/year
    # could not be parsed are only checked in numeric style, where the number
    # is always available.
    cited_indexes: set[int] = set()
    for number in numeric:
        if number in by_number:
            cited_indexes.add(by_number[number].index)
    cited_indexes |= resolved_ref_indexes
    orphan_candidates = [
        ref
        for ref in refs
        if ref.index not in cited_indexes and (numeric or (ref.surname and ref.year))
    ]
    if orphan_candidates:
        result.warnings.append(
            "reference(s) never cited in the text: "
            + ", ".join(f"[{ref.index}]" for ref in orphan_candidates[:15])
            + (" ..." if len(orphan_candidates) > 15 else "")
        )

    return result


# --------------------------------------------------------------------------
# Online verification
# --------------------------------------------------------------------------

def http_json(url: str, timeout: int = 25) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise
            last_error = exc
        except Exception as exc:  # network, timeout, JSON
            last_error = exc
        time.sleep(2 * (attempt + 1))
    raise RuntimeError(str(last_error))


def clean_crossref_text(text: str) -> str:
    """Crossref titles can carry HTML entities, tags and line breaks."""
    text = html.unescape(html.unescape(text or ""))
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def crossref_item_summary(item: dict) -> tuple[str, int | None, str]:
    """Clean title (with subtitle, which Crossref stores separately), year, DOI."""
    title = clean_crossref_text((item.get("title") or [""])[0])
    subtitle = clean_crossref_text((item.get("subtitle") or [""])[0])
    if subtitle and subtitle.lower() not in title.lower():
        title = f"{title}: {subtitle}"
    year = (item.get("issued", {}).get("date-parts") or [[None]])[0][0]
    return title, int(year) if year else None, item.get("DOI", "")


def best_similarity(ref_title: str, item: dict) -> float:
    """Best match against the main title alone or main title + subtitle."""
    main = clean_crossref_text((item.get("title") or [""])[0])
    full = crossref_item_summary(item)[0]
    return max(title_similarity(ref_title, main), title_similarity(ref_title, full))


def verify_one(ref: Reference, mailto: str | None) -> dict:
    if ref.doi:
        try:
            message = http_json("https://api.crossref.org/works/" + urllib.parse.quote(ref.doi))
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return {
                    "index": ref.index,
                    "status": "NOT_FOUND",
                    "doi": ref.doi,
                    "crossref_title": "",
                    "crossref_year": None,
                    "similarity": 0.0,
                    "note": "DOI does not resolve in Crossref",
                }
            return {
                "index": ref.index,
                "status": "ERROR",
                "doi": ref.doi,
                "crossref_title": "",
                "crossref_year": None,
                "similarity": 0.0,
                "note": f"HTTP {exc.code}",
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "index": ref.index,
                "status": "ERROR",
                "doi": ref.doi,
                "crossref_title": "",
                "crossref_year": None,
                "similarity": 0.0,
                "note": str(exc),
            }

        item = message.get("message", {})
        title, year, doi = crossref_item_summary(item)
        similarity = best_similarity(ref.title, item) if ref.title and title else 1.0
        if similarity < 0.55:
            status = "DOI_MISMATCH"
        elif ref.year and year and abs(ref.year - year) > 1:
            status = "YEAR_MISMATCH"
        else:
            status = "VERIFIED"
        return {
            "index": ref.index,
            "status": status,
            "doi": doi or ref.doi,
            "crossref_title": title,
            "crossref_year": year,
            "similarity": similarity,
            "note": "",
        }

    query = DOI_RE.sub("", ref.raw).strip()
    params = {
        "query.bibliographic": query,
        "rows": 3,
        "select": "DOI,title,subtitle,issued",
    }
    if mailto:
        params["mailto"] = mailto
    try:
        data = http_json("https://api.crossref.org/works?" + urllib.parse.urlencode(params))
    except Exception as exc:  # noqa: BLE001
        return {
            "index": ref.index,
            "status": "ERROR",
            "doi": "",
            "crossref_title": "",
            "crossref_year": None,
            "similarity": 0.0,
            "note": str(exc),
        }

    items = data.get("message", {}).get("items", [])
    if not items:
        return {
            "index": ref.index,
            "status": "NO_MATCH",
            "doi": "",
            "crossref_title": "",
            "crossref_year": None,
            "similarity": 0.0,
            "note": "Crossref returned no items",
        }

    best_item = max(items, key=lambda item: best_similarity(ref.title, item))
    title, year, doi = crossref_item_summary(best_item)
    similarity = best_similarity(ref.title, best_item) if ref.title else 0.0
    if similarity >= 0.80:
        status = "YEAR_MISMATCH" if ref.year and year and abs(ref.year - year) > 1 else "VERIFIED"
    elif similarity >= 0.55:
        status = "AMBIGUOUS"
    else:
        status = "NO_MATCH"
    return {
        "index": ref.index,
        "status": status,
        "doi": doi,
        "crossref_title": title,
        "crossref_year": year,
        "similarity": similarity,
        "note": "",
    }


def check_online(
    refs: list[Reference],
    mailto: str | None,
    cache_path: Path | None,
    limit: int | None,
) -> list[dict]:
    cache: dict[str, dict] = {}
    if cache_path and cache_path.exists():
        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            cache = {}

    selected = refs[:limit] if limit else refs
    results: list[dict] = []
    for position, ref in enumerate(selected):
        key = ref.doi.lower() if ref.doi else "q:" + normalize_title(ref.raw)[:200]
        if key in cache:
            result = cache[key]
        else:
            result = verify_one(ref, mailto)
            cache[key] = result
            time.sleep(0.4)
        results.append(result)
        if (position + 1) % 10 == 0:
            print(f"  verified {position + 1}/{len(selected)}", file=sys.stderr)

    if cache_path:
        cache_path.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")
    return results


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------

def render_offline(result: OfflineResult, source: str) -> str:
    lines = [
        "# Reference integrity report",
        "",
        f"**Source:** `{source}`  ",
        "**Mode:** offline (deterministic, no network)  ",
        f"**References parsed:** {len(result.refs)}  ",
        f"**Citation style:** {result.style}  ",
        f"**References with a DOI:** {result.n_with_doi}/{len(result.refs)}",
        "",
        "## Findings",
        "",
    ]
    if not (result.errors or result.warnings or result.infos):
        lines += ["No inconsistencies found.", ""]
        return "\n".join(lines)
    if result.errors:
        lines += [f"### Errors ({len(result.errors)})", ""]
        lines += [f"- {item}" for item in result.errors] + [""]
    if result.warnings:
        lines += [f"### Warnings ({len(result.warnings)})", ""]
        lines += [f"- {item}" for item in result.warnings] + [""]
    if result.infos:
        lines += ["### Notes", ""]
        lines += [f"- {item}" for item in result.infos] + [""]
    lines += [
        "---",
        "",
        "**Gate:** offline consistency must pass before submission. Run with "
        "`--online` for a Crossref spot-check of DOI-bearing references.",
        "",
    ]
    return "\n".join(lines)


def render_online(results: list[dict], refs: list[Reference], source: str) -> str:
    counts: dict[str, int] = {}
    for result in results:
        counts[result["status"]] = counts.get(result["status"], 0) + 1
    errors = sum(counts.get(s, 0) for s in ("NOT_FOUND", "DOI_MISMATCH", "NO_MATCH", "ERROR"))
    warnings = sum(counts.get(s, 0) for s in ("AMBIGUOUS", "YEAR_MISMATCH"))
    summary = " - ".join(f"{status}: {count}" for status, count in sorted(counts.items()))

    lines = [
        "# Reference integrity report (Crossref)",
        "",
        f"**Source:** `{source}`  ",
        f"**Mode:** online (Crossref, checked {date.today().isoformat()})  ",
        f"**References checked:** {len(results)}  ",
        f"**Summary:** {summary or 'none'}  ",
        f"**Errors:** {errors} · **Warnings:** {warnings}",
        "",
        "| # | Status | Similarity | Crossref record | DOI |",
        "|---|---|---:|---|---|",
    ]
    by_index = {ref.index: ref for ref in refs}
    for result in results:
        ref = by_index.get(result["index"])
        short = (ref.raw[:80] + "...") if ref and len(ref.raw) > 80 else (ref.raw if ref else "")
        short = short.replace("|", "\\|")
        crossref = f"{result['crossref_title']} ({result['crossref_year'] or '?'})"
        crossref = crossref.replace("|", "\\|")  # no backslash inside f-string (Python < 3.12)
        lines.append(
            f"| {result['index']} | {result['status']} | {result['similarity']:.2f} | "
            f"{crossref} | {result['doi']} |"
        )
    lines += [
        "",
        "Legend: VERIFIED = title and year agree; YEAR_MISMATCH = DOI/title agree but the "
        "year differs by more than one; AMBIGUOUS = a plausible but not decisive match; "
        "NO_MATCH / DOI_MISMATCH / NOT_FOUND = do not cite without manual resolution; "
        "ERROR = network or API failure, retry.",
        "",
        "---",
        "",
        "**Gate:** every NOT_FOUND, DOI_MISMATCH or NO_MATCH must be resolved or removed. "
        "AMBIGUOUS entries need a manual check against the publisher page.",
        "",
    ]
    return "\n".join(lines)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def selftest() -> None:
    text = (
        "# Test\n\n## 1. Introduction\n\n"
        "Smith (2020) and Jones (2021) are cited; a range is cited [1-2].\n\n"
        "## References\n\n"
        "1. Smith J. A study of things. *Journal of Tests*, 2020. doi:10.1000/abc123\n"
        "2. Jones K. Another study. *Journal of Tests*, 2021. doi:10.1000/def456\n"
    )
    body, refs = parse_markdown(text)
    assert len(refs) == 2, len(refs)
    assert refs[0].doi == "10.1000/abc123", refs[0].doi
    assert refs[0].year == 2020, refs[0].year
    assert refs[1].surname == "Jones", refs[1].surname
    result = check_offline(body, refs)
    assert result.ok, result.errors
    assert not result.warnings, result.warnings

    # Numeric range expansion.
    assert expand_numeric("1,3-5") == {1, 3, 4, 5}

    # Regressions found by verifying shared/method_sources.md online:
    # a page range is not the year (MOOSE: "2000;283(15):2008-2012")...
    moose = ("Stroup DF, Berlin JA. Meta-analysis of observational studies in epidemiology. "
             "*JAMA*. 2000;283(15):2008-2012. doi:10.1001/jama.283.15.2008")
    assert build_reference(1, moose).year == 2000, build_reference(1, moose).year
    # ...Crossref keeps the subtitle separately, and titles may carry markup.
    item = {"title": ["Summarizing systematic reviews"],
            "subtitle": ["methodological development, conduct and reporting of an umbrella review approach"],
            "issued": {"date-parts": [[2015]]}, "DOI": "10.1097/XEB.0000000000000055"}
    aromataris = ("Summarizing systematic reviews: methodological development, conduct and "
                  "reporting of an umbrella review approach")
    assert best_similarity(aromataris, item) >= 0.9, best_similarity(aromataris, item)
    assert crossref_item_summary(item)[0].startswith("Summarizing systematic reviews: methodological")
    marked = {"title": ["Conducting Meta-Analyses in\n   <i>R</i>\n with the <b>metafor</b> Package"]}
    assert crossref_item_summary(marked)[0] == "Conducting Meta-Analyses in R with the metafor Package"
    escaped = {"title": ["Meta-analysis&lt;SUBTITLE&gt;A Proposal&lt;/SUBTITLE&gt;"]}
    assert "<" not in crossref_item_summary(escaped)[0] and "&lt;" not in crossref_item_summary(escaped)[0]

    # Page numbers after the year do not break the citation.
    page_ref = [build_reference(1, "Smith J. A study of things worth citing. 2020.")]
    page_result = check_offline("(Smith, 2020, p. 42)", page_ref)
    assert page_result.ok, page_result.errors

    # Duplicate DOI is an error.
    dup = [
        build_reference(1, "Smith J. One. 2020. doi:10.1000/abc"),
        build_reference(2, "Jones K. Two. 2021. doi:10.1000/abc"),
    ]
    dup_result = check_offline("Body cites nothing.", dup)
    assert any("duplicate DOI" in e for e in dup_result.errors), dup_result.errors

    # Missing citation is an error.
    missing = [build_reference(1, "Smith J. One. 2020. doi:10.1000/abc")]
    missing_result = check_offline("Doe (2022) is not in the list.", missing)
    assert any("no matching reference" in e for e in missing_result.errors), missing_result.errors

    # Running bibliography: no orphan warnings.
    bibliography = [build_reference(1, "Alain C. Ngandjong. A title long enough. 2021.")]
    bib_result = check_offline("No citations here.", bibliography)
    assert bib_result.ok and not bib_result.warnings, (bib_result.errors, bib_result.warnings)
    assert "running bibliography" in bib_result.style

    # Wrapped DOI parenthesis must not leak into the DOI.
    assert extract_doi("(doi:10.1016/0197-2456(86)90046-2)") == "10.1016/0197-2456(86)90046-2"

    # Corporate authors and multi-author citations resolve without false errors.
    corporate = [
        build_reference(1, "World Health Organization. Global report. 2020. doi:10.1000/who"),
        build_reference(2, "Smith J, Jones K. A study of things worth citing. 2021. doi:10.1000/sj"),
    ]
    corp_result = check_offline(
        "(World Health Organization, 2020). (Smith & Jones, 2021).", corporate
    )
    assert corp_result.ok, corp_result.errors
    assert not corp_result.warnings, corp_result.warnings

    # A guideline acronym resolves via the reference title, not a missing-author error.
    prisma = [
        build_reference(
            1,
            "Page MJ. The PRISMA 2020 statement: an updated guideline. 2021. doi:10.1136/bmj.n71",
        )
    ]
    prisma_result = check_offline("Reporting follows PRISMA (2021).", prisma)
    assert prisma_result.ok and not prisma_result.warnings, (
        prisma_result.errors,
        prisma_result.warnings,
    )
    # Without a matching title it is a warning, not a hard error.
    other = [
        build_reference(
            1, "Smith J. A study of things worth citing. 2020. doi:10.1000/other"
        )
    ]
    acronym_result = check_offline("Reporting follows PRISMA (2021).", other)
    assert acronym_result.ok, acronym_result.errors
    assert any("guideline" in warning for warning in acronym_result.warnings)

    # Title similarity sanity.
    assert title_similarity("The PRISMA 2020 statement", "PRISMA 2020 statement") > 0.85

    # .bib parser.
    bib_refs = parse_bib(
        "@article{a, title={A study of things}, author={Smith, John}, year={2020}, doi={10.1000/abc}}"
    )
    assert len(bib_refs) == 1 and bib_refs[0].year == 2020 and bib_refs[0].surname == "Smith"

    print("verify_refs selftest OK (parsing, DOI, citations, duplicates, bibliography, similarity)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check reference-list integrity offline, or against Crossref.")
    parser.add_argument("input", nargs="?", help="review.md, .bib, .ris or .txt")
    parser.add_argument("--section", help="reference heading to use (default: References/Bibliography)")
    parser.add_argument("--online", action="store_true", help="verify against Crossref (network required)")
    parser.add_argument("--mailto", help="contact email for the Crossref polite pool")
    parser.add_argument("--cache", type=Path, help="JSON cache for online lookups")
    parser.add_argument("--limit", type=int, help="verify at most N references online")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    parser.add_argument("--out", type=Path, help="write the Markdown report to this file")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)

    if args.selftest:
        selftest()
        return 0
    if not args.input:
        parser.error("provide a reference file (or --selftest)")

    path = Path(args.input)
    try:
        body, refs = load_references(path, args.section)
    except ParseError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.online:
        results = check_online(refs, args.mailto, args.cache, args.limit)
        report = render_online(results, refs, path.name)
        errors = [r for r in results if r["status"] in ("NOT_FOUND", "DOI_MISMATCH", "NO_MATCH", "ERROR")]
        warnings = [r for r in results if r["status"] in ("AMBIGUOUS", "YEAR_MISMATCH")]
        failed = bool(errors) or (args.strict and bool(warnings))
    else:
        result = check_offline(body, refs)
        report = render_offline(result, path.name)
        errors, warnings = result.errors, result.warnings
        failed = bool(errors) or (args.strict and bool(warnings))

    if args.out:
        args.out.write_text(report, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(report)

    if failed:
        print(f"RESULT: FAIL ({len(errors)} errors, {len(warnings)} warnings)")
        return 1
    print(f"RESULT: PASS ({len(errors)} errors, {len(warnings)} warnings)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
