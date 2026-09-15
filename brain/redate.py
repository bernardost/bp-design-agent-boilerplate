#!/usr/bin/env python3
"""redate.py — move a decision log from `NNNN-slug.md` to `YYYY-MM-DD-slug.md`.

    python3 brain/redate.py                       # dry run: every rename and rewrite
    python3 brain/redate.py --apply               # do it
    python3 brain/redate.py --dir archive/decisions --apply

Why the shape changed. A number does two jobs at once: it identifies the file that
`[[0047-…]]` points at, and it orders the log. Ordering is fine; identity is not, because the
next free number depends on a commit the session has not fetched. Two sessions writing at the
same time both pick it, and the collision surfaces at merge, after both files exist. The date
orders the log just as well and is already on the `Date:` line; the slug identifies the file
and is chosen from what the decision says, so two sessions collide only by writing the same
decision on the same day — at which point they should collide.

A number is only unique inside one folder, so a citation of `0007` is ambiguous while two
folders still hold numbered decisions. Migrate `brain/decisions/` first and the archive after,
or check the dry run for a rewrite that points at the wrong log.

This is a one-way migration and it rewrites citations across the whole tree. Run it on a clean
tree so `git diff` is the review, and read the dry run before `--apply`.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

BRAIN = Path(__file__).resolve().parent
ROOT = BRAIN.parent

NUMBERED = re.compile(r"^(?P<num>\d{4})-(?P<slug>[a-z0-9][a-z0-9-]*)$")
DATE_LINE = re.compile(r"^Date:\s*(\d{4}-\d{2}-\d{2})", re.M)
# Where citations live. Everything else in the tree is generated, vendored, or not ours.
SCAN_SUFFIXES = {".md", ".py", ".toml", ".html"}
SKIP_PARTS = {".git", "__pycache__", "node_modules", "context"}


def scan_files() -> list[Path]:
    out = []
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file() or p.suffix not in SCAN_SUFFIXES:
            continue
        if SKIP_PARTS & set(p.parts) or p.name == "redate.py":
            continue  # this file documents the old form on purpose
        out.append(p)
    return out


def plan(folder: Path) -> tuple[dict, list]:
    """`{number: (old path, new name, slug)}` plus the files that cannot be moved."""
    renames: dict = {}
    skipped: list = []
    taken: set = set()
    for path in sorted(folder.glob("*.md")):
        m = NUMBERED.match(path.stem)
        if not m or path.stem.startswith("0000"):
            continue
        date = DATE_LINE.search(path.read_text(encoding="utf-8"))
        if not date:
            skipped.append((path, "no `Date: YYYY-MM-DD` line — add one, then re-run"))
            continue
        slug, stem = m["slug"], f"{date.group(1)}-{m['slug']}"
        # Two decisions written the same day under the same slug is a naming problem, not a
        # migration one. Suffix it so the move is lossless and let doctor.py fail on the slug.
        n = 2
        while stem in taken:
            stem, n = f"{date.group(1)}-{slug}-{n}", n + 1
        taken.add(stem)
        renames[m["num"]] = (path, stem + ".md", slug)
    return renames, skipped


def rewrite(text: str, renames: dict) -> tuple[str, int]:
    """Every way a decision is cited in practice, rewritten to `[[slug]]`.

    Bare numbers are the delicate case: `2000` is a character limit and `2026` is a year, so
    only a leading-zero token is treated as a citation. A decision log that reaches 1000
    entries can rename that last one by hand."""
    hits = 0
    for num, (_, _, slug) in renames.items():
        patterns = [
            (rf"\[\[{num}-[a-z0-9-]*(\|[^\]]*)?\]\]", rf"[[{slug}\1]]"),
            (rf"\[\[{num}(\|[^\]]*)?\]\]", rf"[[{slug}\1]]"),
            (rf"(?<![\w\-\[]){num}-[a-z0-9-]+(?![\w\-])", slug),
        ]
        if num.startswith("0"):
            patterns.append((rf"(?<![\w\-\[.]){num}(?![\w\-])", f"[[{slug}]]"))
        for pat, sub in patterns:
            text, n = re.subn(pat, sub, text)
            hits += n
    return text, hits


def strip_heading(text: str, slug: str) -> str:
    """`# 0017 — Title` → `# Title`. The number is gone from the filename; leaving it in the
    heading would be the same identifier surviving in the one place nothing checks it."""
    return re.sub(r"^#\s+\d{4}\s+—\s+", "# ", text, count=1, flags=re.M)


def git_mv(src: Path, dst: Path) -> bool:
    try:
        r = subprocess.run(["git", "-C", str(ROOT), "mv", str(src), str(dst)],
                           capture_output=True, text=True, timeout=20)
        return r.returncode == 0
    except Exception:
        return False


def main() -> int:
    apply = "--apply" in sys.argv
    folder = ROOT / "brain" / "decisions"
    if "--dir" in sys.argv:
        folder = ROOT / sys.argv[sys.argv.index("--dir") + 1]
    if not folder.exists():
        print(f"redate: {folder} does not exist")
        return 1

    renames, skipped = plan(folder)
    print(f"redate — {folder.relative_to(ROOT)}\n")
    if not renames:
        print("  nothing to migrate: no `NNNN-slug.md` decisions here.")
        for path, why in skipped:
            print(f"  skipped  {path.name} — {why}")
        return 0

    for num, (path, new_name, _) in sorted(renames.items()):
        print(f"  rename   {path.name}\n           → {new_name}")
    for path, why in skipped:
        print(f"  skipped  {path.name} — {why}")

    touched = 0
    for path in scan_files():
        text = path.read_text(encoding="utf-8")
        new, hits = rewrite(text, renames)
        if hits:
            touched += 1
            print(f"  cite     {path.relative_to(ROOT)} — {hits} citation(s)")
            if apply:
                path.write_text(new, encoding="utf-8")

    if apply:
        for num, (path, new_name, slug) in sorted(renames.items()):
            body = strip_heading(path.read_text(encoding="utf-8"), slug)
            path.write_text(body, encoding="utf-8")
            dst = path.with_name(new_name)
            if not git_mv(path, dst):
                path.rename(dst)
        print(f"\nmigrated {len(renames)} decision(s), {touched} file(s) rewritten.")
        print("Review with `git diff`, then run `python3 brain/doctor.py`.")
    else:
        print(f"\ndry run — {len(renames)} rename(s), {touched} file(s) would be rewritten.")
        print("Re-run with --apply on a clean tree so `git diff` is the review.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
