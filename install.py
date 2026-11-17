#!/usr/bin/env python3
"""Install the Master Academic Review skills and /mar-* slash commands.

    python install.py                 # Claude Code + OpenCode, for your user account
    python install.py --dry-run       # show what would change, change nothing
    python install.py --claude        # Claude Code only
    python install.py --opencode      # OpenCode only
    python install.py --project .     # into this project (.claude/, .opencode/)
    python install.py --uninstall     # remove only what this installer put there

Where things go (user install):

    Claude Code  skills    ~/.claude/skills/<skill>/SKILL.md  (+ shared/)
                 commands  ~/.claude/commands/mar-*.md
    OpenCode     skills    read from ~/.claude/skills (OpenCode's compatibility path);
                           with --opencode alone: ~/.config/opencode/skills/
                 commands  ~/.config/opencode/commands/mar-*.md

Files are copied (no symlinks, so Windows needs no Developer Mode) and the home
folder comes from Python, not from "~", so the shell cannot mangle the path.
A folder that already exists and was not installed by this script (a skill of
the same name from another pack) is left alone unless you pass --force.
Re-run after `git pull` to update. Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path
import contextlib

REPO = Path(__file__).resolve().parent
MANIFEST = ".masteracademicreview-install.json"
MARKER = "shared/jev.md"            # every skill of this suite points to the JEV protocol
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", "out", ".pytest_cache")


def version() -> str:
    text = (REPO / "shared" / "scripts" / "__init__.py").read_text(encoding="utf-8")
    return text.split('__version__ = "', 1)[1].split('"', 1)[0]


def repo_skills() -> list[Path]:
    return sorted(p.parent for p in REPO.glob("*/SKILL.md"))


def repo_commands() -> list[Path]:
    return sorted((REPO / "commands").glob("mar-*.md"))


def targets(home: Path, project: Path | None, claude: bool, opencode: bool) -> dict[str, Path]:
    """Folders to write, keyed by role."""
    base_claude = (project / ".claude") if project else home / ".claude"
    base_opencode = (project / ".opencode") if project else home / ".config" / "opencode"
    out: dict[str, Path] = {}
    if claude:
        out["skills"] = base_claude / "skills"
        out["claude_commands"] = base_claude / "commands"
    if opencode:
        out.setdefault("skills", base_opencode / "skills")   # Claude path also serves OpenCode
        out["opencode_commands"] = base_opencode / "commands"
    return out


def read_manifest(folder: Path) -> list[str]:
    try:
        return json.loads((folder / MANIFEST).read_text(encoding="utf-8")).get("items", [])
    except (OSError, ValueError):
        return []


def write_manifest(folder: Path, items: list[str], dry: bool) -> None:
    if dry:
        return
    path = folder / MANIFEST
    if items:
        path.write_text(json.dumps({"package": "masteracademicreview", "version": version(),
                                    "items": sorted(set(items))}, indent=2), encoding="utf-8")
    elif path.exists():
        path.unlink()


def is_ours(path: Path, recorded: list[str]) -> bool:
    """Installed by us before (manifest), or recognisably this suite's file."""
    if path.name in recorded:
        return True
    if path.is_dir() and path.name == "shared":
        return (path / "scripts" / "check_review.py").exists() and (path / "jev.md").exists()
    if path.is_dir():
        skill = path / "SKILL.md"
        return skill.exists() and MARKER in skill.read_text(encoding="utf-8", errors="replace")
    if path.suffix == ".md":
        return "description: MAR · " in path.read_text(encoding="utf-8", errors="replace")
    return False


def copy_item(src: Path, dst: Path, dry: bool) -> None:
    if dry:
        return
    if dst.is_dir():
        shutil.rmtree(dst)
    elif dst.exists():
        dst.unlink()
    if src.is_dir():
        shutil.copytree(src, dst, ignore=IGNORE)
    else:
        shutil.copy2(src, dst)


def install_into(folder: Path, sources: list[Path], force: bool, dry: bool, log: list[str]) -> list[str]:
    recorded = read_manifest(folder)
    if not dry:
        folder.mkdir(parents=True, exist_ok=True)
    done = []
    for src in sources:
        dst = folder / src.name
        if dst.exists() and not force and not is_ours(dst, recorded):
            log.append(f"  skip   {dst}  (exists and is not from this suite; --force to replace)")
            continue
        log.append(f"  {'update' if dst.exists() else 'add':6} {dst}")
        copy_item(src, dst, dry)
        done.append(src.name)
    keep = [name for name in recorded if (folder / name).exists() and name not in done]
    write_manifest(folder, done + keep, dry)
    return done


def remove_legacy_commands(folder: Path, skill_ids: set[str], dry: bool, log: list[str]) -> None:
    """Unprefixed commands shipped before 0.1.2 (review.md, meta-analysis.md, ...)."""
    if not folder.exists():
        return
    for old in sorted(folder.glob("*.md")):
        if old.name.startswith("mar-") or not (folder / f"mar-{old.name}").exists():
            continue
        text = old.read_text(encoding="utf-8", errors="replace")
        if any(f"`{sid}` skill" in text for sid in skill_ids):
            log.append(f"  remove {old}  (old unprefixed command)")
            if not dry:
                old.unlink()


