# Installation

masteracademicreview is a portable directory of `SKILL.md` skills plus a shared library (`shared/`) and Python scripts. Install the **whole repo as one unit** and keep the internal layout intact — skills resolve the shared library and scripts relative to the repo root.

## Layout contract

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
- `shared/` is the shared library. Skills refer to it as `../shared/…` (one level up). Nothing inside `shared/` is a skill — harnesses ignore it because it has no `SKILL.md`.
- Python scripts run from the repo root, e.g. `python shared/scripts/meta/example.py`.

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

## Claude Code

Claude Code discovers skills as `~/.claude/skills/<name>/SKILL.md` (one level deep). Clone once, then symlink every skill directory plus `shared/` as siblings:

```bash
git clone https://github.com/thabedtholibb/masteracademicreview.git /tmp/masteracademicreview
mkdir -p ~/.claude/skills

for d in /tmp/masteracademicreview/*/; do
  name=$(basename "$d")
  if [ -f "$d/SKILL.md" ]; then
    ln -s "$d" ~/.claude/skills/"$name"
  fi
done
ln -s /tmp/masteracademicreview/shared ~/.claude/skills/shared
```

Result: every skill directory plus `shared/` sits side by side, so each skill's `../shared/…` reference resolves correctly.

**Project-local alternative:** run the same loop with `.claude/skills/` (inside your project) as the destination.

---

## OpenCode

Register the repo root as a skills source. In your project's `opencode.jsonc` (or `.opencode/opencode.jsonc`):

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "skills": ["./masteracademicreview"]
}
```

OpenCode recursively discovers each `*/SKILL.md` and assigns the ID from the directory name — `brainstorm`, `journal-match`, `review-router`, and all thirteen genres. `shared/` is skipped (no `SKILL.md`).

**Global alternative:** clone into `~/.config/opencode/skills/masteracademicreview` and it is discovered automatically.

> OpenCode also reads `~/.claude/skills` for compatibility, so the Claude Code recipe above works for OpenCode too.

---

## Other harnesses / generic

Copy or symlink the skill directories and `shared/` into whichever skills directory your harness scans, keeping them as **siblings** so `../shared/` resolves. The skills use only `name` + `description` frontmatter, which is the common denominator across Claude Code, OpenCode, and similar harnesses.

---

## Invoking a skill

Once installed, start a session any of three ways:

1. **Auto (default)** — just describe what you want (*"Saya mau meta-analysis dari data ini"*); the skill whose `description` matches loads itself.
2. **`@skill-id` (OpenCode)** — `@brainstorm`, `@review-router`, `@journal-match`, `@meta-analysis`, `@book-review`, etc. The ID is the skill's directory name.
3. **`/command` (Claude Code)** — copy the bundled commands into `.claude/commands/`:

```bash
mkdir -p .claude/commands
cp commands/*.md .claude/commands/
```

Then use `/brainstorm`, `/review`, `/journal-match`, `/meta-analysis`, `/systematic-review`, etc.

---

## Verify

Start a session and type:

> Help me write a review.

The `review-router` should kick in and interview you about the object, purpose, rigor, and data. If nothing appears:

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
