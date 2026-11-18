"""Deterministic PRISMA 2020 flow-diagram generator (stdlib-only, emits SVG).

Layout follows the PRISMA 2020 statement (Page et al., 2021) as implemented by
the R package PRISMA2020: a vertical flow down the left, exclusion boxes to the
right, and phase bands (Identification / Screening / Included) on the left edge.

No renderer, no matplotlib, no network. Feed it the screening counts and it
writes a clean, editable vector SVG. This is the auditable artifact behind the
PRISMA "Study selection" item.

Usage:
    from prisma_flow import render_prisma
    render_prisma(
        {
            "database_records": [("PubMed", 102), ("Scopus", 88)],
            "other_sources": 9,
            "after_dedup": 140,
            "screened": 140,
            "excluded_title_abstract": 95,
            "sought_retrieval": 45,
            "not_retrieved": 4,
            "assessed": 41,
            "excluded_fulltext": [("Wrong population", 12), ("Wrong outcome", 11),
                                  ("Wrong design", 8)],
            "included": 10,
        },
        "prisma_flow.svg",
    )

Variants (``render_prisma(counts, path, variant=...)``):
    "systematic"  PRISMA 2020 new-review flow (default).
    "scoping"     PRISMA-ScR / JBI terminology ("sources of evidence").
    "update"      PRISMA 2020 flow for an updated review: the new studies
                  flow down the main column; the previous version's studies
                  and the combined total are shown at the bottom. Extra keys:
                  previous_studies (int), previous_reports (int, optional).

Optional keys:
    registers                int  - additional records from registers
    removed_before_screening list - [(reason, count)]; overrides the derived
                                    duplicate count
    automation_removed       int  - records removed by automation tools
    other_removed            int  - records removed for other reasons
    reports_included         int  - reports of the included studies
"""

import argparse
import html
import json
import sys
from pathlib import Path
import textwrap
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _textio import read_text
import itertools

WIDTH = 1120
PHASE_X, PHASE_W = 10, 112
MAIN_X, MAIN_W = 150, 430
SIDE_X, SIDE_W = 640, 455

LINE = "#1a1a1a"
BORDER = "#333333"
GREY = "#555555"
SIDE_FILL = "#f4f6f8"
PHASE_FILL = "#eceff1"

LH = 17          # detail line height
BOX_PAD_TOP = 21
BOX_PAD_BOTTOM = 12
ARROW_GAP = 44


def _esc(s):
    return html.escape(str(s))


def _text(x, y, s, size=11.5, weight="400", fill=LINE, anchor="start", italic=False):
    style = ' font-style="italic"' if italic else ""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
        f'font-family="Arial, Helvetica, sans-serif" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}"{style}>{_esc(s)}</text>'
    )


def _wrap(text, width_px, font_px=11.5):
    """Rough pixel-aware wrapping (no font metrics available in stdlib)."""
    approx = max(12, int(width_px / (font_px * 0.55)))
    return textwrap.wrap(str(text), approx) or [""]


def _box(x, y, w, title, lines=None, fill="#ffffff"):
    """Draw a titled box with optional detail lines. Returns (svg, height)."""
    wrapped = []
    for line in lines or []:
        wrapped.extend(_wrap(line, w - 30))
    h = BOX_PAD_TOP + LH * (1 + len(wrapped)) + BOX_PAD_BOTTOM
    out = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" '
        f'fill="{fill}" stroke="{BORDER}" stroke-width="1.4"/>',
        _text(x + 14, y + BOX_PAD_TOP, title, size=12.5, weight="600"),
    ]
    ty = y + BOX_PAD_TOP + LH
    for part in wrapped:
        out.append(_text(x + 26, ty, part))
        ty += LH
    return "".join(out), h


def _arrow(x1, y1, x2, y2):
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{LINE}" stroke-width="1.3" marker-end="url(#arrow)"/>'
    )


def _phase_band(x, y1, y2, label):
    """Grey phase band with the label rotated 90 degrees, as in PRISMA2020."""
    cx = x + PHASE_W / 2
    cy = (y1 + y2) / 2
    return (
        f'<rect x="{x}" y="{y1:.1f}" width="{PHASE_W}" height="{y2 - y1:.1f}" '
        f'fill="{PHASE_FILL}"/>'
        f'<text x="{cx:.1f}" y="{cy:.1f}" transform="rotate(-90 {cx:.1f} {cy:.1f})" '
        f'text-anchor="middle" font-family="Arial, Helvetica, sans-serif" '
        f'font-size="12.5" font-weight="700" fill="#37474f">{_esc(label)}</text>'
    )


