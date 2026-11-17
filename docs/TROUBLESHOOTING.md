# Troubleshooting

Run commands from the **repository root**. Most problems below are Windows
console/encoding or missing optional dependencies.

## Quick Self-Check

```bash
python --version                       # needs 3.10 or newer
python tests/run_tool_tests.py         # stdlib tools (no extra packages)
python tests/check_docs.py             # documentation integrity
python shared/scripts/meta/selftest.py # meta-analysis engine (needs numpy + scipy)
```

If the first two pass, the stdlib tools work. The third needs the packages in
the next section.

## `python` Not Found, Or The Wrong Version (Windows)

- Try the launcher: `py -3 shared/scripts/prisma_flow.py --selftest`.
- Check that the right interpreter is first on `PATH`: `where python`.
- On macOS/Linux use `python3`.

## `ModuleNotFoundError: numpy / scipy / matplotlib / docx / reportlab`

Only some tools need packages:

| Tool | Needs |
|---|---|
| `verify_refs.py`, `screening_agreement.py`, `validate_extraction.py`, `check_review.py`, `protocol.py`, `prisma_flow.py`, `journal_rank.py` | nothing (stdlib) |
| `meta/` (pooling, plots) | `numpy`, `scipy`, `matplotlib` |
| `bibliometric/` | `numpy`, `matplotlib` |
| `export.py` fallback | `python-docx`, `reportlab` |

```bash
pip install numpy scipy matplotlib python-docx reportlab
```

## Garbled Characters (Mojibake) Or `UnicodeEncodeError` In The Console

Typical on Windows consoles using cp1252.

- `check_review.py` and `protocol.py` switch stdout to UTF-8 (with replacement);
  the other tools print through the console encoding, and CI runs them under
  cp1252 to catch crashes. If symbols such as the check mark show as `?`, write
  the report to a file instead: `--out report.md`.
- To force UTF-8 for a session: `set PYTHONUTF8=1` (cmd) or
  `$env:PYTHONUTF8 = "1"` (PowerShell).
- Never save review or CSV files in a legacy code page; use UTF-8.

## Scopus/Web Of Science Export Will Not Parse

- Scopus exports are often **semicolon-separated cp1252 with a BOM**. The
  bibliometric parser detects delimiter and encoding. Check your export with
  `python shared/scripts/bibliometric/validate_export.py your_export.csv`.
- If it reports missing columns, re-export with all fields selected
  (Authors, Title, Year, Source title, Cited by, Author Keywords, Affiliations).
- Excel re-saving can break quoting; export directly from the database and do
  not edit the file.

## Word/PDF Export Problems

`python shared/scripts/export.py review.md` uses **Pandoc** when it is installed
and otherwise falls back to the built-in converter.

- Check which is used: `pandoc --version` (not found means the fallback runs).
- Pandoc PDF output needs a PDF engine (for example a LaTeX distribution). If
  Pandoc is installed without an engine, export to DOCX only
  (`--formats docx`) or uninstall/disable Pandoc to use the fallback PDF.
- The fallback supports headings, lists, tables, bold/italic and hard line
  breaks. For complex typography use Pandoc.
- Metadata lines (`**Review type:** ...`) must end with **two spaces**; without
  them the fields merge into one paragraph. `check_review.py` warns about this.

## Skills Or `/mar` Commands Do Not Appear

1. Open a **new** session; skills and slash commands load when a session starts.
2. Run `python install.py --dry-run` from the clone to see where they are installed; run `python install.py` if they are missing.
3. On Windows, check for a folder literally named `~` in your home folder (`C:\Users\<you>\~`). It comes from running a bash-style `git clone ... ~/...` in PowerShell. Move the clone out of it and use `"$HOME\masteracademicreview"` instead.

## Skill Not Found By The Harness (Windows Install)

Older instructions used symlinks; `install.py` copies instead. On Windows, creating symlinks needs
Developer Mode (or an elevated shell). If you cannot create them, **copy** the
whole repository folder instead and keep the internal layout (`shared/` must
sit next to the skill folders).

## `verify_refs.py --online` Fails Or Is Slow

- It needs internet access and queries Crossref. Behind a proxy or offline,
  use the offline mode (the default) and verify references manually.
- Pass `--mailto you@example.org` to use Crossref's polite pool, and
  `--cache refs_cache.json` to avoid repeated lookups.
- `AMBIGUOUS`/`NO_MATCH` for books, reports and acronym guidelines is normal;
  verify them by hand.

## `check_review.py` Reports An Error I Do Not Understand

| Message | Meaning |
|---|---|
| `metadata: missing field ...` | add the field to the header block (see `shared/output_spec.md`) |
| `section: no heading matching ...` | the genre's required section is missing or named differently |
| `references: ...` | an unresolved citation, duplicate DOI or unparsable list (run `verify_refs.py` for detail) |
| `artifact: ... is referenced but not found` | the review mentions a file that is not next to it |
| `artifact: required file ... is missing` | the genre needs that artifact (for example `prisma_flow.svg`) |
| `placeholders left in text` | remove `TODO`, `TBD`, `[citation needed]` |
| `gate: ...` | the gate line is inconsistent with the checklist or the reference check |

Use `--genre` if the genre is not detected from the `Review type` line, and
`--no-artifacts` for a review whose artifacts live elsewhere.

## Tests Pass Locally But CI Fails

CI runs on Ubuntu and Windows. A Windows-only failure is usually an encoding or
path issue: open files with `encoding="utf-8"` and avoid hard-coded `/tmp`.
