"""Convert a Markdown document to Word (.docx) and PDF — no Pandoc needed.

Uses python-docx (Word) and reportlab (PDF). Handles the Markdown subset the
guides use: headings (#..######), paragraphs, bullet/numbered lists, tables,
horizontal rules, and **bold** / *italic* / `code` inline.

Usage:
    python shared/scripts/mdconvert.py PANDUAN.md --out-dir dist
    python shared/scripts/mdconvert.py PANDUAN.md --formats docx
"""

import argparse
import os
import re


# --------------------------------------------------------------------------- #
# Markdown -> blocks
# --------------------------------------------------------------------------- #

def parse_blocks(text):
    lines = text.split("\n")
    blocks, i = [], 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.lstrip().startswith("```"):
            buf = []
            i += 1
            while i < n and not lines[i].lstrip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            blocks.append(("code", "\n".join(buf)))
            continue
        m = re.match(r"(#{1,6})\s+(.*)", line)
        if m:
            blocks.append(("h", (len(m.group(1)), m.group(2).strip())))
            i += 1
            continue
        if re.match(r"^\s*[-*_]{3,}\s*$", line):
            blocks.append(("hr", None))
            i += 1
            continue
        if line.strip().startswith("|"):
            tbl = []
            while i < n and lines[i].strip().startswith("|"):
                tbl.append(lines[i])
                i += 1
            blocks.append(("table", tbl))
            continue
        if re.match(r"^\s*[-*+]\s+", line):
            items = []
            while i < n and re.match(r"^\s*[-*+]\s+", lines[i]):
                items.append(re.sub(r"^\s*[-*+]\s+", "", lines[i]).strip())
                i += 1
            blocks.append(("ul", items))
            continue
        if re.match(r"^\s*\d+[.)]\s+", line):
            items = []
            while i < n and re.match(r"^\s*\d+[.)]\s+", lines[i]):
                items.append(re.sub(r"^\s*\d+[.)]\s+", "", lines[i]).strip())
                i += 1
            blocks.append(("ol", items))
            continue
        buf = [line]
        i += 1
        while (i < n and lines[i].strip()
               and not lines[i].strip().startswith("|")
               and not re.match(r"(#{1,6})\s", lines[i])
               and not re.match(r"^\s*[-*+]\s+", lines[i])
               and not re.match(r"^\s*\d+[.)]\s+", lines[i])):
            buf.append(lines[i])
            i += 1
        # Join soft line breaks with a space; honour hard breaks (two trailing
        # spaces or a trailing backslash) with a newline the renderers preserve.
        para = ""
        for j, raw in enumerate(buf):
            piece = raw.strip()
            if j:
                prev = buf[j - 1]
                para += "\n" if prev.endswith("  ") or prev.endswith("\\") else " "
            if piece.endswith("\\"):
                piece = piece[:-1].rstrip()
            para += piece
        blocks.append(("p", para))
    return blocks


# --------------------------------------------------------------------------- #
# Inline formatting
# --------------------------------------------------------------------------- #

def inline_runs(text):
    """Split inline markdown into (style, text) runs: '', 'bold', 'italic', 'code'."""
    runs, buf, i = [], [], 0
    def flush():
        if buf:
            runs.append(("", "".join(buf)))
            buf.clear()
    while i < len(text):
        if text.startswith("**", i):
            flush()
            j = text.find("**", i + 2)
            j = len(text) if j == -1 else j
            runs.append(("bold", text[i + 2:j]))
            i = j + 2
        elif text.startswith("`", i):
            flush()
            j = text.find("`", i + 1)
            j = len(text) if j == -1 else j
            runs.append(("code", text[i + 1:j]))
            i = j + 1
        elif text.startswith("*", i):
            flush()
            j = text.find("*", i + 1)
            j = len(text) if j == -1 else j
            runs.append(("italic", text[i + 1:j]))
            i = j + 1
        else:
            buf.append(text[i])
            i += 1
    flush()
    return runs


