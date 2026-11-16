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

Optional keys:
    registers                int  - additional records from registers
    removed_before_screening list - [(reason, count)]; overrides the derived
                                    duplicate count
    automation_removed       int  - records removed by automation tools
    other_removed            int  - records removed for other reasons
    reports_included         int  - reports of the included studies
"""

import html
import textwrap

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


def render_prisma(d, out_path):
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
    box_c, h_c = _box(MAIN_X, y_c, MAIN_W, f"Records screened (n = {screened})")
    box_d, h_d = _box(SIDE_X, y_c, SIDE_W, f"Records excluded (n = {excl_ta})",
                      fill=SIDE_FILL)

    y_e = y_c + max(h_c, h_d) + ARROW_GAP
    box_e, h_e = _box(MAIN_X, y_e, MAIN_W,
                      f"Reports sought for retrieval (n = {sought})")
    box_f, h_f = _box(SIDE_X, y_e, SIDE_W,
                      f"Reports not retrieved (n = {not_retrieved})", fill=SIDE_FILL)

    y_g = y_e + max(h_e, h_f) + ARROW_GAP
    box_g, h_g = _box(MAIN_X, y_g, MAIN_W,
                      f"Reports assessed for eligibility (n = {assessed})")
    if excl_ft:
        box_h, h_h = _box(SIDE_X, y_g, SIDE_W, "Reports excluded:",
                          [f"{r} (n = {c})" for r, c in excl_ft], fill=SIDE_FILL)
    else:
        box_h, h_h = _box(SIDE_X, y_g, SIDE_W, "Reports excluded (n = 0)",
                          fill=SIDE_FILL)

    y_i = y_g + max(h_g, h_h) + ARROW_GAP
    included_lines = []
    if reports_included is not None:
        included_lines.append(f"Reports of included studies (n = {reports_included})")
    box_i, h_i = _box(MAIN_X, y_i, MAIN_W,
                      f"Studies included in review (n = {included})",
                      included_lines, fill="#ffffff")

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
    bottom = y_i + h_i + 16
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
        + "".join(parts)
        + "</svg>"
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    return out_path


if __name__ == "__main__":
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
    print("wrote prisma_flow.svg")
