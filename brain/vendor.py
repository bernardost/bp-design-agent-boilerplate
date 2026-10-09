#!/usr/bin/env python3
"""vendor.py — take third-party skills into this workspace, with their credits.

    python3 brain/vendor.py            # refresh every vendored collection from upstream
    python3 brain/vendor.py --check    # report what would change; write nothing

Some skills are better taken whole from the people who wrote them than rewritten here. This
copies them into `.claude/skills/` and `.agents/skills/` exactly as published, pins the commit
they came from, and writes `CREDITS.md` at the repo root: author, licence, commit, and the
licence text itself, which is what the MIT licence asks for.

**A vendored skill is never edited in place.** The next refresh overwrites it. A rule this
workspace wants on top of one goes in `AGENTS.md` or in a skill of our own that cites it.

The collections are listed below, not in `workspace.toml`: what the template ships is the
template's decision, and a clone gets the same set through `/update`, because the skill folders
are template-owned in `brain/upstream.py`.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BRAIN = Path(__file__).resolve().parent
ROOT = BRAIN.parent
TARGETS = (ROOT / ".claude" / "skills", ROOT / ".agents" / "skills")

# One entry per collection. `skills` is the subfolder holding `<name>/SKILL.md` directories;
# every directory in it is taken. `credit` is the line a reader needs.
COLLECTIONS = [
    {
        "name": "jakubkrehel/skills",
        "repo": "https://github.com/jakubkrehel/skills",
        "skills": "skills",
        "manifest": ".claude-plugin/plugin.json",      # carries `version`
        "credit": "Jakub Krehel — interfaces.dev · jakub.kr/skills",
        "about": ("Thirteen skills for building good product interfaces: the `better-*` domain "
                  "skills (UI polish, typography, colours, accessibility, layout, writing), "
                  "`better-interface` and `interface-review` that run them as a review, and the "
                  "workbenches `break`, `state-machine`, `variant`, `build-design` and "
                  "`explain-interface`. Written for product code; in this workspace they apply "
                  "inside a product repo under `projects/` and to playground pieces."),
    },
]


def clone(repo: str, into: Path) -> str:
    subprocess.run(["git", "clone", "--depth", "1", "--quiet", repo, str(into)],
                   check=True, timeout=180)
    return subprocess.run(["git", "-C", str(into), "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()


def differs(a: Path, b: Path) -> bool:
    if not b.exists():
        return True
    fa = {p.relative_to(a): p.read_bytes() for p in a.rglob("*") if p.is_file()}
    fb = {p.relative_to(b): p.read_bytes() for p in b.rglob("*") if p.is_file()}
    return fa != fb


def main() -> int:
    check = "--check" in sys.argv
    credits = ["# Credits — skills taken from elsewhere\n",
               "Written by `python3 brain/vendor.py`, which is also how they are refreshed. "
               "**Vendored skills are never edited in place**; a refresh overwrites them. "
               "A rule this workspace wants on top of one goes in `AGENTS.md`, or in a skill of "
               "our own that cites it.\n"]
    changed = 0
    with tempfile.TemporaryDirectory() as tmp:
        for col in COLLECTIONS:
            src = Path(tmp) / col["name"].replace("/", "__")
            sha = clone(col["repo"], src)
            version = ""
            if col.get("manifest") and (src / col["manifest"]).exists():
                version = json.loads((src / col["manifest"]).read_text()).get("version", "")
            lic_path = next((p for p in src.iterdir() if p.name.upper().startswith("LICENSE")), None)
            licence = lic_path.read_text(encoding="utf-8").strip() if lic_path else "(no licence file upstream)"
            names = sorted(p.name for p in (src / col["skills"]).iterdir()
                           if (p / "SKILL.md").exists())
            for name in names:
                for target in TARGETS:
                    dst = target / name
                    if differs(src / col["skills"] / name, dst):
                        changed += 1
                        if check:
                            print(f"  would update {dst.relative_to(ROOT)}")
                            continue
                        if dst.exists():
                            shutil.rmtree(dst)
                        shutil.copytree(src / col["skills"] / name, dst)
            head = f"## {col['name']}" + (f" · v{version}" if version else "")
            credits += [f"\n{head}\n",
                        f"**{col['credit']}** · {col['repo']} · commit `{sha[:12]}`\n",
                        f"{col['about']}\n",
                        "Skills: " + " · ".join(f"`/{n}`" for n in names) + "\n",
                        "<details><summary>Licence</summary>\n\n```\n" + licence + "\n```\n</details>\n"]
            print(f"{col['name']}: {len(names)} skill(s) at {sha[:12]}" + (f" (v{version})" if version else ""))
    if check:
        print(f"{changed} folder(s) would change" if changed else "everything matches upstream")
        return 1 if changed else 0
    (ROOT / "CREDITS.md").write_text("\n".join(credits), encoding="utf-8")
    print(f"wrote CREDITS.md · {changed} folder(s) written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