def _escape_xml(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline_to_rl(text):
    """Inline markdown -> reportlab XML-like markup."""
    parts = []
    for style, t in inline_runs(text):
        t = _escape_xml(t)
        if style == "bold":
            parts.append("<b>%s</b>" % t)
        elif style == "italic":
            parts.append("<i>%s</i>" % t)
        elif style == "code":
            parts.append('<font face="Courier">%s</font>' % t)
        else:
            parts.append(t)
    return "".join(parts).replace("\n", "<br/>")


def _parse_table(tbl_lines):
    rows = []
    for line in tbl_lines:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        rows.append(cells)
    header = rows[0] if rows else []
    data = rows[2:] if len(rows) > 2 else []
    return header, data


# --------------------------------------------------------------------------- #
# DOCX
# --------------------------------------------------------------------------- #

def to_docx(blocks, out_path):
    from docx import Document
    from docx.shared import Pt, RGBColor

    doc = Document()
    for typ, payload in blocks:
        if typ == "h":
            level, text = payload
            doc.add_heading(text, level=min(level, 4))
        elif typ == "p":
            p = doc.add_paragraph()
            _add_runs(p, payload)
        elif typ == "ul":
            for item in payload:
                p = doc.add_paragraph(style="List Bullet")
                _add_runs(p, item)
        elif typ == "ol":
            for item in payload:
                p = doc.add_paragraph(style="List Number")
                _add_runs(p, item)
        elif typ == "table":
            header, data = _parse_table(payload)
            if header:
                table = doc.add_table(rows=1 + len(data), cols=len(header))
                table.style = "Light Grid Accent 1"
                for j, h in enumerate(header):
                    table.rows[0].cells[j].text = h
                for i, row in enumerate(data):
                    for j, c in enumerate(row):
                        table.rows[i + 1].cells[j].text = c
        elif typ == "code":
            p = doc.add_paragraph()
            run = p.add_run(payload)
            run.font.name = "Consolas"
            run.font.size = Pt(9)
        elif typ == "hr":
            doc.add_paragraph("_" * 60)
    doc.save(out_path)
    return out_path


def _add_runs(p, text):
    for k, line in enumerate(text.split("\n")):
        if k:
            p.add_run().add_break()
        for style, t in inline_runs(line):
            run = p.add_run(t)
            if style == "bold":
                run.bold = True
            elif style == "italic":
                run.italic = True
            elif style == "code":
                run.font.name = "Consolas"


# --------------------------------------------------------------------------- #
# PDF
# --------------------------------------------------------------------------- #

def to_pdf(blocks, out_path):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    Table, TableStyle, HRFlowable)

    styles = getSampleStyleSheet()
    body = ParagraphStyle("Body", parent=styles["BodyText"], spaceAfter=6,
                          fontSize=10.5, leading=15)
    h1 = ParagraphStyle("H1", parent=styles["Title"], spaceAfter=12, fontSize=20)
    h2 = ParagraphStyle("H2", parent=styles["Heading1"], spaceBefore=12,
                        spaceAfter=6, fontSize=14)
    h3 = ParagraphStyle("H3", parent=styles["Heading2"], spaceBefore=8,
                        spaceAfter=4, fontSize=12)
    bullet = ParagraphStyle("Bullet", parent=body, leftIndent=18,
                            bulletIndent=6, spaceAfter=3)
    code = ParagraphStyle("Code", parent=styles["Code"], fontSize=8.5,
                          backColor=colors.whitesmoke, spaceAfter=6)

    doc = SimpleDocTemplate(out_path, pagesize=A4,
                            leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=2 * cm, bottomMargin=2 * cm)
    story = []
    for typ, payload in blocks:
        if typ == "h":
            level, text = payload
            style = {1: h1, 2: h2, 3: h3}.get(level, h3)
            story.append(Paragraph(inline_to_rl(text), style))
        elif typ == "p":
            story.append(Paragraph(inline_to_rl(payload), body))
        elif typ == "ul":
            for item in payload:
                story.append(Paragraph(inline_to_rl(item), bullet, bulletText="\u2022"))
        elif typ == "ol":
            for idx, item in enumerate(payload, 1):
                story.append(Paragraph(inline_to_rl(item), bullet, bulletText="%d." % idx))
        elif typ == "table":
            header, data = _parse_table(payload)
            if header:
                tbl = Table([header] + data, repeatRows=1)
                tbl.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef3f7")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#999999")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ]))
                story.append(tbl)
                story.append(Spacer(1, 6))
        elif typ == "code":
            story.append(Paragraph(_escape_xml(payload), code))
        elif typ == "hr":
            story.append(HRFlowable(width="100%", thickness=0.5,
                                    color=colors.HexColor("#999999")))
            story.append(Spacer(1, 6))
    doc.build(story)
    return out_path


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #

def convert(md_path, out_dir=".", formats=("docx", "pdf")):
    os.makedirs(out_dir, exist_ok=True)
    with open(md_path, encoding="utf-8") as f:
        blocks = parse_blocks(f.read())
    base = os.path.splitext(os.path.basename(md_path))[0]
    produced = []
    if "docx" in formats:
        produced.append(to_docx(blocks, os.path.join(out_dir, base + ".docx")))
    if "pdf" in formats:
        produced.append(to_pdf(blocks, os.path.join(out_dir, base + ".pdf")))
    for p in produced:
        print("wrote", p)
    return produced


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("md", help="path to the Markdown file")
    ap.add_argument("--out-dir", default="dist", help="output directory")
    ap.add_argument("--formats", default="docx,pdf",
                    help="comma-separated: docx,pdf")
    args = ap.parse_args()
    formats = [f.strip() for f in args.formats.split(",") if f.strip()]
    convert(args.md, args.out_dir, formats)
