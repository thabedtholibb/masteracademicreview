# Master Academic Review

![License: MIT](https://img.shields.io/badge/license-MIT-blue)
![CI](https://github.com/thabedtholibb/masteracademicreview/actions/workflows/ci.yml/badge.svg)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![Skills: 16](https://img.shields.io/badge/skills-16-2ea44f)
![Review genres: 13](https://img.shields.io/badge/review%20genres-13-2ea44f)
![Reporting: PRISMA 2020](https://img.shields.io/badge/reporting-PRISMA%202020-6f42c1)

> **Every kind of review, one toolkit.** A portable agent skill-suite specialized in *writing reviews* — from a book review to a meta-analysis to a realist review — each with the right protocol, the right reporting standard, and (where it matters) real statistics for its genre.

Most academic-AI tools treat "review" as a side-mode of a paper generator. **Master Academic Review** inverts that: **the review is the product**, and the first job of the tool is to figure out *which* review you actually need.

> **What this is — and is not.** Master Academic Review is **not** a full-paper pipeline: it does not design or run experiments, and it does not generate new findings (unlike Spark-to-Paper or AI-Scientist). It produces **one kind of deliverable — a review document** — plus the auditable artifacts that back it (a PRISMA flow diagram, pooled estimates, forest/funnel plots). It works interactively, genre by genre, with you as the author.
>
> Deeper reading: [docs/USAGE.md](docs/USAGE.md) for the working model · [docs/FLOWS.md](docs/FLOWS.md) for skill-by-skill flows · [docs/WALKTHROUGH.md](docs/WALKTHROUGH.md) for a concrete session · [docs/INSTALL.md](docs/INSTALL.md) for per-platform setup.

---

## Documentation

[Decision tree (which skill?)](docs/DECISION_TREE.md) · [FAQ](docs/FAQ.md) · [Troubleshooting (Windows, Pandoc, encoding)](docs/TROUBLESHOOTING.md) · [Usage](docs/USAGE.md) · [Install](docs/INSTALL.md)

## The Flow

```
vague idea
   │
   ▼
brainstorm ──► focused research question + keyword set (PICO / PICo / PCC / SPIDER)
   │                │
   │                └──► journal-match (optional) ──► verified journal shortlist (JEV)
   │
   ▼
review-router ──► classify + rank the review genre (best fit first)
   │
   ▼
genre skill (thirteen genres)
   │  methodology from shared/*.md · scripts from shared/scripts/
   ▼
review document + artifacts (PRISMA flow, forest/funnel plots, pooled estimates)
```

The **`brainstorm` skill** sits before classification because most people get stuck choosing keywords and framing their question. It produces a ready-to-search question plus a Boolean query, then hands off to the router.

---

## What You Get (the Output)

Every run ends with **one review document plus supporting artifacts** (see [shared/output_spec.md](shared/output_spec.md)):

1. **`review.md`** — the review itself: a title, a metadata block (review type, reporting standard, sources, search date, gate status), an abstract, the genre's sections, and references.
2. **Artifacts** (per genre) — e.g. `prisma_flow.svg`, `forest.png`, `funnel.png`, `effects.csv`, `characteristics.csv`, plus the gate reports `agreement.md`, `extraction_check.md`, and `ref_check.md`.
3. **`review.docx` / `review.pdf`** — optional, via `python shared/scripts/export.py review.md` (Pandoc, with an automatic no-Pandoc fallback), so the review can be submitted to Word-based journals or a supervisor.
4. **`journal_shortlist.md`** — optional, from `journal-match`: a ranked target-journal shortlist with verified metrics and a submission cascade.

---

## The Core Idea: A Review Is Not One Thing

A review is a *family* of genres, each with its own methodology, reporting standard, and reader. Master Academic Review encodes that taxonomy as its organizing principle — **all thirteen implemented**.

| Genre | What it does | Reporting standard |
|---|---|---|
| **Book review** | Critically assess a single book | Genre conventions |
| **Narrative review** | Broad expert synthesis of a field | SANRA |
| **Critical review** | Argue a conceptual thesis across literature | — (argument contract) |
| **Systematic review** | Reproducible, comprehensive synthesis | PRISMA 2020 |
| **Meta-analysis** | Statistically pool effect sizes | PRISMA + MOOSE, GRADE |
| **Scoping review** | Map the breadth of a field | PRISMA-ScR |
| **Umbrella review** | Synthesize existing reviews | PRIOR |
| **Meta-synthesis** | Qualitative evidence synthesis | ENTREQ |
| **Rapid review** | Streamlined systematic review | Cochrane rapid-review guidance |
| **Integrative review** | Combine diverse designs into a whole | Whittemore & Knafl |
| **Mapping review** | Visual evidence & gap map | ROSES / EGM |
| **Bibliometric review** | Citation & co-word analysis | PRISMA 2020 (search) |
| **Realist review** | Theory-driven explanation (CMO) | RAMESES |

Every standard above is backed by a Crossref-verified citation in [`shared/method_sources.md`](shared/method_sources.md), along with the method papers behind each workflow and a cross-genre **Q1-readiness checklist**. Two genres (critical review, book review) have no EQUATOR-registered checklist; the suite says so and uses an explicit internal contract instead of borrowing a standard that does not fit.

---

## Journal Targeting (Optional)

Writing the review and choosing the venue are two decisions. **`journal-match`** handles the second one — before you write (recommended, because the venue shapes scope and length) or after.

- **Ranked, not guessed.** Eight criteria — scope fit (30%), article type (15%), method acceptance (15%), indexing (10%), speed (10%), cost/APC (10%), audience (5%), legitimacy (5%) — are scored 0–5 and combined by `shared/scripts/journal_rank.py`, so the ranking is reproducible.
- **Evidence-first (JEV).** Every quartile, APC, and decision-time claim carries a source and a check date. Anything unverified is labelled `unverified` and lowers the confidence; it is never filled in with a plausible number.
- **Submission cascade.** Reach / target / safety with explicit triggers and no simultaneous submissions. The recommended **#1** is the best fit-adjusted target, not the highest quartile.

Ask *"Where should I submit this review?"* — `brainstorm` offers it after the question + keywords, and `review-router` passes the genre and object to it.

---

## Reproducibility Checks (Built In)

The suite does not ask you to trust arithmetic it cannot show. Stdlib-only tools are part of the gates:

| Check | Command | What it catches |
|---|---|---|
| **Reference integrity** | `python shared/scripts/verify_refs.py review.md` | duplicate DOIs, citations with no reference, orphan references, missing year/title. Add `--online` for a Crossref DOI/title/year check. |
| **Screening agreement** | `python shared/scripts/screening_agreement.py screening_log.csv --long --reviewers alice,bob` | Cohen's κ, PABAK, per-stage agreement, and a `conflicts.csv` for adjudication. |
| **Extraction validation** | `python shared/scripts/validate_extraction.py effects.csv` | non-finite effects, variance ≤ 0, bad sample sizes/years, duplicate study–outcome rows, and k < 2 / k < 10 guards. |
| **Protocol** | `python shared/scripts/protocol.py protocol.json --out protocol.md` | a registration-ready protocol (PROSPERO/OSF fields) per genre, PRISMA-P based; undecided fields stay `[TO COMPLETE]` and `--strict` fails until they are filled. Start with `--template GENRE`. |
| **Review gate** | `python shared/scripts/check_review.py review.md` | missing metadata fields, missing genre sections, unresolved citations, referenced/required artifacts that do not exist, leftover `TODO`/`[citation needed]`, and a gate line that says "passed" with an incomplete checklist. |

All of these are offline by default and run in CI; only `verify_refs.py --online` needs the network. Reports land in `review_check.md`, `ref_check.md`, `agreement.md`, and `extraction_check.md`.

---

## Invoking a Skill (Three Ways)

1. **Auto (default).** Just describe what you want — *"I want a meta-analysis of this data"* — and the skill whose `description` matches loads itself.
2. **`@skill-id` (OpenCode).** Type `@meta-analysis`, `@brainstorm`, `@journal-match`, `@book-review`, and so on.
3. **`/command` (Claude Code).** Copy `commands/*.md` into `.claude/commands/`, then use `/review`, `/brainstorm`, `/journal-match`, `/meta-analysis`, `/systematic-review`, and so on.

---

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
      │    └─ scripts/
      │         ├─ prisma_flow.py     # deterministic PRISMA flow-diagram generator (stdlib SVG)
      │         ├─ journal_rank.py    # deterministic journal-fit scoring (stdlib)
      │         ├─ verify_refs.py     # reference integrity: offline + Crossref (stdlib)
      │         ├─ screening_agreement.py  # Cohen's κ + PABAK for dual screening (stdlib)
      │         ├─ validate_extraction.py  # effects/characteristics validation (stdlib)
      │         ├─ meta/              # real meta-analysis statistics engine (numpy/scipy/matplotlib)
      │         └─ bibliometric/      # bibliometric engine (parse, performance, co-word mapping, plots)
      │
      └─ one directory per genre (each a standalone skill)
           book-review/  narrative-review/  critical-review/
           systematic-review/  meta-analysis/  scoping-review/
           umbrella-review/  meta-synthesis/  rapid-review/
           integrative-review/  mapping-review/  bibliometric-review/  realist-review/
```

One brainstorm + one orchestrator + one optional journal matcher + one shared core + one skill per genre. **Narrow and deep, not a 13-agent mega-suite.**

---

## How It Differs from the Incumbents

| Capability | Master Academic Review | Academic-Research-Skills (ARS) | AI-Scientist | Spark-to-Paper |
|---|---|---|---|---|
| Treats review as a *family of genres* (13 types) | ✅ | ⚠️ | ❌ | ❌ |
| Orphan genres (book / narrative / critical / umbrella / meta-synthesis / integrative / mapping / realist) | ✅ | ❌ | ❌ | ❌ |
| Review-type diagnostic router (ranked) | ✅ | ❌ | ❌ | ❌ |
| Research-question + keyword brainstorm | ✅ | ⚠️ | ❌ | ❌ |
| Ranked target-journal shortlist with verified metrics (JEV) | ✅ | ⚠️ | ❌ | ❌ |
| Real meta-analysis statistics (Python) | ✅ | ❌ | ❌ | ❌ |
| Deterministic reporting-standard gates | ✅ | ⚠️ | ❌ | ✅ |
| Focus on *reviews* (not papers) | ✅ | ❌ | ❌ | ❌ |

✅ = yes · ⚠️ = partial · ❌ = no

**Positioning:** Master Academic Review does not generate a paper and does not run your experiments. It is a **human-in-the-loop specialist for the review genre** — the author owns every claim; the tool owns the protocol, the reporting checklist, and the arithmetic.

---

## Quick Start

1. **[Install](docs/INSTALL.md)** — copy or register the skill directories plus `shared/` in your harness (Claude Code / OpenCode / generic). Python is needed only for `systematic-review`, `scoping-review`, `mapping-review`, `meta-analysis`, `bibliometric-review`, and the `journal-match` scorer.
2. **Ask for a review** — in a session, say:
   - *"I want to write a review but I don't know the topic yet."* → `brainstorm` sharpens the question + keywords.
   - *"Help me write a review."* → `review-router` interviews you and classifies the type.
   - *"I want a meta-analysis of this data."* → `meta-analysis` (runs `shared/scripts/meta/`).
   - *"Where should I submit this review?"* → `journal-match` builds a verified, ranked shortlist.
   - Or use `@meta-analysis` / `/meta-analysis` to jump straight in.
3. **See it in action** — [docs/WALKTHROUGH.md](docs/WALKTHROUGH.md) shows a full annotated session.

---

## Repository Layout

```
masteracademicreview/
├── README.md
├── LICENSE
├── .gitignore
├── .gitattributes
├── brainstorm/SKILL.md             # pre-router: research question + keywords (+ optional journal fit)
├── review-router/SKILL.md          # orchestrator: interview → classify + rank → dispatch
├── journal-match/SKILL.md          # optional: verified target-journal shortlist (JEV)
├── book-review/SKILL.md
├── narrative-review/SKILL.md
├── critical-review/SKILL.md
├── systematic-review/SKILL.md
├── meta-analysis/SKILL.md
├── scoping-review/SKILL.md
├── umbrella-review/SKILL.md
├── meta-synthesis/SKILL.md
├── rapid-review/SKILL.md
├── integrative-review/SKILL.md
├── mapping-review/SKILL.md
├── bibliometric-review/SKILL.md
├── realist-review/SKILL.md
├── commands/                       # slash commands (copy to .claude/commands/ for Claude Code)
│   ├── brainstorm.md
│   ├── review.md
│   ├── journal-match.md
│   └── *.md                        # one per genre (13)
├── shared/                         # shared library (methodology + scripts)
│   ├── search_strategy.md
│   ├── screening.md
│   ├── data_extraction.md
│   ├── risk_of_bias.md
│   ├── reporting_standards.md
│   ├── method_sources.md           # Crossref-verified method citations + Q1 checklist
│   ├── output_spec.md
│   └── scripts/
│       ├── prisma_flow.py
│       ├── journal_rank.py         # deterministic journal-fit scorer (stdlib)
│       ├── verify_refs.py          # reference consistency + Crossref verification (stdlib)
│       ├── screening_agreement.py  # Cohen's κ + PABAK, wide or long logs (stdlib)
│       ├── validate_extraction.py  # meta/generic extraction checks (stdlib)
│       ├── export.py               # one-command MD → DOCX/PDF (Pandoc, fallback to mdconvert)
│       ├── mdconvert.py            # no-Pandoc converter (python-docx + reportlab)
│       ├── meta/
│       │   ├── __init__.py
│       │   ├── effect_sizes.py
│       │   ├── pooling.py
│       │   ├── plots.py
│       │   └── example.py
│       └── bibliometric/
│           ├── __init__.py
│           ├── parsers.py
│           ├── performance.py
│           ├── mapping.py
│           ├── plots.py
│           ├── example.py
│           ├── validate_export.py  # regression checks on a real Scopus/WoS export
│           └── sample.csv
├── tests/
│   ├── check_docs.py               # standards/gates/provenance integrity (stdlib)
│   ├── run_tool_tests.py           # CLI regression tests for the reproducibility tools
│   ├── fixtures/scopus_mini.csv    # cp1252 + semicolon fixture used by CI
│   ├── fixtures/journals_example.csv  # fictional journal table for the scorer's CI check
│   ├── fixtures/review_refs_*.md   # clean / broken / running-bibliography reference fixtures
│   ├── fixtures/screening_*.csv    # wide and long dual-screening fixtures
│   └── fixtures/effects_*.csv      # valid / invalid meta-analysis extraction fixtures
├── .github/workflows/ci.yml        # engines + parser + export + journal + reproducibility tools
└── docs/
    ├── INSTALL.md
    ├── USAGE.md
    ├── FLOWS.md
    └── WALKTHROUGH.md
```

Skill directories are named in lowercase (e.g. `meta-analysis/`) because that is the skill *ID* your harness loads; "Master Academic Review" is the project name. On GitHub this repository is `masteracademicreview`; a fresh clone creates a folder of the same name.

---

## Principles

- **AI is the copilot, not the author.** Every review type stops for author confirmation at decision points; the author answers for every claim and every inclusion/exclusion.
- **Recommendation-first.** At every decision point, the skill presents the best options in priority order with a recommended default — never a bare open question.
- **Deterministic where it matters.** Search counts, screening tallies, PRISMA flow, and meta-analysis arithmetic are computed by code, never by an LLM guessing.
- **Reporting standards are gates, not suggestions.** A review that skips a PRISMA item is flagged, not silently passed.
- **Evidence over memory.** Journal quartiles, APCs, and decision times are verified against a primary source and date-stamped; unverified values are labelled, never invented.
- **Portable.** Plain `SKILL.md` frontmatter (`name` + `description`) works across Claude Code, OpenCode, and other agent harnesses with minimal adjustment.

---

## License

MIT. See [LICENSE](LICENSE).
