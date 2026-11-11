#!/usr/bin/env python3
"""prose.py — find the sentences an assistant writes on autopilot, in code rather than in prose.

    python3 brain/prose.py <file ...>          # lint; exit 1 if anything is flagged
    python3 brain/prose.py --report [dir]      # counts by phrase and by file across a tree
    python3 brain/prose.py --json <file>       # the hits as JSON, for the write hook
    python3 brain/prose.py --template          # lint the template's own text (the test)

The charter bans a list of stock phrases, and the ban held for a few turns at a time. Six
projects built from this template carried "reads as" 140 times, "lands" 145 times and
"load-bearing" 16 times, with "load-bearing" on the banned list the whole while. A rule in
prose scrolls out of the context; this file does not. `doctor.py` runs it over the brain and
fails on a file written in the last week, and a hook runs it on every `.md` or `.html` the
assistant writes, so the fix happens in the same turn.

What it flags, in four groups:

- **stock** — the charter's own list, the register the template used to teach ("reads as",
  "the move", "does the work"), and the adverbs that add nothing.
- **opener** — throat-clearing before the point: "here's the thing", "the real question is".
- **jargon** — the consulting words the deck lens bans: leverage, seamless, journey.
- **shape** — "not X, it's Y", three short sentences in a row, and the em dash, which
  `stop-slop` bans outright and this workspace now avoids.

It reads markdown with the frontmatter, fenced code, task lines and URLs removed, and HTML
with scripts, styles and tags removed. It does not lint verbatim material: braindumps,
briefings, transcripts, `context/`, archives, product repos, or a vendored skill.
"""

from __future__ import annotations

import argparse
import html as htmllib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

BRAIN = Path(__file__).resolve().parent
ROOT = BRAIN.parent

# ── what is flagged ────────────────────────────────────────────────────────────────────────

STOCK = [
    # the charter's list
    "load-bearing", "worth stating plainly", "the honest truth", "the honest answer",
    "the real tension", "carry the argument", "carries the argument", "worth naming",
    "the thing that matters", "worth noting", "worth saying", "worth mentioning",
    "it's worth", "it is worth",
    # the register the template used to teach
    "reads as", "read as a", "reads like", "the move is", "the move was", "the move here",
    "does the work", "do the work", "doing the work", "earns its", "earn its", "earned its",
    "one job", "the whole point", "that is the point", "that's the point", "the point is",
    "the answer is", "which is what", "and that is the", "quietly",
    "the one permitted", "is how a", "is how the", "is how you", "and nothing else",
    "it lands", "that lands", "lands as", "lands well", "lands flat", "lands on", "by construction",
    "the failure is", "the failure here", "the failure mode",
    # adverbs that add nothing
    "genuinely", "crucially", "importantly", "arguably", "essentially", "fundamentally",
    "truly", "incredibly", "remarkably", "notably", "interestingly", "ultimately",
    "actually", "really", "simply", "deeply", "frankly", "honestly",
    # the stop-slop crutches
    "let that sink in", "make no mistake", "this matters because",
    "here's why that matters", "a reminder that", "at its core", "at the end of the day",
    "in short", "put simply", "simply put", "in other words", "to be clear", "to be fair",
    "let's be clear", "let me be clear", "the key insight", "the core insight",
    "the key idea", "the key point", "this isn't about", "it's not about", "is not about",
    "more than just", "not just a", "not merely", "nothing more than",
]

OPENER = [
    "here's the thing", "here's what", "here's why", "here's how", "here's the",
    "here is the thing", "here is what", "here is why", "the truth is", "it turns out",
    "the uncomfortable truth", "i'll be honest", "i'm going to be honest", "can we talk about",
    "the real question", "the real issue", "the real problem", "the real work",
    "the real test", "the real risk", "the real reason", "the real answer",
    "what this means is", "the bottom line", "the takeaway", "the lesson here",
    "the thing is", "the problem is", "the catch is", "the trick is", "the trouble is",
]

JARGON = [
    "leverage", "leverages", "leveraging", "synergy", "synergies", "holistic", "robust",
    "seamless", "seamlessly", "best-in-class", "unlock", "unlocks", "unlocking", "elevate",
    "elevates", "elevating", "journey", "ecosystem", "empower", "empowers", "empowering",
    "streamline", "streamlines", "cutting-edge", "state-of-the-art", "game-changer",
    "game-changing", "delve", "delves", "tapestry", "testament", "transformative",
    "innovative", "paradigm", "foster", "fosters", "actionable",
    "impactful", "scalable", "world-class", "next-level", "deep dive", "double down",
    "move the needle", "low-hanging fruit", "circle back", "touch base",
    "at scale", "value-add", "learnings", "utilize", "utilise", "utilizing",
]

