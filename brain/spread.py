#!/usr/bin/env python3
"""spread.py — render `brain/explorations/*.md` as a page you can judge at a glance.

    python3 brain/spread.py [file ...] [--open]

`/explore` produces six to eight directions. As prose that is a wall of text, and a wall of
text is the thing an owner cannot actually judge — they read the first two, skim the rest, and
pick the one that was described best rather than the one that is best. This renders the same
file as a grid: every direction's specimen, pitch and verdict on one screen, side by side.

**The markdown file stays the truth.** This writes a projection next to it and is never read
back — same contract as `feed.py`. Delete the HTML and nothing is lost.

The specimen — a fenced ```specimen block inside each direction — is authored by the agent,
not derived from the prose, because a script cannot infer a palette from a paragraph. It goes
into a sandboxed `srcdoc` iframe, which is deliberate on two counts: a direction's own colours
and type must not be overridden by this page's house style, and its CSS must not leak out and
wreck the page.

House style comes from `feed.py` — one stylesheet for the whole workspace, never a second copy.
"""

from __future__ import annotations

import argparse
import html
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BRAIN = Path(__file__).resolve().parent
ROOT = BRAIN.parent
DIR = BRAIN / "explorations"

sys.path.insert(0, str(BRAIN))
from config import PROJECT_NAME, MULTI_PROJECT, PROJECT_LABEL  # noqa: E402
from feed import CSS, FONT_LINK, glossary, render_md  # noqa: E402

SPECIMEN_H = 208   # px — a specimen is a token card, so a fixed frame keeps the grid even


# ---------------------------------------------------------------------------------------------
# Reading an exploration
# ---------------------------------------------------------------------------------------------

def project_kicker(ex: dict) -> str:
    """` · Client Portal`, or nothing at all in a one-project workspace."""
    key = ex.get("project", "")
    if not MULTI_PROJECT or not key or key == "all":
        return ""
    return " · " + html.escape(PROJECT_LABEL.get(key, key))


def parse(path: Path) -> dict:
    """One exploration file → the shape `brain/explorations/README.md` specifies.

    Tolerant on purpose: a half-written exploration should still render, because seeing the
    three directions that exist is how you notice the other five are missing.
    """
    text = path.read_text(encoding="utf-8")

    body = text
    fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    tags: list[str] = []
    if fm:
        body = text[fm.end():]
        t = re.search(r"^tags:\s*\[(.*?)\]", fm.group(1), re.M)
        if t:
            tags = [x.strip() for x in t.group(1).split(",") if x.strip()]

    head = re.search(r"^#\s+(.+)$", body, re.M)
    title = head.group(1).strip() if head else path.stem

    seed = re.search(r"^Seed:\s*([^\n·]+)", body, re.M)
    brief = re.search(r"^(?:.*·\s*)?Brief:\s*([^\n]+)", body, re.M)

    went = re.search(r"^##\s*Where it went\s*\n(.*?)(?=\n##\s|\Z)", body, re.M | re.S)
    went_text = (went.group(1).strip() if went else "")

    directions = []
    for i, chunk in enumerate(re.split(r"^###\s+", body, flags=re.M)[1:]):
        line, _, rest = chunk.partition("\n")
        m = re.match(r"^([A-Za-z0-9]+)\s*[—–-]\s*(.+)$", line.strip())
        letter, name = (m.group(1), m.group(2)) if m else (chr(65 + i), line.strip())

        spec = re.search(r"```specimen\s*\n(.*?)```", rest, re.S)
        rest_wo = rest[:spec.start()] + rest[spec.end():] if spec else rest

        v = re.search(r"^Verdict:\s*(live|rejected)\b\s*[—–-]?\s*(.*)$",
                      rest_wo, re.M | re.I)
        pitch = re.sub(r"^Verdict:.*$", "", rest_wo, flags=re.M).strip()
        # A direction's own heading level would fight the page's; the pitch is prose.
        pitch = re.sub(r"^#{1,6}\s+", "", pitch, flags=re.M)

        directions.append({
            "letter": letter.strip(),
            "name": name.strip(),
            "pitch": pitch,
            "specimen": spec.group(1).strip() if spec else None,
            "verdict": (v.group(1).lower() if v else None),
            "reason": (v.group(2).strip() if v else ""),
        })

    return {
        "path": path, "title": title, "tags": tags,
        # Which strand of the engagement these directions belong to. Directions are judged
        # against one project's brief and one project's lens, so a page that does not say
        # which is a page whose verdicts cannot be checked later.
        "project": (m.group(1).strip() if fm and (m := re.search(
            r"^project:\s*(\S+)\s*$", fm.group(1), re.M)) else ""),
        "seed": seed.group(1).strip() if seed else "",
        "brief": brief.group(1).strip() if brief else "",
        "directions": directions, "went": went_text,
    }