VARIANTS = ("systematic", "scoping", "update")

LABELS = {
    "systematic": {
        "screened": "Records screened", "excluded_ta": "Records excluded",
        "sought": "Reports sought for retrieval", "not_retrieved": "Reports not retrieved",
        "assessed": "Reports assessed for eligibility", "excl_ft": "Reports excluded:",
        "excl_ft_zero": "Reports excluded", "included": "Studies included in review",
    },
    "scoping": {
        "screened": "Records screened", "excluded_ta": "Records excluded",
        "sought": "Sources of evidence sought for retrieval",
        "not_retrieved": "Sources of evidence not retrieved",
        "assessed": "Sources of evidence assessed for eligibility",
        "excl_ft": "Sources of evidence excluded:",
        "excl_ft_zero": "Sources of evidence excluded",
        "included": "Sources of evidence included in review",
    },
}
LABELS["update"] = dict(LABELS["systematic"], included="New studies included in review")


def _main_cx(x, w):
    return x + w / 2


def render_prisma(d, out_path, variant="systematic"):
    """Render a standard PRISMA 2020 flow diagram from screening counts.

    Required keys (all integers except where noted):
        database_records : list of (name, count)
        other_sources    : int
        after_dedup      : int
        screened         : int
        excluded_title_abstract : int
        sought_retrieval : int
        not_retrieved    : int
        assessed         : int
        excluded_fulltext: list of (reason, count)
        included         : int
    """
    if variant not in VARIANTS:
        raise ValueError("variant must be one of {}".format(", ".join(VARIANTS)))
    L = LABELS[variant]
    db = list(d["database_records"])
    n_db = sum(c for _, c in db)
    n_other = int(d.get("other_sources", 0) or 0)
    n_reg = int(d.get("registers", 0) or 0)
    identified = n_db + n_other + n_reg
    after_dedup = int(d["after_dedup"])

    # ---------------- Identification ----------------
    ident_lines = [f"{name} (n = {c})" for name, c in db] or ["Databases (n = 0)"]
    if n_reg:
        ident_lines.append(f"Registers (n = {n_reg})")
    if n_other:
        ident_lines.append(f"Other sources (n = {n_other})")

    if d.get("removed_before_screening") is not None:
        removed_lines = [f"{r} (n = {c})" for r, c in d["removed_before_screening"]]
    else:
        removed_lines = [f"Duplicate records removed (n = {max(0, identified - after_dedup)})"]
        if d.get("automation_removed"):
            removed_lines.append(
                f"Marked ineligible by automation tools (n = {d['automation_removed']})")
        if d.get("other_removed"):
            removed_lines.append(f"Removed for other reasons (n = {d['other_removed']})")

    # ---------------- Screening ----------------
    screened = int(d["screened"])
    excl_ta = int(d["excluded_title_abstract"])
    sought = int(d["sought_retrieval"])
    not_retrieved = int(d["not_retrieved"])
    assessed = int(d["assessed"])
    excl_ft = list(d.get("excluded_fulltext") or [])
    included = int(d["included"])
    reports_included = d.get("reports_included")

    # ---------------- Geometry ----------------
    y_a = 64
    box_a, h_a = _box(MAIN_X, y_a, MAIN_W, "Records identified from:", ident_lines)
    box_b, h_b = _box(SIDE_X, y_a, SIDE_W, "Records removed before screening:",
                      removed_lines, fill=SIDE_FILL)

    y_c = y_a + max(h_a, h_b) + ARROW_GAP
    box_c, h_c = _box(MAIN_X, y_c, MAIN_W, f"{L['screened']} (n = {screened})")
    box_d, h_d = _box(SIDE_X, y_c, SIDE_W, f"{L['excluded_ta']} (n = {excl_ta})",
                      fill=SIDE_FILL)

    y_e = y_c + max(h_c, h_d) + ARROW_GAP
    box_e, h_e = _box(MAIN_X, y_e, MAIN_W,
                      f"{L['sought']} (n = {sought})")
    box_f, h_f = _box(SIDE_X, y_e, SIDE_W,
                      f"{L['not_retrieved']} (n = {not_retrieved})", fill=SIDE_FILL)

    y_g = y_e + max(h_e, h_f) + ARROW_GAP
    box_g, h_g = _box(MAIN_X, y_g, MAIN_W,
                      f"{L['assessed']} (n = {assessed})")
    if excl_ft:
        box_h, h_h = _box(SIDE_X, y_g, SIDE_W, L["excl_ft"],
                          [f"{r} (n = {c})" for r, c in excl_ft], fill=SIDE_FILL)
    else:
        box_h, h_h = _box(SIDE_X, y_g, SIDE_W, L["excl_ft_zero"] + " (n = 0)",
                          fill=SIDE_FILL)

    y_i = y_g + max(h_g, h_h) + ARROW_GAP
    included_lines = []
    if reports_included is not None:
        included_lines.append(f"Reports of included studies (n = {reports_included})")
    box_i, h_i = _box(MAIN_X, y_i, MAIN_W,
                      f"{L['included']} (n = {included})",
                      included_lines, fill="#ffffff")
    extra_boxes = ""
    extra_parts = []
    y_end = y_i + h_i
    if variant == "update":
        prev = int(d.get("previous_studies", 0) or 0)
        prev_lines = []
        if d.get("previous_reports") is not None:
            prev_lines.append(f"Reports of previous studies (n = {d['previous_reports']})")
        box_p, h_p = _box(SIDE_X, y_i, SIDE_W,
                          f"Studies included in previous version (n = {prev})",
                          prev_lines, fill=SIDE_FILL)
        y_t = y_i + max(h_i, h_p) + ARROW_GAP
        box_t, h_t = _box(MAIN_X, y_t, MAIN_W,
                          f"Total studies included in review (n = {included + prev})")
        extra_boxes = box_p + box_t
        px = SIDE_X + SIDE_W / 2
        extra_parts = [
            _arrow(_main_cx(MAIN_X, MAIN_W), y_i + h_i, _main_cx(MAIN_X, MAIN_W), y_t),
            f'<line x1="{px:.1f}" y1="{y_i + h_p:.1f}" x2="{px:.1f}" '
            f'y2="{y_t + h_t / 2:.1f}" stroke="{LINE}" stroke-width="1.3"/>',
            _arrow(px, y_t + h_t / 2, MAIN_X + MAIN_W, y_t + h_t / 2),
        ]
        y_end = y_t + h_t

    # ---------------- Connectors ----------------
    main_cx = MAIN_X + MAIN_W / 2
    parts = [
        _arrow(main_cx, y_a + h_a, main_cx, y_c),
        _arrow(MAIN_X + MAIN_W, y_a + min(h_a, h_b) / 2, SIDE_X,
               y_a + min(h_a, h_b) / 2),
        _arrow(MAIN_X + MAIN_W, y_c + min(h_c, h_d) / 2, SIDE_X,
               y_c + min(h_c, h_d) / 2),
        _arrow(main_cx, y_c + h_c, main_cx, y_e),
        _arrow(MAIN_X + MAIN_W, y_e + min(h_e, h_f) / 2, SIDE_X,
               y_e + min(h_e, h_f) / 2),
        _arrow(main_cx, y_e + h_e, main_cx, y_g),
        _arrow(MAIN_X + MAIN_W, y_g + min(h_g, h_h) / 2, SIDE_X,
               y_g + min(h_g, h_h) / 2),
        _arrow(main_cx, y_g + h_g, main_cx, y_i),
    ]

    # ---------------- Phase bands ----------------
    top = y_a - 16
    boundary_1 = y_c - ARROW_GAP / 2
    boundary_2 = y_i - ARROW_GAP / 2
    bottom = y_end + 16
    height = bottom + 10

    parts.insert(0, _phase_band(PHASE_X, top, boundary_1, "Identification"))
    parts.insert(1, _phase_band(PHASE_X, boundary_1, boundary_2, "Screening"))
    parts.insert(2, _phase_band(PHASE_X, boundary_2, bottom, "Included"))
    for b in (boundary_1, boundary_2):
        parts.insert(3, f'<line x1="{PHASE_X}" y1="{b:.1f}" x2="{WIDTH - 20}" '
                        f'y2="{b:.1f}" stroke="#cfd8dc" stroke-width="1"/>')

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height:.0f}" '
        f'viewBox="0 0 {WIDTH} {height:.0f}">'
        "<defs>"
        '<marker id="arrow" markerWidth="9" markerHeight="9" refX="7" refY="3" '
        'orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="' + LINE + '"/></marker>'
        "</defs>"
        '<rect width="100%" height="100%" fill="#ffffff"/>'
        + box_a + box_b + box_c + box_d + box_e + box_f + box_g + box_h + box_i
        + extra_boxes
        + "".join(parts) + "".join(extra_parts)
        + "</svg>"
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    return out_path


