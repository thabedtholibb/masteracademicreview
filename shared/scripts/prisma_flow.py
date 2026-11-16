"""Deterministic PRISMA 2020 flow-diagram generator (stdlib-only, emits SVG).

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
"""

import html

BOX_W = 260
BOX_H = 40
COL_X = [40, 380, 720, 1060, 1400]
LINE = "#1a1a1a"
GREY = "#555555"


def _box(x, y, w, h, text, fill="#ffffff", bold=False):
    weight = "600" if bold else "400"
    size = 13 if not bold else 14
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" '
        f'fill="{fill}" stroke="{LINE}" stroke-width="1.5"/>'
        f'<text x="{x + w / 2}" y="{y + h / 2 + 5}" text-anchor="middle" '
        f'font-family="Arial, sans-serif" font-size="{size}" font-weight="{weight}" '
        f'fill="{LINE}">{html.escape(text)}</text>'
    )


def _label(x, y, text, anchor="start"):
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="Arial, sans-serif" '
        f'font-size="12" font-style="italic" fill="{GREY}">{html.escape(text)}</text>'
    )


def _arrow(x1, y1, x2, y2):
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{LINE}" stroke-width="1.5" marker-end="url(#arrow)"/>'
    )


def render_prisma(d, out_path):
    """Render a PRISMA flow diagram from screening counts.

    `d` keys (all integers except where noted):
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
    db = d["database_records"]
    n_db = sum(c for _, c in db)
    n_other = d.get("other_sources", 0)

    parts = []

    # --- Identification column ---
    col = 0
    y = 60
    parts.append(_label(COL_X[col], y - 12, "Identification"))
    # databases box grows with number of rows
    rows = max(1, len(db))
    h = BOX_H * rows + 6 * (rows - 1)
    parts.append(_box(COL_X[col], y, BOX_W, h, "Records identified from databases"))
    for i, (name, count) in enumerate(db):
        parts.append(_label(COL_X[col] + 12, y + 26 + i * (BOX_H + 6),
                            f"{name} (n = {count})"))
    parts.append(_box(COL_X[col], y + h + 12, BOX_W, BOX_H,
                      f"Records identified from other sources (n = {n_other})"))
    dedup_y = y + h + 12 + BOX_H + 14

    # --- After duplicates ---
    parts.append(_box(COL_X[col], dedup_y, BOX_W, BOX_H,
                      f"Records after duplicates removed (n = {d['after_dedup']})"))
    parts.append(_arrow(COL_X[col] + BOX_W / 2, dedup_y + BOX_H + 8,
                        COL_X[col] + BOX_W / 2, dedup_y + BOX_H + 34))

    # --- Screening column ---
    col = 1
    screen_y = dedup_y + BOX_H + 34
    parts.append(_label(COL_X[col], screen_y - 12, "Screening"))
    parts.append(_box(COL_X[col], screen_y, BOX_W, BOX_H,
                      f"Records screened (n = {d['screened']})"))
    parts.append(_arrow(COL_X[col] + BOX_W / 2, screen_y + BOX_H + 8,
                        COL_X[col] + BOX_W / 2, screen_y + BOX_H + 34))
    parts.append(_box(COL_X[col], screen_y + BOX_H + 34, BOX_W, BOX_H,
                      f"Records excluded (n = {d['excluded_title_abstract']})"))

    # horizontal connector: after-dedup -> screened
    parts.append(_arrow(COL_X[col - 1] + BOX_W, dedup_y + BOX_H / 2,
                        COL_X[col], screen_y + BOX_H / 2))

    # --- Retrieval column ---
    col = 2
    ret_y = screen_y
    parts.append(_label(COL_X[col], ret_y - 12, "Retrieval"))
    parts.append(_box(COL_X[col], ret_y, BOX_W, BOX_H,
                      f"Reports sought for retrieval (n = {d['sought_retrieval']})"))
    parts.append(_arrow(COL_X[col] + BOX_W / 2, ret_y + BOX_H + 8,
                        COL_X[col] + BOX_W / 2, ret_y + BOX_H + 34))
    parts.append(_box(COL_X[col], ret_y + BOX_H + 34, BOX_W, BOX_H,
                      f"Reports not retrieved (n = {d['not_retrieved']})"))
    parts.append(_arrow(COL_X[col - 1] + BOX_W, screen_y + BOX_H / 2,
                        COL_X[col], ret_y + BOX_H / 2))

    # --- Eligibility column ---
    col = 3
    elig_y = ret_y
    parts.append(_label(COL_X[col], elig_y - 12, "Eligibility"))
    parts.append(_box(COL_X[col], elig_y, BOX_W, BOX_H,
                      f"Reports assessed for eligibility (n = {d['assessed']})"))
    excl = d.get("excluded_fulltext", [])
    excl_rows = max(1, len(excl))
    h2 = BOX_H * excl_rows + 6 * (excl_rows - 1)
    parts.append(_box(COL_X[col], elig_y + BOX_H + 34, BOX_W, h2,
                      "Reports excluded"))
    for i, (reason, count) in enumerate(excl):
        parts.append(_label(COL_X[col] + 12, elig_y + BOX_H + 34 + 26 + i * (BOX_H + 6),
                            f"{reason} (n = {count})"))
    parts.append(_arrow(COL_X[col - 1] + BOX_W, ret_y + BOX_H / 2,
                        COL_X[col], elig_y + BOX_H / 2))

    # --- Included column ---
    col = 4
    inc_y = elig_y + BOX_H / 2 - BOX_H / 2
    parts.append(_label(COL_X[col], inc_y - 14, "Included"))
    parts.append(_box(COL_X[col], inc_y, BOX_W, BOX_H,
                      f"Studies included in review (n = {d['included']})",
                      fill="#eef3f7", bold=True))
    parts.append(_arrow(COL_X[col - 1] + BOX_W, elig_y + BOX_H / 2,
                        COL_X[col], inc_y + BOX_H / 2))

    height = max(dedup_y, elig_y) + BOX_H + 260
    width = COL_X[-1] + BOX_W + 40
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
        "<defs><marker id=\"arrow\" markerWidth=\"8\" markerHeight=\"8\" "
        "refX=\"6\" refY=\"3\" orient=\"auto\"><path d=\"M0,0 L6,3 L0,6 Z\" "
        f'fill="{LINE}"/></marker></defs>'
        f'<rect width="100%" height="100%" fill="#ffffff"/>'
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
