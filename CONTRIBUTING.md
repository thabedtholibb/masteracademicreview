# Contributing

1. Open an issue first for new genres or changes to a skill's protocol.
2. Keep tools stdlib-only where possible (see `shared/scripts/`).
3. Before a PR run:
   ```bash
   python tests/run_tool_tests.py
   python tests/check_docs.py
   python examples/systematic-review-demo/run_demo.py
   ```
   CI repeats these on Linux and Windows with Python 3.10-3.13; `uv python install 3.10` lets you test the oldest version locally.
4. Add a fixture in `tests/fixtures/` and a case in `tests/run_tool_tests.py` for every new tool or bug fix.
5. Never add scraping of services whose terms forbid it (e.g. Scopus). Cite real sources only; do not invent references.
6. Files must be UTF-8; scripts must not crash on a cp1252 console (Windows).
7. Decisions follow JEV (`shared/jev.md`): a new decision point in a skill lists ranked options with **#1 recommended**; a new tool prints its next steps in priority order.
8. Fixtures and examples use **synthetic or fictional data only** (DOIs with the test prefix `10.5555`), released with the code under the MIT licence. Never commit real screening data, unpublished manuscripts or personal data.
9. Be kind: see the [Code of Conduct](CODE_OF_CONDUCT.md). Security problems go through [SECURITY.md](SECURITY.md), not public issues.