# ---------------------------------------------------------------------------------------------
# The page
# ---------------------------------------------------------------------------------------------

PAGE_CSS = f"""
/* Wider than the feed on purpose: eight directions have to be comparable without scrolling,
   and comparison is the entire job of this page. */
.wrap{{max-width:1180px}}

.spread{{display:grid;gap:34px 26px;margin:0 0 60px;
  grid-template-columns:repeat(auto-fill,minmax(248px,1fr))}}

.dir{{display:flex;flex-direction:column;min-width:0}}
/* Rejected directions stay — greyed and in place, never hidden. Keeping them is the whole
   reason the file exists; hiding them would make the page disagree with the record. */
.dir.rejected{{opacity:.42;filter:saturate(.15);transition:opacity .18s,filter .18s}}
.dir.rejected:hover{{opacity:1;filter:none}}

.dir .frame{{height:{SPECIMEN_H}px;border:1px solid var(--rule);background:var(--paper);
  overflow:hidden;position:relative}}
.dir .frame iframe{{width:100%;height:100%;border:0;display:block}}
.dir .frame.empty{{display:flex;align-items:center;justify-content:center;
  background:var(--wash);border-style:dashed}}
.dir .frame.empty span{{font-family:var(--mono);font-size:11px;letter-spacing:.09em;
  text-transform:uppercase;color:var(--ochre)}}

.dir .letter{{font-family:var(--mono);font-size:11.5px;letter-spacing:.09em;
  color:var(--ink-4);margin:14px 0 3px}}
.dir h3{{font-size:19px;margin:0 0 9px;line-height:1.3}}
/* The min-height is what makes the verdict rules land on one line across the grid. Bottom-
   aligning them instead lets a two-line reason shove one card's rule up, and a row of
   hairlines at four different heights reads as a broken table rather than a spread. Five
   lines fits the two-or-three-line pitch `/explore` asks for; a longer one grows the card
   rather than being clipped, because losing a direction's last sentence to make the grid
   tidy is the wrong trade. */
.dir .pitch{{font-size:14.5px;line-height:1.62;color:var(--ink-2);margin:0 0 14px;
  min-height:calc(5 * 1.62 * 14.5px)}}
.dir .pitch p{{margin:0 0 .5em}}
.dir .pitch p:last-child{{margin-bottom:0}}

.dir .verdict{{padding-top:11px;border-top:1px solid var(--rule-soft);
  font-size:13.5px;line-height:1.55;color:var(--ink-3)}}
.dir .v{{font-size:10px;font-weight:600;letter-spacing:.13em;text-transform:uppercase;
  display:block;margin-bottom:4px}}
.dir.live .v{{color:var(--ink)}}
.dir.rejected .v{{color:var(--red)}}
.dir.undecided .v{{color:var(--ochre)}}

.top .brief{{font-size:18.5px;color:var(--ink-2);margin:14px 0 0;max-width:64ch}}
.facts .seed{{font-family:var(--mono);font-size:12px;color:var(--ink-3);word-break:break-all}}
.went{{border-top:1px solid var(--rule);padding-top:24px;font-size:15.5px;color:var(--ink-2)}}
.went.open p{{color:var(--ink-3)}}
"""


