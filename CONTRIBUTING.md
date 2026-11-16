# Contributing

1. Open an issue first for new genres or changes to a skill's protocol.
2. Keep tools stdlib-only where possible (see `shared/scripts/`).
3. Before a PR run:
   ```bash
   python tests/run_tool_tests.py
   python tests/check_docs.py
   ```
4. Add a fixture in `tests/fixtures/` and a case in `tests/run_tool_tests.py` for every new tool or bug fix.
5. Never add scraping of services whose terms forbid it (e.g. Scopus). Cite real sources only; do not invent references.
6. Files must be UTF-8; scripts must not crash on a cp1252 console (Windows).
