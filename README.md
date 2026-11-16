# masteracademicreview

> **Every kind of review, one toolkit.** A portable agent skill-suite specialized in *writing reviews* — from a book review to a meta-analysis to a realist review — with the right protocol, reporting standard, and (where it matters) real statistics for each genre.

Most academic-AI tools treat "review" as a side-mode of a paper generator. masteracademicreview inverts that: **the review is the product**, and the first job of the tool is to figure out *which* review you actually need.

> **What this is — and is not.** masteracademicreview is **not** a full-paper pipeline: it does not design or run experiments and does not generate new findings (unlike Spark-to-Paper or AI-Scientist). It produces **one kind of deliverable — a review document** — plus the auditable artifacts that back it (a PRISMA flow diagram, pooled estimates, forest/funnel plots). It works interactively, genre by genre, with you as the author. See [docs/USAGE.md](docs/USAGE.md) for the model, [docs/FLOWS.md](docs/FLOWS.md) for skill-by-skill flows, [docs/WALKTHROUGH.md](docs/WALKTHROUGH.md) for a concrete session, and [docs/INSTALL.md](docs/INSTALL.md) for per-platform setup.

---

## The flow

```
vague idea
   │
   ▼
brainstorm ──► focused research question + keyword set (PICO/PICo/PCC/SPIDER)
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

The **`brainstorm` skill** sits before classification because most people get stuck choosing keywords and framing their question. It produces a ready-to-search question + Boolean query, then hands off to the router.

---

## What you get (the output)

Every run ends with **one review document plus supporting artifacts** (see [shared/output_spec.md](shared/output_spec.md)):

1. **`review.md`** — the review itself: a title, a metadata block (review type, reporting standard, sources, search date, gate status), an abstract, the genre's sections, and references.
2. **Artifacts** (per genre) — e.g. `prisma_flow.svg`, `forest.png`, `funnel.png`, `effects.csv`, `characteristics.csv`.
3. **`review.docx` / `review.pdf`** — optional, via `python shared/scripts/export.py review.md` (Pandoc), so the review can be submitted to Word-based journals or a supervisor.

---

## The core idea: a review is not one thing

A review is a *family* of genres, each with its own methodology, reporting standard, and reader. masteracademicreview encodes that taxonomy as its organizing principle — **all thirteen implemented**.

| Genre | What it does | Reporting standard |
|---|---|---|
| **Book review** (resensi buku) | Critically assess a single book | genre conventions |
| **Narrative review** | Broad expert synthesis of a field | SANRA |
| **Critical review** | Argue a conceptual thesis across literature | — |
| **Systematic review** | Reproducible, comprehensive synthesis | PRISMA 2020 |
| **Meta-analysis** | Statistically pool effect sizes | PRISMA + MOOSE, GRADE |
| **Scoping review** | Map the breadth of a field | PRISMA-ScR |
| **Umbrella review** | Synthesize existing reviews | PRIOR |
| **Meta-synthesis** | Qualitative evidence synthesis | ENTREQ |
| **Rapid review** | Streamlined systematic review | Cochrane RAPID |
| **Integrative review** | Combine diverse designs into a whole | Whittemore & Knafl |
| **Mapping review** | Visual evidence & gap map | ROSES / EGM |
| **Bibliometric review** | Citation & co-word analysis | PRISMA (search) |
| **Realist review** | Theory-driven explanation (CMO) | RAMESES |

---

## Invoking a skill (three ways)

1. **Auto (default).** Just describe what you want — *"Saya mau meta-analysis dari data ini"* — and the skill whose `description` matches loads itself.
2. **`@skill-id` (OpenCode).** Type `@meta-analysis`, `@brainstorm`, `@book-review`, etc.
3. **`/command` (Claude Code).** Copy `commands/*.md` into `.claude/commands/`, then use `/review`, `/brainstorm`, `/meta-analysis`, `/systematic-review`, etc.

---

## Architecture

```
brainstorm ──► research question + keywords ──► review-router ──► classify + rank ──► dispatch
      │
      ├─ shared/                     # reusable core (not a skill)
      │    ├─ search_strategy.md     # database query + grey literature
      │    ├─ screening.md           # title/abstract/full-text + PRISMA flow
      │    ├─ data_extraction.md     # extraction forms + effect-size data
      │    ├─ risk_of_bias.md        # RoB 2, ROBINS-I, NOS, CASP, AMSTAR-2, GRADE
      │    ├─ reporting_standards.md # PRISMA / SANRA / MOOSE / ENTREQ / PRIOR / RAMESES
      │    └─ scripts/
      │         ├─ prisma_flow.py    # deterministic PRISMA flow-diagram generator (stdlib SVG)
      │         ├─ meta/             # real meta-analysis statistics engine (numpy/scipy/matplotlib)
      │         └─ bibliometric/     # bibliometric engine (parse, performance, co-word mapping, plots)
      │
      └─ one directory per genre (each a standalone skill)
           book-review/  narrative-review/  critical-review/
           systematic-review/  meta-analysis/  scoping-review/
           umbrella-review/  meta-synthesis/  rapid-review/
           integrative-review/  mapping-review/  bibliometric-review/  realist-review/
```

One brainstorm + one orchestrator + one shared core + one skill per genre. **Narrow and deep, not a 13-agent mega-suite.**

---

## How it differs from the incumbents

| | masteracademicreview | ARS | AI-Scientist | Spark-to-Paper |
|---|---|---|---|---|
| Treats review as a *family of genres* (13 types) | ✅ core | ⚠️ few types | ❌ | ❌ |
| Orphan genres (book/narrative/critical/umbrella/meta-synthesis/integrative/mapping/realist) | ✅ | ❌ | ❌ | ❌ |
| Review-type diagnostic router (ranked) | ✅ | ❌ | ❌ | ❌ |
| Research-question + keyword brainstorm | ✅ | ⚠️ | ❌ | ❌ |
| Real meta-analysis statistics (Python) | ✅ | ❌ (explicitly no stats) | ❌ | ❌ |
| Deterministic reporting-standard gates | ✅ | ⚠️ | ❌ | ✅ (papers) |
| Focus on *reviews* (not papers) | ✅ | ❌ | ❌ | ❌ |

**Positioning:** masteracademicreview does not generate a paper and does not run your experiments. It is a **human-in-the-loop specialist for the review genre** — the author owns every claim; the tool owns the protocol, the reporting checklist, and the arithmetic.

---

## Quick start

1. **[Install](docs/INSTALL.md)** — copy or register the skill directories plus `shared/` in your harness (Claude Code / OpenCode / generic). Python is needed only for `systematic-review`, `scoping-review`, `mapping-review`, `meta-analysis`, and `bibliometric-review`.
2. **Ask for a review** — in a session, say:
   - *"Saya mau menulis review tapi belum tahu topiknya."* → `brainstorm` sharpens the question + keywords.
   - *"Bantu saya menulis review."* → `review-router` interviews you and classifies the type.
   - *"Saya mau meta-analisis dari data ini."* → `meta-analysis` (runs `shared/scripts/meta/`).
   - Or use `@meta-analysis` / `/meta-analysis` to jump straight in.
3. **See it in action** — [docs/WALKTHROUGH.md](docs/WALKTHROUGH.md) shows a full annotated session.

---

## Repository layout

```
academicskills/
├── README.md
├── LICENSE
├── .gitignore
├── .gitattributes
├── brainstorm/SKILL.md             # pre-router: research question + keywords
├── review-router/SKILL.md          # orchestrator: interview → classify+rank → dispatch
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
│   └── *.md                        # one per genre (13)
├── shared/                         # shared library (methodology + scripts)
│   ├── search_strategy.md
│   ├── screening.md
│   ├── data_extraction.md
│   ├── risk_of_bias.md
│   ├── reporting_standards.md
│   ├── output_spec.md
│   └── scripts/
│       ├── prisma_flow.py
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
│           └── example.py
└── docs/
    ├── INSTALL.md
    ├── USAGE.md
    ├── FLOWS.md
    └── WALKTHROUGH.md
```

---

## Principles

- **AI is the copilot, not the author.** Every review type stops for author confirmation at decision points; the author answers for every claim and every inclusion/exclusion.
- **Recommendation-first.** At every decision point, the skill presents the best options in priority order with a recommended default — never a bare open question.
- **Deterministic where it matters.** Search counts, screening tallies, PRISMA flow, and meta-analysis arithmetic are computed by code, never by an LLM guessing.
- **Reporting standards are gates, not suggestions.** A review that skips a PRISMA item is flagged, not silently passed.
- **Portable.** Plain `SKILL.md` frontmatter (`name` + `description`) works across Claude Code, OpenCode, and other agent harnesses with minimal adjustment.

---

## License

MIT. See [LICENSE](LICENSE).