def specimen_frame(d: dict) -> str:
    """A specimen in a sandboxed iframe: its palette is its own, and its CSS cannot escape."""
    if not d["specimen"]:
        return '<div class="frame empty"><span>no specimen</span></div>'
    doc = (f'<!doctype html><meta charset="utf-8">{FONT_LINK}'
           '<style>html,body{margin:0;height:100%;font-family:"Inter",system-ui,sans-serif}'
           '</style>' + d["specimen"])
    return ('<div class="frame"><iframe sandbox loading="lazy" '
            f'title="{html.escape(d["name"])} — specimen" '
            f'srcdoc="{html.escape(doc, quote=True)}"></iframe></div>')


def build(ex: dict, g: dict) -> str:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    live = sum(1 for d in ex["directions"] if d["verdict"] == "live")
    rej = sum(1 for d in ex["directions"] if d["verdict"] == "rejected")
    open_ = len(ex["directions"]) - live - rej

    facts = [f'<div class="fact"><b>directions</b>{len(ex["directions"])}</div>',
             f'<div class="fact"><b>live</b>{live}</div>',
             f'<div class="fact"><b>rejected</b>{rej}</div>']
    if open_:
        facts.append(f'<div class="fact"><b>no verdict</b>{open_}</div>')
    if ex["tags"]:
        facts.append('<div class="fact"><b>tags</b>'
                     + html.escape(", ".join(ex["tags"])) + "</div>")
    if ex["seed"]:
        facts.append('<div class="fact"><b>seed</b>'
                     f'<span class="seed">{html.escape(ex["seed"])}</span></div>')

    cards = []
    for d in ex["directions"]:
        state = d["verdict"] or "undecided"
        label = {"live": "live", "rejected": "rejected"}.get(d["verdict"], "no verdict yet")
        reason = html.escape(d["reason"]) if d["reason"] else ""
        cards.append(f"""<div class="dir {state}">
{specimen_frame(d)}
  <div class="letter">{html.escape(d["letter"])}</div>
  <h3>{html.escape(d["name"])}</h3>
  <div class="pitch">{render_md(d["pitch"], g) if d["pitch"] else ""}</div>
  <div class="verdict"><span class="v">{label}</span>{reason}</div>
</div>""")

    went = ex["went"] or ("Nothing picked yet. Picking one produces exactly one numbered "
                          "decision that links back to this file — until it exists, nothing "
                          "in the brain may treat a direction as chosen.")
    went_cls = "went" if ex["went"] else "went open"

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(ex["title"])} — {html.escape(PROJECT_NAME)}</title>
{FONT_LINK}<style>{CSS}{PAGE_CSS}</style></head><body>
<div class="wrap">
<div class="top">
  <div class="kicker">{html.escape(PROJECT_NAME)}{project_kicker(ex)} · exploration</div>
  <h1>{html.escape(ex["title"])}</h1>
  {f'<p class="brief">{html.escape(ex["brief"])}</p>' if ex["brief"] else ""}
  <div class="meta">generated {stamp} from
    <code>{ex["path"].relative_to(ROOT)}</code> — regenerate with
    <code>python3 brain/spread.py</code></div>
</div>

<div class="facts">{"".join(facts)}</div>

<div class="spread">{"".join(cards)}</div>

<div class="{went_cls}">{render_md(went, g)}</div>
</div></body></html>"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("files", nargs="*", help="explorations to render (default: all)")
    ap.add_argument("--open", action="store_true")
    args = ap.parse_args()

    paths = ([Path(f).resolve() for f in args.files] if args.files
             else sorted(p for p in DIR.glob("*.md") if p.name != "README.md"))
    if not paths:
        print("no explorations yet — /explore writes the first one")
        return 0

    g = glossary()
    written = []
    for p in paths:
        ex = parse(p)
        out = p.with_suffix(".html")
        out.write_text(build(ex, g), encoding="utf-8")
        missing = sum(1 for d in ex["directions"] if not d["specimen"])
        note = f", {missing} without a specimen" if missing else ""
        print(f"{out.relative_to(ROOT)}  ·  {len(ex['directions'])} direction(s){note}")
        written.append(out)

    if args.open:
        subprocess.run(["open", *[str(w) for w in written]], check=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