# Structures. Each is (name, compiled regex, what to do instead).
SHAPE = [
    ("not X, it's Y",
     re.compile(r"\b(?:isn't|aren't|wasn't|weren't|is not|are not|was not|were not|not|never)"
                r"\s+(?:just|merely|only|simply|about|a|an|the)?\s*[^.;:!?\n]{1,45}?[,;—]\s*"
                r"(?:it's|it is|they're|they are|it was|but rather|but a|but the|but an)\b", re.I),
     "say Y"),
    ("three short sentences",
     re.compile(r"(?:(?<=[.!?]\s)|^)([A-Z][^.!?\n]{1,28}[.!?])\s+([A-Z][^.!?\n]{1,28}[.!?])"
                r"\s+([A-Z][^.!?\n]{1,28}[.!?])(?=\s|$)"),
     "vary the rhythm"),
    ("em dash",
     re.compile(r"(?<!\*\*)(?<!\*\* )—"),
     "a full stop, a comma or a colon"),
    ("colon doing a verb's work",
     re.compile(r"(?:^|[.!?]\s+)[A-Z][^.!?:\n,]{3,24}:\s+[a-z][^.!?\n,]{3,24}[.!?](?=\s|$)"),
     "write the verb"),
]

GROUPS = (("stock", STOCK), ("opener", OPENER), ("jargon", JARGON))


def _phrase_re(words: list[str]) -> re.Pattern:
    alts = sorted((re.escape(w).replace(r"'", "['’]") for w in words), key=len, reverse=True)
    return re.compile(r"(?<![\w-])(?:" + "|".join(alts) + r")(?![\w-])", re.I)


PHRASE_RES = {name: _phrase_re(words) for name, words in GROUPS}

# ── what is read ───────────────────────────────────────────────────────────────────────────

# Verbatim material, outside material, and files with their own owners.
SKIP_DIRS = {"context", "archive", "braindumps", "briefings", "transcripts", "projects",
             "node_modules", ".git", "_canvas", "_template", "references", "brand", "workshop"}
SUFFIXES = {".md", ".html"}


def vendored_skills() -> set[str]:
    """Skill folders taken from elsewhere, read from CREDITS.md. Never linted: a refresh would
    overwrite any fix, and their voice is their author's."""
    credits = ROOT / "CREDITS.md"
    if not credits.exists():
        return set()
    return set(re.findall(r"`/([a-z0-9-]+)`", credits.read_text(encoding="utf-8")))


def in_scope(p: Path, root: Path = ROOT) -> bool:
    if p.suffix not in SUFFIXES:
        return False
    try:
        r = p.resolve().relative_to(root)
    except ValueError:
        return False
    parts = set(r.parts)
    if parts & SKIP_DIRS:
        return False
    if len(r.parts) > 2 and r.parts[0] in (".claude", ".agents") and r.parts[1] == "skills" \
            and r.parts[2] in vendored_skills():
        return False
    if r.name in ("tasks.md", "feed-items.md", "CREDITS.md", "LICENSE.md"):
        return False
    if r.parts[0] == "brain" and r.suffix == ".html" and r.parent.name == "brain":
        return False  # rendered projections (feed.html, brief.html): generated, not written
    return True


