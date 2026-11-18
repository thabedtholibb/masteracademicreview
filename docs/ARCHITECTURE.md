# Architecture And Repository Layout

How the pieces fit together. For installing and using the suite, start with the
[README](../README.md); for which skill to run, see
[DECISION_TREE.md](DECISION_TREE.md).

## Architecture

```
brainstorm ──► research question + keywords ──► review-router ──► classify + rank ──► dispatch
      │
      ├─ journal-match/               # optional: verified target-journal shortlist (JEV)
      │
      ├─ shared/                      # reusable core (not a skill)
      │    ├─ search_strategy.md      # database query + grey literature
      │    ├─ screening.md            # title/abstract/full-text + PRISMA flow
      │    ├─ data_extraction.md      # extraction forms + effect-size data
      │    ├─ risk_of_bias.md         # RoB 2, ROBINS-I, NOS, CASP, AMSTAR-2, GRADE
      │    ├─ reporting_standards.md  # PRISMA / PRISMA-ScR / SANRA / ENTREQ / PRIOR / RAMESES / ROSES / AMSTAR-2
      │    ├─ method_sources.md       # verified citations + Q1-readiness checklist
      │    ├─ jev.md                  # JEV decision protocol: ranked options, #1 recommended
      │    └─ scripts/
      │         ├─ cli.py             # `mar <tool>`: one command for every tool (pip package entry point)
      │         ├─ dedup.py           # deduplicate RIS/CSV/BibTeX exports -> PRISMA identification (stdlib)
      │         ├─ prisma_flow.py     # deterministic PRISMA flow-diagram generator + count checks (stdlib SVG)
      │         ├─ journal_rank.py    # deterministic journal-fit scoring (stdlib)
      │         ├─ verify_refs.py     # reference integrity: offline + Crossref (stdlib)
      │         ├─ screening_agreement.py  # Cohen's κ + PABAK for dual screening (stdlib)
      │         ├─ validate_extraction.py  # effects/characteristics validation (stdlib)
      │         ├─ protocol.py        # protocol.md per genre, PROSPERO/OSF fields (stdlib)
      │         ├─ check_review.py    # the review gate, ranked next steps (stdlib)
      │         ├─ submission.py      # cover letter + response to reviewers, EN/ID (stdlib)
      │         ├─ meta/              # real meta-analysis statistics engine (numpy/scipy/matplotlib)
      │         └─ bibliometric/      # bibliometric engine (parse, performance, co-word mapping, plots)
      │
      └─ one directory per genre (each a standalone skill)
           book-review/  narrative-review/  critical-review/
           systematic-review/  meta-analysis/  scoping-review/
           umbrella-review/  meta-synthesis/  rapid-review/
           integrative-review/  mapping-review/  bibliometric-review/  realist-review/
```

One brainstorm + one orchestrator + one optional journal matcher + one shared core +
one skill per genre. **Narrow and deep, not a 13-agent mega-suite.**

## Repository Layout

```
masteracademicreview/
├── README.md  README.id.md         # English / Bahasa Indonesia
├── LICENSE
├── pyproject.toml                  # pip package `masteracademicreview` (maps shared/scripts/)
├── install.py                      # installs skills + /mar-* commands (Claude Code, OpenCode)
├── CHANGELOG.md  CITATION.cff  CONTRIBUTING.md  CODE_OF_CONDUCT.md  SECURITY.md
├── brainstorm/SKILL.md             # pre-router: research question + keywords (+ optional journal fit)
├── review-router/SKILL.md          # orchestrator: interview → classify + rank → dispatch
├── journal-match/SKILL.md          # optional: verified target-journal shortlist (JEV)
├── <13 genre folders>/SKILL.md     # book, narrative, critical, systematic, meta-analysis, scoping,
│                                   # umbrella, meta-synthesis, rapid, integrative, mapping,
│                                   # bibliometric, realist
├── commands/                       # slash commands, all prefixed mar- (installed by install.py)
├── shared/                         # shared library (methodology + scripts)
│   ├── *.md                        # search, screening, extraction, risk of bias, reporting
│   │                               # standards, method sources, output spec, JEV
│   └── scripts/                    # the tools above, plus export.py and mdconvert.py (MD → DOCX/PDF)
├── tests/                          # tool tests, docs checks, cross-genre and encoding checks, fixtures
├── examples/systematic-review-demo/  # synthetic end-to-end run: exports → dedup → PRISMA → gate → letter
├── .github/workflows/              # ci.yml, verify-sources.yml (monthly Crossref check), publish.yml
└── docs/                           # INSTALL, USAGE, FLOWS, WALKTHROUGH, DECISION_TREE, FAQ,
                                    # TROUBLESHOOTING, ARCHITECTURE, id/ (Bahasa Indonesia)
```

Skill directories are named in lowercase (for example `meta-analysis/`) because that
is the skill ID your harness loads; "Master Academic Review" is the project name.
On GitHub this repository is `masteracademicreview`; a fresh clone creates a folder
of the same name.