SVG_NS = "{http://www.w3.org/2000/svg}"
EXPECTED_ARROWS = {"systematic": 8, "scoping": 8, "update": 10}
REQUIRED_TEXT = {
    "systematic": ["Records identified from", "Records screened", "Studies included in review"],
    "scoping": ["Sources of evidence assessed for eligibility",
                "Sources of evidence included in review"],
    "update": ["New studies included in review", "Studies included in previous version",
               "Total studies included in review"],
}


def validate_svg(path, variant="systematic"):
    """Structural check of a PRISMA SVG (parsed as XML, not substring search).

    Verifies: well-formed SVG, viewBox matches size, boxes inside the canvas
    and non-overlapping, text anchored inside a box (and not wider than it),
    main-column boxes ordered top to bottom, the arrow count, the three phase
    bands, and the variant's required labels. Returns a list of problems.
    """
    problems = []
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as exc:
        return [f"not a readable SVG: {exc}"]
    if root.tag != SVG_NS + "svg":
        return ["root element is not <svg>"]
    vb = [float(v) for v in root.get("viewBox", "0 0 0 0").split()]
    w, h = float(root.get("width", 0)), float(root.get("height", 0))
    if vb[2:] != [w, h]:
        problems.append("viewBox does not match width/height")

    boxes, bands = [], []
    for r in root.iter(SVG_NS + "rect"):
        if r.get("stroke"):
            boxes.append(tuple(float(r.get(k)) for k in ("x", "y", "width", "height")))
        elif r.get("x") is not None:
            bands.append(r)
    if len(bands) != 3:
        problems.append(f"expected 3 phase bands, found {len(bands):d}")
    for x, y, bw, bh in boxes:
        if x < 0 or y < 0 or x + bw > w or y + bh > h:
            problems.append(f"box at ({x:g},{y:g}) lies outside the canvas")
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            if (a[0] < b[0] + b[2] and b[0] < a[0] + a[2]
                    and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]):
                problems.append(f"boxes overlap at ({a[0]:g},{a[1]:g}) and ({b[0]:g},{b[1]:g})")

    texts = []
    for t in root.iter(SVG_NS + "text"):
        if t.get("transform"):          # rotated phase label
            continue
        x, y = float(t.get("x")), float(t.get("y"))
        size = float(t.get("font-size", 11.5))
        content = "".join(t.itertext())
        texts.append(content)
        host = [b for b in boxes if b[0] <= x <= b[0] + b[2] and b[1] <= y <= b[1] + b[3]]
        if not host:
            problems.append(f"text {content[:40]!r} is not inside any box")
        elif x + len(content) * size * 0.6 > host[0][0] + host[0][2] + 4:
            problems.append(f"text {content[:40]!r} overflows its box")

    main_x = min(b[0] for b in boxes) if boxes else 0
    col = sorted(b[1] for b in boxes if b[0] == main_x)
    if any(b2 <= b1 for b1, b2 in itertools.pairwise(col)):
        problems.append("main column boxes are not ordered top to bottom")
    arrows = sum(1 for ln in root.iter(SVG_NS + "line") if ln.get("marker-end"))
    if arrows != EXPECTED_ARROWS[variant]:
        problems.append(f"expected {EXPECTED_ARROWS[variant]:d} arrows for {variant}, found {arrows:d}")
    for needle in REQUIRED_TEXT[variant]:
        if not any(needle in t for t in texts):
            problems.append(f"missing label {needle!r}")
    return problems


