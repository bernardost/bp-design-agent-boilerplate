#!/usr/bin/env python3
"""lint_prose.py — after the assistant writes a `.md` or `.html`, hand it the sentences to fix.

Wired as a PostToolUse hook on Write, Edit and MultiEdit in `.claude/settings.json`. It runs
`brain/prose.py` on the file just written and returns the hits as context, so the assistant
rewrites them in the same turn, before the owner reads the file. The rule in AGENTS.md says
what not to write; this is the part that still holds when the rule has scrolled out.

It never blocks. A file outside the lint's scope (a braindump, a vendored skill, a product
repo) passes through silently.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROSE = ROOT / "brain" / "prose.py"


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    path = (event.get("tool_input") or {}).get("file_path") or ""
    if not path or not PROSE.exists():
        return 0
    p = Path(path)
    if p.suffix not in (".md", ".html") or not p.exists():
        return 0
    sys.path.insert(0, str(PROSE.parent))
    try:
        import prose  # noqa: E402
    except Exception:
        return 0
    if not prose.in_scope(p):
        return 0
    try:
        hits = prose.lint_file(p)
    except Exception:
        return 0
    if not hits:
        return 0
    try:
        name = str(p.resolve().relative_to(ROOT))
    except ValueError:
        name = str(p)
    lines = [f"prose.py flagged {len(hits)} sentence(s) in {name}. Rewrite them now, in this turn:"]
    for h in hits[:20]:
        lines.append(f"  line {h['line']} · {h['group']} · {h['phrase']!r} → {h['fix']}")
        lines.append(f"      {h['excerpt']}")
    if len(hits) > 20:
        lines.append(f"  … and {len(hits) - 20} more; run `python3 brain/prose.py {name}`.")
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": "\n".join(lines),
    }}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
