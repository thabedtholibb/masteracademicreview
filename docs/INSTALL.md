# Installation

masteracademicreview is a portable directory of `SKILL.md` skills plus a shared library (`shared/`) and Python scripts. Install the **whole repo as one unit** and keep the internal layout intact — skills resolve the shared library and scripts relative to the repo root.

## Layout contract

```
academicskills/
├── review-router/SKILL.md      # skill: review-router
├── book-review/SKILL.md        # skill: book-review
├── narrative-review/SKILL.md   # skill: narrative-review
├── critical-review/SKILL.md    # skill: critical-review
├── systematic-review/SKILL.md  # skill: systematic-review
├── meta-analysis/SKILL.md      # skill: meta-analysis
├── shared/                     # shared library (NOT a skill)
│   ├── search_strategy.md
│   ├── screening.md
│   ├── data_extraction.md
│   ├── risk_of_bias.md
│   ├── reporting_standards.md
│   └── scripts/
│       ├── prisma_flow.py
│       └── meta/               # effect_sizes.py, pooling.py, plots.py, example.py
└── docs/
    ├── INSTALL.md
    └── USAGE.md
```

- Each top-level `*/SKILL.md` is **one skill**; its ID equals its directory name.
- `shared/` is the shared library. Skills refer to it as `../shared/…` (one level up). Nothing inside `shared/` is a skill — harnesses ignore it because it has no `SKILL.md`.
- Python scripts run from the repo root, e.g. `python shared/scripts/meta/example.py`.

## Requirements

- A harness that supports `SKILL.md` skills (Claude Code, OpenCode, Cursor, etc.).
- Python 3.10+ **only** for `systematic-review` (PRISMA flow diagram) and `meta-analysis` (statistics):

```bash
pip install numpy scipy pandas matplotlib
```

The other four skills (`book-review`, `narrative-review`, `critical-review`, and the writing half of `systematic-review`) need no Python.

---

## Claude Code

Claude Code discovers skills as `~/.claude/skills/<name>/SKILL.md` (one level deep). Install each skill directory plus `shared/` as siblings:

```bash
git clone https://github.com/<you>/academicskills.git /tmp/academicskills

# Symlink (stays in sync when you pull) — or use `cp -R` to copy instead.
for d in review-router book-review narrative-review critical-review \
         systematic-review meta-analysis shared; do
  ln -s "/tmp/academicskills/$d" ~/.claude/skills/
done
```

Result:

```
~/.claude/skills/
├── review-router/ … meta-analysis/   # six skills
└── shared/                            # library, sits beside them
```

Because `shared/` is a sibling of the skill directories, each skill's `../shared/…` reference resolves correctly.

**Project-local alternative:** run the same loop with `.claude/skills/` (inside your project) as the destination.

---

## OpenCode

Register the repo root as a skills source. In your project's `opencode.jsonc` (or `.opencode/opencode.jsonc`):

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "skills": ["./academicskills"]
}
```

OpenCode recursively discovers each `*/SKILL.md` and assigns the ID from the directory name — `review-router`, `book-review`, `narrative-review`, `critical-review`, `systematic-review`, `meta-analysis`. `shared/` is skipped (no `SKILL.md`).

**Global alternative:** clone into `~/.config/opencode/skills/academicskills` and it is discovered automatically.

> OpenCode also reads `~/.claude/skills` for compatibility, so the Claude Code recipe above works for OpenCode too.

---

## Other harnesses / generic

Copy or symlink the six skill directories and `shared/` into whichever skills directory your harness scans, keeping them as **siblings** so `../shared/` resolves. The skills use only `name` + `description` frontmatter, which is the common denominator across Claude Code, OpenCode, and similar harnesses.

---

## Invoking a skill

Once installed, start a session any of three ways:

1. **Auto (default)** — just describe what you want (*"Saya mau meta-analysis dari data ini"*); the skill whose `description` matches loads itself.
2. **`@skill-id` (OpenCode)** — `@brainstorm`, `@review-router`, `@meta-analysis`, `@book-review`, etc. The ID is the skill's directory name.
3. **`/command` (Claude Code)** — copy the bundled commands into `.claude/commands/`:

```bash
mkdir -p .claude/commands
cp commands/*.md .claude/commands/
```

Then use `/brainstorm`, `/review`, `/meta-analysis`, `/systematic-review`, `/scoping-review`, etc.

---

## Verify

Start a session and type:

> Help me write a review.

The `review-router` should kick in and interview you about the object, purpose, rigor, and data. If nothing appears:

1. Confirm each skill directory sits at the expected level and contains its own `SKILL.md`.
2. Confirm `shared/` is beside them (not inside one of them).
3. Confirm the skill has a non-empty `description` in its frontmatter (discovery depends on it).
