# Installation

masteracademicreview is a portable directory of `SKILL.md` skills plus a shared library (`shared/`) and Python scripts. Install the **whole repo as one unit** and keep the internal layout intact: skills resolve the shared library and scripts relative to the repo root.

## Layout Contract

```
masteracademicreview/
├── brainstorm/SKILL.md          # skill: research question + keywords (+ optional journal fit)
├── journal-match/SKILL.md       # skill: verified target-journal shortlist (JEV)
├── review-router/SKILL.md       # skill: genre classification + dispatch
├── book-review/SKILL.md  …  realist-review/SKILL.md   # 13 genre skills
├── commands/                    # slash commands (copy to .claude/commands/)
├── shared/                      # shared library (NOT a skill)
│   ├── search_strategy.md
│   ├── screening.md
│   ├── data_extraction.md
│   ├── risk_of_bias.md
│   ├── reporting_standards.md
│   ├── method_sources.md
│   ├── output_spec.md
│   └── scripts/
│       ├── prisma_flow.py
│       ├── journal_rank.py
│       ├── verify_refs.py
│       ├── screening_agreement.py
│       ├── validate_extraction.py
│       ├── export.py / mdconvert.py
│       ├── meta/
│       └── bibliometric/
└── docs/
```

- Each top-level `*/SKILL.md` is **one skill**; its ID equals its directory name.
- `shared/` is the shared library. Skills refer to it as `../shared/…` (one level up). Nothing inside `shared/` is a skill: harnesses ignore it because it has no `SKILL.md`.
- Python scripts run from the repo root, e.g. `python shared/scripts/meta/example.py`.

## The Tools Only (Pip)

If you only need the deterministic tools (deduplication, PRISMA, kappa, reference checks, the gate, protocols, journal ranking, letters), install the package; no clone needed:

```bash
pip install masteracademicreview
mar list
```

On Windows PowerShell use `py -m pip install ...` if `pip` is not found, and `python -m masteracademicreview` if `mar` is not on PATH. Extras: `masteracademicreview[meta]`, `[bibliometric]`, `[export]`, `[all]`. The skills below still need the repository.

## Requirements

- A harness that supports `SKILL.md` skills (Claude Code, OpenCode, Cursor, etc.).
- Python 3.10+ **only** for the skills that compute artifacts:
  - `systematic-review`, `scoping-review`, `mapping-review` → PRISMA flow (`prisma_flow.py`, stdlib only);
  - `journal-match` → journal scoring (`journal_rank.py`, stdlib only);
  - reference, agreement, and extraction checks (`verify_refs.py`, `screening_agreement.py`, `validate_extraction.py`, stdlib only);
  - `meta-analysis` → statistics (`numpy`, `scipy`, `pandas`, `matplotlib`);
  - `bibliometric-review` → corpus analysis (`numpy`, `matplotlib`);
  - Markdown export (`export.py`) → `python-docx`, `reportlab` (or Pandoc if installed).

```bash
pip install numpy scipy pandas matplotlib python-docx reportlab
```

The writing-only genres (`book-review`, `narrative-review`, `critical-review`, `integrative-review`, `realist-review`, `umbrella-review`, `rapid-review`, `meta-synthesis`) need no Python.

---

## Claude Code And OpenCode (Installer)

One clone, one command. The installer copies the 16 skills plus `shared/` and the
`/mar-*` slash commands to the folders each app reads, for your user account, so
the skills work in every project.

**Mac / Linux (Terminal):**

```bash
git clone https://github.com/thabedtholibb/masteracademicreview.git ~/masteracademicreview
python3 ~/masteracademicreview/install.py
```

**Windows (PowerShell):** use `$HOME`, not `~`. PowerShell does not expand `~` for
`git`, which would create a folder literally named `~`.

```bash
git clone https://github.com/thabedtholibb/masteracademicreview.git "$HOME\masteracademicreview"
python "$HOME\masteracademicreview\install.py"
```

Then **open a new session** (skills and commands load when a session starts) and
type `/mar` in Claude Code, or `@review-router` in OpenCode.

| App | Skills Go To | Slash Commands Go To |
|---|---|---|
| Claude Code | `~/.claude/skills/` (+ `shared/`) | `~/.claude/commands/mar-*.md` |
| OpenCode | read from `~/.claude/skills/` (OpenCode's compatibility path) | `~/.config/opencode/commands/mar-*.md` |

| Option | Effect |
|---|---|
| `--dry-run` | print the plan, change nothing |
| `--claude` / `--opencode` | one app only (`--opencode` alone puts skills in `~/.config/opencode/skills/`) |
| `--project DIR` | install into one project (`DIR/.claude/`, `DIR/.opencode/`) instead of your account |
| `--uninstall` | remove only what the installer added (it keeps a manifest) |
| `--force` | replace a same-named skill from another pack (skipped by default) |

**Update:** `git pull` in the clone, then run the installer again.

### Manual Install (No Installer)

Copy, do not symlink (symlinks need Developer Mode on Windows), and keep `shared/`
**next to** the skill folders so each skill's `../shared/` path resolves:

1. every folder that contains a `SKILL.md`, plus `shared/`, into `~/.claude/skills/`;
2. `commands/mar-*.md` into `~/.claude/commands/` (Claude Code) and
   `~/.config/opencode/commands/` (OpenCode).

Do **not** register the repository root as an OpenCode skill source: OpenCode
treats every `.md` file at a source root as a skill, so `README.md`, `CHANGELOG.md`
and the other root documents would appear as skills.

---

## Other Harnesses / Generic

Copy or symlink the skill directories and `shared/` into whichever skills directory your harness scans, keeping them as **siblings** so `../shared/` resolves. The skills use only `name` + `description` frontmatter, which is the common denominator across Claude Code, OpenCode, and similar harnesses.

---

## Invoking A Skill

Once installed, start a session any of three ways:

1. **Auto (default):** just describe what you want (*"Saya mau meta-analysis dari data ini"*); the skill whose `description` matches loads itself.
2. **`@skill-id` (OpenCode):** `@brainstorm`, `@review-router`, `@journal-match`, `@meta-analysis`, `@book-review`, etc. The ID is the skill's directory name.
3. **`/command` (Claude Code and OpenCode):** the installer copies the commands; type `/mar` to list them. Then use `/mar-brainstorm`, `/mar-review`, `/mar-journal-match`, `/mar-meta-analysis`, `/mar-systematic-review`, etc.

---

## Verify

Start a session and type:

> Help me write a review.

The `review-router` should kick in and interview you about the object, purpose, rigor, and data. If nothing appears:

0. Open a **new** session: skills and commands are loaded when a session starts. `python install.py --dry-run` shows where they were installed.
1. Confirm each skill directory sits at the expected level and contains its own `SKILL.md`.
2. Confirm `shared/` is beside them (not inside one of them).
3. Confirm the skill has a non-empty `description` in its frontmatter (discovery depends on it).

For the deterministic pieces, run:

```bash
python tests/check_docs.py
python tests/run_tool_tests.py
python shared/scripts/journal_rank.py --selftest
python shared/scripts/prisma_flow.py
```
