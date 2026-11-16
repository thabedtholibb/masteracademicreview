"""Export a Markdown review document to Word (.docx) and PDF.

Prefers Pandoc when installed; otherwise falls back to the built-in converter
(mdconvert.py: python-docx for Word, reportlab for PDF), so the command always
works with no external tools.

Usage:
    python shared/scripts/export.py review.md
    python shared/scripts/export.py review.md --formats docx
"""

import argparse
import os
import shutil
import subprocess


def pandoc_available():
    return shutil.which("pandoc") is not None


def _pandoc_export(md_path, formats):
    base = os.path.splitext(md_path)[0]
    produced = []
    for fmt in formats:
        out = f"{base}.{fmt}"
        r = subprocess.run(["pandoc", md_path, "-o", out, "--standalone"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            last = r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "unknown error"
            print(f"[!] pandoc {fmt} failed: {last}")
            if fmt == "pdf":
                print("    PDF needs a PDF engine; install one (e.g. tectonic),"
                      " or let the built-in converter handle it.")
        else:
            produced.append(out)
            print(f"wrote {out}")
    return produced


def export(md_path, formats=("docx", "pdf")):
    """Convert `md_path` to the given formats. Returns the list of files written."""
    if pandoc_available():
        return _pandoc_export(md_path, formats)
    print("Pandoc not found — using the built-in converter (python-docx + reportlab).")
    from mdconvert import convert
    out_dir = os.path.dirname(os.path.abspath(md_path))
    return convert(md_path, out_dir=out_dir, formats=formats)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("md", help="path to review.md")
    ap.add_argument("--formats", default="docx,pdf",
                    help="comma-separated formats, e.g. docx,pdf")
    args = ap.parse_args()
    formats = [f.strip() for f in args.formats.split(",") if f.strip()]
    export(args.md, formats)