_SAMPLE = {
    "database_records": [("PubMed", 102), ("Scopus", 88)],
    "other_sources": 9,
    "after_dedup": 140,
    "screened": 140,
    "excluded_title_abstract": 95,
    "sought_retrieval": 45,
    "not_retrieved": 4,
    "assessed": 41,
    "excluded_fulltext": [("Wrong population", 12), ("Wrong outcome", 11),
                          ("Wrong design", 8)],
    "included": 10,
}


def _selftest():
    import os
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        for variant in VARIANTS:
            data = dict(_SAMPLE, previous_studies=7, previous_reports=9)
            path = os.path.join(d, variant + ".svg")
            render_prisma(data, path, variant)
            problems = validate_svg(path, variant)
            assert not problems, (variant, problems)
        with open(os.path.join(d, "update.svg"), encoding="utf-8") as f:
            broken = f.read().replace('width="430"', 'width="2000"', 1)
        bad = os.path.join(d, "bad.svg")
        with open(bad, "w", encoding="utf-8") as f:
            f.write(broken)
        assert validate_svg(bad, "update"), "oversized box must be detected"
        assert validate_svg(os.path.join(d, "nope.svg")), "missing file must be reported"
        assert check_counts(_SAMPLE) == [], check_counts(_SAMPLE)
        assert check_counts(dict(_SAMPLE, included=9)), "off-by-one must be reported"
        assert check_counts(dict(_SAMPLE, removed_before_screening=[("Duplicates", 50)]))
        try:
            render_prisma(_SAMPLE, os.path.join(d, "x.svg"), "bogus")
        except ValueError:
            pass
        else:
            raise AssertionError("unknown variant must raise")
    print("prisma_flow selftest OK ({})".format(", ".join(VARIANTS)))


