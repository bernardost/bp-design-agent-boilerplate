#!/usr/bin/env python3
"""review.py — build the page for a review round across several playground pieces.

    python3 brain/review.py <round> <slug>[:<file>] [<slug>[:<file>] ...]
                            [--title "Six additions, round four"]
                            [--rec <slug>=<case numbers>=<recommendation in words>] [--open]

    python3 brain/review.py additions-v04 board-foot:v04-slides-left.html jump-menu \\
        --title "Six additions, round four" \\
        --rec "jump-menu=2=The drawer on the left, under the button that opened it"

This is the one structure for asking the owner to react to the cases of more than one piece:
one case on screen at a time, four reactions, a note, and a single paste back into the
session. It replaces stacked frames with a list of questions underneath, which made the owner
scroll twice for every answer. It writes `brain/review-<round>.html`, built from
`brain/playground/_template/review.html`, and the page loads the pieces by relative path
(`playground/<slug>/<file>`), so it has to sit in `brain/`.

**The cases are read, never retyped.** For each piece this opens the version under review and
reads `data-case` and `data-note` from its `<template id="screen">`, in the order the canvas
numbers them, so case 02 here is the `case-02` anchor there. A piece with no `data-case` gets
one case, the whole piece. Without `:<file>` the piece's final version is used, else its
latest. Pieces built with `boards` (artboards on a canvas) number their anchors differently
and are not supported: review them in the piece.

`--rec` is the builder's recommendation for one piece: the 1-based numbers of the cases it
recommends, then the words. Give it for every piece the builder has an opinion on; a page with
no recommendation shows none.

The output is a projection of the pieces and is gitignored. The owner's reactions live in the
browser (`localStorage`, keyed by the round) and come back as text the owner pastes.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

BRAIN = Path(__file__).resolve().parent
sys.path.insert(0, str(BRAIN))

import playground  # noqa: E402

TEMPLATE = BRAIN / "playground" / "_template" / "review.html"
ROUND_NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class _Cases(HTMLParser):
    """Every element carrying `data-case`, in document order, with its `data-note`."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.cases: list[dict] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "data-case" in a:
            self.cases.append({"name": (a["data-case"] or "").strip(),
                               "note": (a.get("data-note") or "").strip()})


def read_cases(html_text: str) -> list[dict]:
    """The cases of a piece file: what `canvas.js` finds in `<template id="screen">`."""
    m = re.search(r'<template\s+id=["\']screen["\'][^>]*>(.*?)</template>', html_text, re.S | re.I)
    parser = _Cases()
    parser.feed(m.group(1) if m else "")
    return parser.cases


def parse_rec(spec: str) -> tuple[str, list[int], str]:
    parts = spec.split("=", 2)
    if len(parts) != 3 or not parts[0] or not parts[2].strip():
        raise SystemExit(f"--rec wants <slug>=<case numbers>=<words>, got: {spec!r}")
    try:
        nums = [int(n) for n in re.split(r"[,\s]+", parts[1].strip()) if n]
    except ValueError:
        raise SystemExit(f"--rec case numbers are 1-based integers, got: {parts[1]!r}")
    return parts[0], nums, parts[2].strip()


def build(round_name: str, specs: list[str], title: str, recs: list[str]) -> tuple[list[dict], str]:
    """The `P` array the page runs on, and a line per piece for the report."""
    if not ROUND_NAME.match(round_name):
        raise SystemExit(f"round name must be lowercase-kebab, got {round_name!r}")
    known = {p["slug"]: p for p in playground.pieces()}
    rec_by_slug = {}
    for spec in recs:
        slug, nums, words = parse_rec(spec)
        rec_by_slug[slug] = (nums, words)
    data, report = [], []
    for spec in specs:
        slug, _, file = spec.partition(":")
        piece = known.get(slug)
        if not piece:
            raise SystemExit(f"no piece {slug!r} in brain/playground/ (have: {', '.join(sorted(known)) or 'none'})")
        file = file or piece["final_file"] or (piece["versions"][-1]["file"] if piece["versions"] else "")
        path = playground.DIR / slug / file
        if not file or not path.is_file():
            raise SystemExit(f"{slug}: no file {file!r} to review")
        cases = read_cases(path.read_text(encoding="utf-8"))
        if not cases:
            cases = [{"name": "The whole piece", "note": piece["brief"]}]
        nums, words = rec_by_slug.pop(slug, ([], ""))
        bad = [n for n in nums if not 1 <= n <= len(cases)]
        if bad:
            raise SystemExit(f"{slug}: --rec names case(s) {bad}, but {file} has {len(cases)}")
        data.append({"slug": slug, "title": piece["title"], "file": file, "brief": piece["brief"],
                     "rec": words, "recn": nums, "cases": cases})
        report.append(f"  {slug}  {file}  {len(cases)} case(s)" + (f"  recommends {nums}" if nums else ""))
    if rec_by_slug:
        raise SystemExit(f"--rec names piece(s) not in this round: {', '.join(rec_by_slug)}")
    return data, "\n".join(report)


def render(round_name: str, title: str, data: list[dict]) -> str:
    page = TEMPLATE.read_text(encoding="utf-8")
    round_js = json.dumps({"key": f"review-{round_name}", "title": title}, ensure_ascii=False)
    # `</` inside a JSON string would close the script element early.
    pieces_js = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    for marker, value in (("/*ROUND*/{key:'round',title:'Review'}", round_js), ("/*PIECES*/[]", pieces_js)):
        if marker not in page:
            raise SystemExit(f"template is missing {marker!r}; brain/playground/_template/review.html was edited")
        page = page.replace(marker, value, 1)
    return page.replace("{{ROUND_TITLE}}", title.replace("&", "&amp;").replace("<", "&lt;"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("round", help="lowercase-kebab name of the round, e.g. additions-v04")
    ap.add_argument("pieces", nargs="+", help="<slug> or <slug>:<file>, in the order they are reviewed")
    ap.add_argument("--title", help="heading for the round; default is the round name")
    ap.add_argument("--rec", action="append", default=[], metavar="SLUG=NUMS=WORDS")
    ap.add_argument("--open", action="store_true")
    args = ap.parse_args()

    title = args.title or args.round.replace("-", " ").capitalize()
    data, report = build(args.round, args.pieces, title, args.rec)
    out = BRAIN / f"review-{args.round}.html"
    out.write_text(render(args.round, title, data), encoding="utf-8")
    total = sum(len(p["cases"]) for p in data)
    print(f"review  {out.relative_to(BRAIN.parent)}  {len(data)} piece(s), {total} case(s)\n{report}")
    if args.open:
        subprocess.run(["open", str(out)], check=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
