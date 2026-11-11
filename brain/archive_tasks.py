#!/usr/bin/env python3
"""archive_tasks.py — move done tasks that have been done for a month out of `brain/tasks.md`.

    python3 brain/archive_tasks.py            # move them, print what moved
    python3 brain/archive_tasks.py --check    # say what would move, write nothing
    python3 brain/archive_tasks.py --days 60  # a longer grace period

`tasks.md` was the record of every task ever closed, and every session read it whole before
touching the project. One project's file reached 203 kilobytes and 2,328 lines, every task
done and none open: fifty thousand tokens of finished work read before any change. The file
stays the record; the old part of the record lives in `archive/tasks.md`.

A task line carries no date, so the date a task became `done` comes from `git blame`: marking
it done changed the line, and blame stamps that change. A line not committed yet, or in a
tree with no git, stays where it is. Done tasks younger than the grace period stay too, so a
hand-over can still show what this fortnight finished.

Moved lines keep their `##` project and `###` stage headings in the archive, appended under a
dated heading, so a reader can still tell which strand and stage a task belonged to.
`doctor.py` fails `tasks.md` past 300 lines and reports it past 200; `/close` runs this.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

BRAIN = Path(__file__).resolve().parent
ROOT = BRAIN.parent
TASKS = BRAIN / "tasks.md"
ARCHIVE = ROOT / "archive" / "tasks.md"
DONE = re.compile(r"^- `done`")


def blame_dates(path: Path) -> dict[int, datetime] | None:
    """`line number -> the time that line last changed`, from git. None when git cannot say
    (no repo, no commits, or the file is untracked); uncommitted lines are left out."""
    try:
        out = subprocess.run(["git", "-C", str(ROOT), "blame", "--line-porcelain",
                              "--", str(path.relative_to(ROOT))],
                             capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    dates: dict[int, datetime] = {}
    line_no = None
    committed = True
    for ln in out.stdout.splitlines():
        m = re.match(r"^[0-9a-f]{40} \d+ (\d+)", ln)
        if m:
            line_no = int(m.group(1))
            committed = not ln.startswith("0" * 40)
        elif ln.startswith("author-time ") and line_no is not None and committed:
            dates[line_no] = datetime.fromtimestamp(int(ln.split()[1]), tz=timezone.utc)
    return dates


def partition(lines: list[str], dates: dict[int, datetime], cutoff: datetime):
    """Split the file into (kept lines, moved blocks). A moved block is a done task line plus
    its indented note lines, paired with the heading path above it."""
    kept, moved = [], []
    heading: list[str] = ["", ""]      # current `##` and `###`
    i, fenced = 0, False
    while i < len(lines):
        line = lines[i]
        if line.lstrip().startswith("```"):
            fenced = not fenced
        if not fenced:
            if line.startswith("## "):
                heading = [line, ""]
            elif line.startswith("### "):
                heading[1] = line
        if (not fenced and DONE.match(line) and (i + 1) in dates
                and dates[i + 1] < cutoff):
            block = [line]
            j = i + 1
            while j < len(lines) and lines[j].startswith("      ") and lines[j].strip():
                block.append(lines[j])
                j += 1
            moved.append((tuple(heading), block))
            i = j
            continue
        kept.append(line)
        i += 1
    return kept, moved


def archive_text(moved, today: str) -> str:
    out = [f"\n## Archived {today}\n"]
    last = None
    for heading, block in moved:
        if heading != last:
            for h in heading:
                if h:
                    out.append(h)
            out.append("")
            last = heading
        out.extend(block)
    out.append("")
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="report only; write nothing")
    ap.add_argument("--days", type=int, default=30, help="grace period for done tasks")
    args = ap.parse_args(argv)

    if not TASKS.exists():
        print("brain/tasks.md is missing")
        return 1
    dates = blame_dates(TASKS)
    if dates is None:
        print("git cannot date the lines of brain/tasks.md; nothing moved")
        return 0
    lines = TASKS.read_text(encoding="utf-8").split("\n")
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=args.days)
    kept, moved = partition(lines, dates, cutoff)
    if not moved:
        print(f"nothing to archive: no task done for more than {args.days} days")
        return 0
    n = len(moved)
    if args.check:
        print(f"{n} done task(s) older than {args.days} days would move to archive/tasks.md")
        return 0
    ARCHIVE.parent.mkdir(exist_ok=True)
    head = ("# Archived tasks\n\n*Done tasks moved out of `brain/tasks.md` by "
            "`python3 brain/archive_tasks.py`. The record, not the backlog; never cite a "
            "task by key.*\n")
    existing = ARCHIVE.read_text(encoding="utf-8") if ARCHIVE.exists() else head
    today = datetime.now().strftime("%Y-%m-%d")
    ARCHIVE.write_text(existing.rstrip("\n") + "\n" + archive_text(moved, today),
                       encoding="utf-8")
    TASKS.write_text("\n".join(kept), encoding="utf-8")
    print(f"moved {n} done task(s) to archive/tasks.md · brain/tasks.md is now "
          f"{len(kept)} line(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