def check_counts(d):
    """Arithmetic checks on the flow; returns a list of human-readable problems.

    PRISMA numbers must add up at every box. A mismatch usually means a
    record was lost between tools, which reviewers notice immediately.
    """
    problems = []

    def num(key):
        value = d.get(key)
        return int(value) if value is not None else None

    identified = sum(int(c) for _, c in d.get("database_records", [])) \
        + int(d.get("other_sources", 0) or 0) + int(d.get("registers", 0) or 0)
    removed = d.get("removed_before_screening")
    if removed is not None and num("after_dedup") is not None:
        removed_n = sum(int(c) for _, c in removed)
        if identified - removed_n != num("after_dedup"):
            problems.append(f'identified ({identified:d}) - removed before screening ({removed_n:d}) != after_dedup ({num("after_dedup"):d})')
    if num("after_dedup") is not None and num("screened") is not None:
        expected = num("after_dedup") - int(d.get("automation_removed", 0) or 0) \
            - int(d.get("other_removed", 0) or 0)
        if removed is None and num("screened") != expected:
            problems.append(f'screened ({num("screened"):d}) != after_dedup minus other removals ({expected:d})')
        if removed is not None and num("screened") != num("after_dedup"):
            problems.append(f'screened ({num("screened"):d}) != after_dedup ({num("after_dedup"):d})')
    checks = [
        ("screened", ["excluded_title_abstract", "sought_retrieval"]),
        ("sought_retrieval", ["not_retrieved", "assessed"]),
    ]
    for total, parts in checks:
        if num(total) is not None and all(num(p) is not None for p in parts):
            if num(total) != sum(num(p) for p in parts):
                problems.append(f'{total} ({num(total):d}) != {" + ".join(parts)} ({sum(num(p) for p in parts):d})')
    if num("assessed") is not None and num("included") is not None:
        excl = sum(int(c) for _, c in d.get("excluded_fulltext", []) or [])
        if num("assessed") != excl + num("included"):
            problems.append(f'assessed ({num("assessed"):d}) != excluded at full text ({excl:d}) + included ({num("included"):d})')
    return problems


def load_counts(paths):
    """Merge one or more counts JSON files (later files override earlier ones)."""
    data = {}
    for path in paths:
        data.update(json.loads(read_text(path)))
    for key in ("database_records", "excluded_fulltext", "removed_before_screening"):
        if data.get(key):
            data[key] = [tuple(x) for x in data[key]]
    return data


def main(argv=None):
    p = argparse.ArgumentParser(description="PRISMA 2020 flow diagram (SVG).")
    p.add_argument("input", nargs="*",
                   help="counts JSON file(s), merged in order: e.g. the dedup "
                        "prisma_identification.json then your screening counts "
                        "(default: built-in demo)")
    p.add_argument("--strict", action="store_true",
                   help="exit 1 if the counts do not add up")
    p.add_argument("--variant", choices=VARIANTS, default="systematic")
    p.add_argument("--out", default="prisma_flow.svg")
    p.add_argument("--validate", metavar="SVG", help="structurally validate an SVG and exit")
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args(argv)
    if a.selftest:
        _selftest()
        return 0
    if a.validate:
        problems = validate_svg(a.validate, a.variant)
        for problem in problems:
            print("FAIL: " + problem)
        print(f'RESULT: {"FAIL" if problems else "PASS"}')
        return 1 if problems else 0
    try:
        data = load_counts(a.input) if a.input else dict(_SAMPLE, previous_studies=7)
        problems = check_counts(data)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"error: cannot use the counts file ({type(exc).__name__}: {exc}). "
              "Expected JSON with database_records, after_dedup, screened, ...; "
              "see examples/systematic-review-demo/screening_counts.json", file=sys.stderr)
        return 2
    for problem in problems:
        print("WARNING: counts do not add up: " + problem)
    try:
        render_prisma(data, a.out, a.variant)
    except (KeyError, TypeError, ValueError) as exc:
        print(f"error: the counts file is missing or has a bad field ({type(exc).__name__}: {exc}); "
              "required: database_records, after_dedup, screened, excluded_title_abstract, "
              "sought_retrieval, not_retrieved, assessed, included", file=sys.stderr)
        return 2
    print(f"wrote {a.out}")
    return 1 if (a.strict and problems) else 0


if __name__ == "__main__":
    sys.exit(main())