def _strip_markdown(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            head = text[:end + 4]
            text = "\n" * head.count("\n") + text[end + 4:]   # keep line numbers true
    # Italic spans quote examples and the owner's own words; they are not the writer's prose.
    text = re.sub(r"(?<![*\w])\*(?!\*)([^*]{1,400}?)\*(?![*\w])",
                  lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)
    out, fenced = [], False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("```"):
            fenced = not fenced
            out.append("")
            continue
        if fenced or s.startswith("- `") or s.startswith("|") or s.startswith("<!--") \
                or s.startswith("#"):
            out.append("")
            continue
        line = re.sub(r"https?://\S+", " ", line)
        line = re.sub(r"`[^`\n]*`", " ", line)          # code spans: file paths, commands
        line = re.sub(r"\[\[[^\]]*\]\]", " ", line)      # wiki-links are slugs, not prose
        line = re.sub(r"\^\[[^\]]*\]", " ", line)        # source tags
        out.append(line)
    return "\n".join(out)


def _strip_html(text: str) -> str:
    text = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"<(pre|code)\b[^>]*>.*?</\1>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<(?:br|/p|/h[1-6]|/li|/div|/td|/tr)\b[^>]*>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = htmllib.unescape(text)
    return re.sub(r"[ \t]+", " ", text)


def readable(p: Path) -> str:
    text = p.read_text(encoding="utf-8", errors="replace")
    return _strip_html(text) if p.suffix == ".html" else _strip_markdown(text)


# ── the lint ───────────────────────────────────────────────────────────────────────────────

def lint_text(text: str) -> list[dict]:
    """Every hit as {line, group, phrase, excerpt, fix}."""
    hits = []
    lines = text.splitlines()
    starts = []
    pos = 0
    for ln in lines:
        starts.append(pos)
        pos += len(ln) + 1

    def line_of(i: int) -> int:
        lo, hi = 0, len(starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if starts[mid] <= i:
                lo = mid
            else:
                hi = mid - 1
        return lo + 1

    def excerpt(i: int, j: int) -> str:
        ln = lines[line_of(i) - 1].strip()
        return ln if len(ln) <= 110 else ("…" + text[max(0, i - 40):j + 40].replace("\n", " ") + "…")

    for group, rx in PHRASE_RES.items():
        for m in rx.finditer(text):
            hits.append({"line": line_of(m.start()), "group": group,
                         "phrase": m.group(0).lower(), "excerpt": excerpt(m.start(), m.end()),
                         "fix": "cut it, or say the specific thing"})
    for name, rx, fix in SHAPE:
        for m in rx.finditer(text):
            hits.append({"line": line_of(m.start()), "group": "shape", "phrase": name,
                         "excerpt": excerpt(m.start(), m.end()), "fix": fix})
    hits.sort(key=lambda h: (h["line"], h["group"]))
    return hits


def lint_file(p: Path) -> list[dict]:
    return lint_text(readable(p))


def walk(root: Path, scope_root: Path | None = None):
    """Every lintable file under `root`. Scope is judged against the repo that holds it:
    `scope_root` when given, else the nearest ancestor with a `brain/` folder, else `root`."""
    if scope_root is None:
        scope_root = root
        for anc in (root, *root.parents):
            if (anc / "brain").is_dir() or (anc / "AGENTS.md").exists():
                scope_root = anc
                break
    for p in sorted(root.rglob("*")):
        if p.is_file() and in_scope(p, scope_root):
            yield p


def recently_written(days: int = 7) -> set[str] | None:
    """Repo-relative paths committed in the last `days` days or not committed at all.
    None outside a git repo, meaning: treat everything as recent."""
    try:
        log = subprocess.run(["git", "-C", str(ROOT), "log", f"--since={days}.days",
                              "--name-only", "--format="], capture_output=True, text=True,
                             timeout=20)
        if log.returncode != 0:
            return None
        status = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain",
                                 "--untracked-files=all"], capture_output=True, text=True,
                                timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    out = {ln.strip() for ln in log.stdout.splitlines() if ln.strip()}
    for ln in status.stdout.splitlines():
        if len(ln) > 3:
            out.add(ln[3:].strip().split(" -> ")[-1])
    return out


# ── output ─────────────────────────────────────────────────────────────────────────────────

def print_hits(p: Path, hits: list[dict]) -> None:
    try:
        name = str(p.resolve().relative_to(ROOT))
    except ValueError:
        name = str(p)
    print(f"{name}: {len(hits)} hit(s)")
    for h in hits:
        print(f"  {h['line']:>4}  {h['group']:<7} {h['phrase']!r:<28} → {h['fix']}")
        print(f"        {h['excerpt']}")


def report(root: Path) -> int:
    by_phrase: Counter = Counter()
    by_file: Counter = Counter()
    files = 0
    for p in walk(root):
        files += 1
        hs = lint_file(p)
        if hs:
            by_file[str(p.relative_to(root))] = len(hs)
            by_phrase.update(h["phrase"] for h in hs)
    total = sum(by_phrase.values())
    print(f"prose report · {root}\n{files} file(s) read · {total} hit(s) in {len(by_file)} file(s)\n")
    if not total:
        return 0
    print("by phrase")
    for phrase, n in by_phrase.most_common(25):
        print(f"  {n:5d}  {phrase}")
    print("\nby file")
    for f, n in by_file.most_common(15):
        print(f"  {n:5d}  {f}")
    return 0


TEMPLATE_PATHS = ("AGENTS.md", "README.md", ".claude/skills", "brain")


def template_files() -> list[Path]:
    out = []
    for t in TEMPLATE_PATHS:
        p = ROOT / t
        if p.is_file() and in_scope(p):
            out.append(p)
        elif p.is_dir():
            out.extend(walk(p))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--report", action="store_true", help="counts across a tree")
    ap.add_argument("--json", action="store_true", help="hits as JSON")
    ap.add_argument("--template", action="store_true", help="lint the template's own text")
    args = ap.parse_args(argv)

    if args.report:
        return report(Path(args.paths[0]).resolve() if args.paths else ROOT)

    if args.template:
        paths = template_files()
    else:
        paths = []
        for a in args.paths:
            p = Path(a)
            if p.is_dir():
                paths.extend(walk(p))
            elif p.exists():
                paths.append(p)
    if not paths:
        print("nothing to lint")
        return 0

    results = {}
    for p in paths:
        hs = lint_file(p)
        if hs:
            results[str(p)] = hs
    if args.json:
        print(json.dumps(results, ensure_ascii=False))
        return 1 if results else 0
    for p, hs in results.items():
        print_hits(Path(p), hs)
    total = sum(len(h) for h in results.values())
    if total:
        print(f"\n{total} hit(s) in {len(results)} file(s) of {len(paths)} read")
        return 1
    print(f"clean · {len(paths)} file(s) read")
    return 0


if __name__ == "__main__":
    sys.exit(main())