def uninstall_from(folder: Path, dry: bool, log: list[str]) -> None:
    for name in read_manifest(folder):
        path = folder / name
        if path.exists():
            log.append(f"  remove {path}")
            if not dry:
                shutil.rmtree(path) if path.is_dir() else path.unlink()
    if (folder / MANIFEST).exists():
        write_manifest(folder, [], dry)


def run(home: Path, project: Path | None, claude: bool, opencode: bool,
        uninstall: bool = False, force: bool = False, dry: bool = False) -> list[str]:
    log: list[str] = []
    places = targets(home, project, claude, opencode)
    skills = [*repo_skills(), REPO / "shared"]
    commands = repo_commands()
    skill_ids = {p.name for p in repo_skills()}
    for role, folder in places.items():
        log.append(f"{role}: {folder}")
        if uninstall:
            uninstall_from(folder, dry, log)
        elif role == "skills":
            install_into(folder, skills, force, dry, log)
        else:
            install_into(folder, commands, force, dry, log)
            remove_legacy_commands(folder, skill_ids, dry, log)
    return log


def selftest() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp)
        foreign = home / ".claude" / "skills" / "brainstorm"
        foreign.mkdir(parents=True)
        (foreign / "SKILL.md").write_text("---\nname: brainstorm\n---\nsomeone else's skill\n", encoding="utf-8")
        legacy = home / ".claude" / "commands" / "review.md"
        legacy.parent.mkdir(parents=True)
        legacy.write_text("Load the `review-router` skill.\n", encoding="utf-8")

        dry = run(home, None, True, True, dry=True)
        assert not (home / ".claude" / "skills" / "review-router").exists(), "dry run wrote files"
        assert any("skip" in line and "brainstorm" in line for line in dry)

        run(home, None, True, True)
        skills = home / ".claude" / "skills"
        n_skills = len(repo_skills())
        assert (skills / "review-router" / "SKILL.md").exists()
        assert (skills / "shared" / "scripts" / "check_review.py").exists()
        assert "someone else's skill" in (foreign / "SKILL.md").read_text(encoding="utf-8"), "foreign skill replaced"
        assert len(list((home / ".claude" / "commands").glob("mar-*.md"))) == len(repo_commands())
        assert len(list((home / ".config" / "opencode" / "commands").glob("mar-*.md"))) == len(repo_commands())
        assert not legacy.exists(), "old unprefixed command not removed"
        assert not list(skills.rglob("__pycache__")), "caches copied"
        assert len(read_manifest(skills)) == n_skills          # 16 skills + shared - foreign brainstorm

        run(home, None, True, True)                              # idempotent update
        assert len(read_manifest(skills)) == n_skills

        run(home, None, True, True, uninstall=True)
        assert not (skills / "review-router").exists() and not (skills / "shared").exists()
        assert (foreign / "SKILL.md").exists(), "uninstall touched a foreign skill"
        assert not list((home / ".claude" / "commands").glob("mar-*.md"))

        run(home, None, False, True)                             # OpenCode only: its own skills folder
        assert (home / ".config" / "opencode" / "skills" / "review-router" / "SKILL.md").exists()

        proj = home / "proj"
        run(home, proj, True, False)
        assert (proj / ".claude" / "skills" / "meta-analysis" / "SKILL.md").exists()
    print(f"install selftest OK ({len(repo_skills())} skills, {len(repo_commands())} commands)")


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        with contextlib.suppress(AttributeError, ValueError):
            stream.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description="Install the Master Academic Review skills and /mar-* commands.")
    p.add_argument("--claude", action="store_true", help="Claude Code only")
    p.add_argument("--opencode", action="store_true", help="OpenCode only")
    p.add_argument("--project", type=Path, help="install into this project folder instead of your user account")
    p.add_argument("--uninstall", action="store_true", help="remove what this installer added")
    p.add_argument("--force", action="store_true", help="replace same-named folders from other packs")
    p.add_argument("--dry-run", action="store_true", help="print the plan, change nothing")
    p.add_argument("--home", type=Path, default=Path.home(), help=argparse.SUPPRESS)
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args(argv)
    if a.selftest:
        selftest()
        return 0
    claude, opencode = (a.claude or not a.opencode), (a.opencode or not a.claude)
    project = a.project.resolve() if a.project else None
    log = run(a.home, project, claude, opencode, a.uninstall, a.force, a.dry_run)
    head = "DRY RUN, nothing changed" if a.dry_run else ("Uninstalled" if a.uninstall else "Installed")
    print(f"Master Academic Review {version()}: {head}")
    print("\n".join(log))
    if not a.uninstall and not a.dry_run:
        print("\nNext: open a NEW session (skills and commands load at start), then type /mar")
        print("      (Claude Code) or @review-router (OpenCode). Update later: git pull, then run this again.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
