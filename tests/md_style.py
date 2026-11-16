"""House style for Markdown: Title Case headings and table headers.

Used by tests/check_docs.py (enforcement) and by one-off clean-up scripts.
Stdlib only.

Title Case rule ("Capitalize Each Word"): the first letter of every word is
upper case, including each part of a hyphenated or slashed word
("Risk-Of-Bias", "Scoping/Mapping"). Left untouched: inline code, link
targets, words that already carry an inner capital (PRISMA, PyPI, ScR),
words starting with a digit or symbol (#1, 2x2, --strict), and file-like
tokens (review.md, e.g.).
"""

from __future__ import annotations

import re

PROTECT_RE = re.compile(r"`[^`]*`|\]\([^)]*\)|<[^>]+>|https?://\S+")
LEAD = "*_([\"'“‘"


def _cap_part(part: str) -> str:
    i = 0
    while i < len(part) and part[i] in LEAD:
        i += 1
    if i < len(part) and part[i].isalpha() and part[i].islower():
        return part[:i] + part[i].upper() + part[i + 1:]
    return part


def _cap_word(word: str) -> str:
    core = word.strip(LEAD + "*_)]\"'”’.,:;!?")
    if not core or not core[0].isalpha():
        return word                                   # #1, 2x2, --strict, numbers
    if re.search(r"[A-Za-z]\.[A-Za-z]|_|\\|=", core):
        return word                                   # review.md, e.g., snake_case
    parts = re.split(r"([-/–])", word)
    for part in parts[::2]:
        if any(c.isupper() for c in part.strip(LEAD)[1:]):
            return word                               # PRISMA, PyPI, ScR, McGill
    return "".join(_cap_part(p) if k % 2 == 0 else p for k, p in enumerate(parts))


def title_case(text: str) -> str:
    out, last = [], 0
    for m in PROTECT_RE.finditer(text):
        out.append(_title_plain(text[last:m.start()]))
        out.append(m.group(0))
        last = m.end()
    out.append(_title_plain(text[last:]))
    return "".join(out)


def _title_plain(text: str) -> str:
    return "".join(_cap_word(t) if not t.isspace() else t for t in re.split(r"(\s+)", text))


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
TABLE_SEP_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")


def iter_style_targets(lines: list[str]):
    """Yield (index, kind) for headings and table header rows outside code fences."""
    fence = False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        if HEADING_RE.match(line):
            yield i, "heading"
        elif line.lstrip().startswith("|") and i + 1 < len(lines) and TABLE_SEP_RE.match(lines[i + 1]):
            yield i, "table"


def fix_line(line: str, kind: str) -> str:
    if kind == "heading":
        m = HEADING_RE.match(line)
        return f"{m.group(1)} {title_case(m.group(2))}"
    return "|".join(title_case(c) for c in line.split("|"))


def style_problems(text: str) -> list[str]:
    """Headings / table headers that are not in Title Case."""
    lines = text.splitlines()
    return [lines[i].strip() for i, kind in iter_style_targets(lines)
            if fix_line(lines[i], kind) != lines[i]]


def selftest() -> None:
    cases = {
        "Decision points (JEV)": "Decision Points (JEV)",
        "Risk of bias: RoB 2 and ROBINS-I": "Risk Of Bias: RoB 2 And ROBINS-I",
        "What the code does (`shared/scripts/meta/`)": "What The Code Does (`shared/scripts/meta/`)",
        "meta-analysis and scoping/mapping": "Meta-Analysis And Scoping/Mapping",
        "#1 recommended: the author's call": "#1 Recommended: The Author's Call",
        "Install with pip on PyPI, see review.md": "Install With Pip On PyPI, See review.md",
        "Skill mana yang saya butuhkan?": "Skill Mana Yang Saya Butuhkan?",
        "*ranked* shortlist": "*Ranked* Shortlist",
    }
    for raw, want in cases.items():
        got = title_case(raw)
        assert got == want, (raw, got, want)
    md = "# a title\n\n```\n## not a heading\n```\n\n| col one | `code` |\n|---|---|\n| keep this | x |\n"
    assert style_problems(md) == ["# a title", "| col one | `code` |"], style_problems(md)
    print("md_style selftest OK")


if __name__ == "__main__":
    selftest()
