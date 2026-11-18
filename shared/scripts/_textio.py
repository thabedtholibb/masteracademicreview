"""Read text files the way people actually save them on Windows.

Excel and Notepad write CSV and text as UTF-8 (with or without a BOM), UTF-16
("Unicode Text") or the legacy ANSI code page (cp1252). The tools used to
assume UTF-8 and crashed with a traceback on the other two. ``read_text`` takes
the bytes and picks the first encoding that fits:

    BOM (UTF-8 / UTF-16 / UTF-32)  ->  BOM-less UTF-16  ->  UTF-8  ->  cp1252  ->  latin-1

Stdlib only; shared by every tool in this folder.
"""

from __future__ import annotations

import codecs
from pathlib import Path

BOMS = (
    (codecs.BOM_UTF32_LE, "utf-32"),
    (codecs.BOM_UTF32_BE, "utf-32"),
    (codecs.BOM_UTF8, "utf-8-sig"),
    (codecs.BOM_UTF16_LE, "utf-16"),
    (codecs.BOM_UTF16_BE, "utf-16"),
)


def decode(raw: bytes) -> str:
    """Decode bytes from a text file saved by Excel, Notepad, Scopus, Zotero or an editor."""
    for bom, encoding in BOMS:
        if raw.startswith(bom):
            return raw.decode(encoding)
    if len(raw) >= 4 and raw[1::2].count(0) > len(raw) // 4:      # UTF-16-LE without BOM
        try:
            return raw.decode("utf-16-le")
        except UnicodeDecodeError:
            pass
    for encoding in ("utf-8", "cp1252"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1")          # never fails; every byte maps to a character


def read_text(path: str | Path) -> str:
    """Whole file as text; raises ``OSError`` exactly like ``Path.read_text``."""
    return decode(Path(path).read_bytes())


def selftest() -> None:
    text = "Studi Ané, é ü ñ: 3 × 2, r² = 0.5\nsecond line\n"
    samples = {
        "utf-8": text.encode("utf-8"),
        "utf-8-bom": codecs.BOM_UTF8 + text.encode("utf-8"),
        "utf-16-bom": text.encode("utf-16"),
        "utf-16-be-bom": codecs.BOM_UTF16_BE + text.encode("utf-16-be"),
        "utf-16-le-nobom": text.encode("utf-16-le"),
        "cp1252": "Studi Ané, é ü ñ\nsecond line\n".encode("cp1252"),
    }
    for name, raw in samples.items():
        got = decode(raw)
        want = "Studi Ané, é ü ñ\nsecond line\n" if name == "cp1252" else text
        assert got == want, (name, got[:30])
    assert decode(b"") == ""
    assert decode(b"plain ascii") == "plain ascii"
    assert decode(bytes([0x81, 0x8d, 0x41])) != "", "undefined cp1252 bytes must still decode"
    print("textio selftest OK (utf-8, BOM, utf-16, utf-16 without BOM, cp1252)")


if __name__ == "__main__":
    selftest()
