#!/usr/bin/env python3
"""guard_push.py — ask before any `git push` that leaves this workspace's own repo.

Wired as a PreToolUse hook on Bash in `.claude/settings.json`. Push-as-you-go is standing
permission to push *the workspace*. A product repo cloned under `projects/` has its own remote,
its own branches and its own review process, and a session that `cd`s into one and follows the
workspace's rule pushes client code to whatever branch it is on. A rule in AGENTS.md says not
to; this is the part that still holds when the rule has scrolled out of the session.

It never blocks. It turns the push into a question, and a push inside the workspace's own repo
(or one of its worktrees) passes through untouched.
"""

from __future__ import annotations

import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def common_dir(path: Path) -> Path | None:
    """The shared `.git` of whatever repo holds `path`. Worktrees of one repo share it, so a
    push from a workspace worktree counts as the workspace."""
    try:
        r = subprocess.run(["git", "-C", str(path), "rev-parse", "--path-format=absolute",
                            "--git-common-dir"], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return Path(r.stdout.strip()).resolve() if r.returncode == 0 and r.stdout.strip() else None


def places(command: str, cwd: Path) -> list[Path]:
    """Every directory the command could push from: the cwd, each `cd X`, and each
    `git -C X`. Over-inclusive on purpose — a false question costs one keystroke."""
    try:
        words = shlex.split(command, posix=True)
    except ValueError:
        words = command.split()
    out = [cwd]
    for i, w in enumerate(words[:-1]):
        if w in ("cd", "pushd", "-C"):
            out.append((cwd / Path(words[i + 1]).expanduser()))
    return out


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    command = (event.get("tool_input") or {}).get("command") or ""
    if not re.search(r"\bgit\b.*\bpush\b", command):
        return 0
    cwd = Path(event.get("cwd") or ROOT)
    home = common_dir(ROOT)
    elsewhere = []
    for p in places(command, cwd):
        if not p.exists():
            continue
        cd = common_dir(p)
        if cd and home and cd != home:
            elsewhere.append(str(p))
    if not elsewhere:
        return 0
    where = elsewhere[0]
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason": (
            f"This push targets a repo other than the workspace ({where}). Push-as-you-go "
            "covers the workspace only; a product repo pushes on its own rules."),
    }}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
