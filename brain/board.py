#!/usr/bin/env python3
"""board.py — render `brain/moodboards/*.md` as a canvas you can read at a glance.

    python3 brain/board.py [file ...] [--open]

`/moodboard` produces ideas grouped into narratives. As markdown that is an outline, and an
outline is the one shape a moodboard must not have: the whole argument is that these ideas sit
next to each other and add up to something. This lays them out as a desk — the material
pinned up, the sell line big enough to read across the room, the reasoning folded underneath,
and the connections between ideas live.

**The markdown file stays the truth.** This writes a projection next to it and is never read
back — same contract as `feed.py` and `spread.py`. Delete the HTML and nothing is lost.

Plates are files that already exist in the workspace, referenced by path from the repo root
and linked relatively so the page works from disk. A path that does not resolve renders as a
visible gap rather than a broken image with a caption: an idea whose evidence is missing
should look missing, because the alternative is a board that reads as grounded when it is not.

House style comes from `feed.py` — one stylesheet for the whole workspace, never a second copy.
"""

from __future__ import annotations

import argparse
import html
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BRAIN = Path(__file__).resolve().parent
ROOT = BRAIN.parent
DIR = BRAIN / "moodboards"

sys.path.insert(0, str(BRAIN))
from config import PROJECT_NAME, MULTI_PROJECT, PROJECT_LABEL  # noqa: E402
from feed import (  # noqa: E402
    CSS, FONT_LINK, cite_list_html, cite_reset, glossary, render_md,
)

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif", ".svg"}


# ---------------------------------------------------------------------------------------------
# Reading a board
# ---------------------------------------------------------------------------------------------

def slug(title: str) -> str:
    out = "".join(c.lower() if c.isalnum() else "-" for c in title).strip("-")
    while "--" in out:
        out = out.replace("--", "-")
    return out or "idea"


def tilt(key: str) -> float:
    """A plate's angle on the desk — small, and the same every render.

    Random rotation would make every regeneration a diff, and a board whose pins move when
    nothing changed is one nobody trusts. Hashing the path keeps it deterministic. The range
    is deliberately tiny: this is paper resting on a table, not a scrapbook.
    """
    h = sum((i + 1) * ord(c) for i, c in enumerate(key))
    return round(((h % 29) - 14) / 10.0, 2)


def parse(path: Path) -> dict:
    """One board file → the shape `brain/moodboards/README.md` specifies.

    Tolerant on purpose: a half-written board should still render, because seeing the two
    narratives that exist is how you notice the third one never got written.
    """
    text = path.read_text(encoding="utf-8")

    body = text
    tags: list[str] = []
    project = ""
    fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if fm:
        body = text[fm.end():]
        t = re.search(r"^tags:\s*\[(.*?)\]", fm.group(1), re.M)
        if t:
            tags = [x.strip().strip("\"'") for x in t.group(1).split(",") if x.strip()]
        p = re.search(r"^project:\s*(\S+)\s*$", fm.group(1), re.M)
        if p:
            project = p.group(1).strip()

    head = re.search(r"^#\s+(.+)$", body, re.M)
    title = head.group(1).strip() if head else path.stem
    vision = re.search(r"^Vision:\s*(.+?)(?=\n\s*\n|\n##\s)", body, re.M | re.S)

    narratives = []
    for chunk in re.split(r"^##\s+", body, flags=re.M)[1:]:
        line, _, rest = chunk.partition("\n")
        name = re.sub(r"^Narrative\s*[—–-]\s*", "", line.strip(), flags=re.I).strip()

        pieces = re.split(r"^###\s+", rest, flags=re.M)
        story = re.sub(r"^\s+|\s+$", "", pieces[0])
        ideas = [_idea(c) for c in pieces[1:]]
        narratives.append({"name": name, "story": story, "ideas": ideas})

    # Ideas that live outside any narrative are a real state mid-run: material arrived before
    # the story did. They get their own band rather than being dropped on the floor.
    loose = re.split(r"^###\s+", re.split(r"^##\s+", body, flags=re.M)[0], flags=re.M)[1:]
    if loose:
        narratives.insert(0, {"name": "", "story": "", "ideas": [_idea(c) for c in loose]})

    return {"path": path, "title": title, "tags": tags, "project": project,
            "vision": (vision.group(1).strip() if vision else ""),
            "narratives": narratives}


def _idea(chunk: str) -> dict:
    line, _, rest = chunk.partition("\n")
    name = line.strip()

    plates = []
    for m in re.finditer(r"^Plate:\s*(\S+)\s*(?:[—–-]\s*(.*))?$", rest, re.M):
        plates.append({"kind": "image", "src": m.group(1).strip(),
                       "caption": (m.group(2) or "").strip()})
    for m in re.finditer(r'^Quote:\s*"(.+?)"\s*(.*)$', rest, re.M):
        plates.append({"kind": "quote", "text": m.group(1).strip(),
                       "attr": m.group(2).strip()})

    conn = re.search(r"^Connects:\s*(.+)$", rest, re.M)
    size = re.search(r"^Size:\s*(\w+)\s*$", rest, re.M)
    cut = re.search(r"^Cut:\s*(.*)$", rest, re.M)

    detail = re.sub(r"^(?:Plate|Quote|Connects|Size|Cut):.*$", "", rest, flags=re.M)
    # The sell line is the first paragraph; everything after it is the detail underneath.
    detail = detail.strip()
    sell, _, under = detail.partition("\n\n")
    # A heading inside an idea would fight the page's hierarchy. The detail is prose.
    under = re.sub(r"^#{1,6}\s+", "", under, flags=re.M).strip()

    return {
        "title": name, "id": slug(name),
        "sell": sell.strip(), "detail": under,
        "plates": plates,
        "connects": [c.strip() for c in conn.group(1).split(",") if c.strip()] if conn else [],
        "size": (size.group(1).lower() if size else ""),
        "cut": cut.group(1).strip() if cut else None,
        "is_cut": bool(cut),
    }


# ---------------------------------------------------------------------------------------------
# The page
# ---------------------------------------------------------------------------------------------

PAGE_CSS = """
/* Wider than the feed, like the exploration spread: ideas have to sit beside each other or
   the page has turned back into the outline it exists to not be. */
.wrap{max-width:1480px}

.top .vision{font-size:clamp(20px,2.1vw,25px);line-height:1.5;letter-spacing:-.012em;
  color:var(--ink);margin:20px 0 0;max-width:46ch;text-wrap:pretty}

/* ── narratives: a band of paper, titled in the margin ───────────────── */
.band{border-top:1px solid var(--rule);padding-top:26px;margin:0 0 76px}
.band .num{font-family:var(--mono);font-size:11.5px;letter-spacing:.09em;color:var(--ink-4)}
.band h2{font-size:29px;line-height:1.16;letter-spacing:-.026em;margin:6px 0 0;
  max-width:22ch}
.band .story{font-size:17px;line-height:1.6;color:var(--ink-2);margin:10px 0 0;max-width:58ch}
.band .head{display:grid;grid-template-columns:minmax(240px,1fr) 2fr;gap:10px 48px;
  align-items:end;margin-bottom:34px}
@media (max-width:860px){.band .head{grid-template-columns:1fr}}

/* Columns, not a grid. A grid row is as tall as its tallest card, so a board of unequal
   ideas gets holes in it — and a hole reads as a missing idea rather than as a short one.
   Columns pack, the way things pack on a desk: the bottom edge is ragged and nothing is
   padded out to meet a neighbour. `break-inside` is what keeps an idea whole. */
.ideas{columns:3;column-gap:38px}
@media (max-width:1180px){.ideas{columns:2}}
@media (max-width:720px){.ideas{columns:1}}
.idea{break-inside:avoid;-webkit-column-break-inside:avoid;page-break-inside:avoid;
  margin:0 0 50px;scroll-margin-top:24px}
/* One idea may take the whole width — the board's centre of gravity, where there is one.
   `Size: full` is the author saying so; nothing derives it. */
.idea.full{column-span:all;margin-bottom:56px}
.idea.full .plates{align-items:flex-start}
.idea.full .sell{max-width:52ch;font-size:20px}

/* ── plates: the material, resting on the table ──────────────────────── */
.plates{display:flex;flex-wrap:wrap;align-items:flex-end;gap:14px;margin:0 0 20px}
.plate{position:relative;max-width:100%}
.plate img{display:block;max-width:100%;max-height:265px;background:var(--wash);
  border:1px solid var(--rule-soft);
  box-shadow:0 1px 2px rgba(13,13,14,.05),0 8px 22px -14px rgba(13,13,14,.35)}
/* The second plate onward tucks under the first a little, the way paper does. */
.plates .plate + .plate{margin-left:-20px}
@media (max-width:640px){.plates .plate + .plate{margin-left:0}}
.plate .cap{font-size:12.5px;line-height:1.45;color:var(--ink-3);margin:8px 2px 0;
  max-width:30ch}
.plate.gone{padding:26px 18px;border:1px dashed var(--rule);background:var(--wash);
  min-width:200px}
.plate.gone .path{font-family:var(--mono);font-size:11px;color:var(--ochre);
  word-break:break-all}

/* A quote is material too — it came off the same desk, so it sits on the board and not in
   the prose. Big enough to be read before the paragraph under it. */
.plate.quote{flex:1 1 220px;max-width:100%;padding:20px 22px 18px;background:var(--wash);
  border-left:2px solid var(--ink)}
.plate.quote p{font-size:18px;line-height:1.42;letter-spacing:-.015em;margin:0;
  text-wrap:pretty;max-width:26ch}
.plate.quote .attr{font-size:12px;color:var(--ink-3);margin-top:10px;display:block}

/* ── the idea itself ─────────────────────────────────────────────────── */
.idea h3{font-size:21px;line-height:1.24;letter-spacing:-.021em;margin:0 0 7px}
.idea .sell{font-size:17.5px;line-height:1.52;color:var(--ink-2);margin:0 0 14px;
  max-width:44ch;text-wrap:pretty}
.idea .sell p{margin:0}

.idea .conn{font-size:12.5px;line-height:1.6;color:var(--ink-4);margin:0 0 10px}
.idea .conn a{color:var(--blue);text-decoration:none;
  border-bottom:1px solid var(--blue-wash)}
.idea .conn a:hover{border-bottom-color:var(--blue)}
.idea .conn b{font-weight:600;letter-spacing:.11em;text-transform:uppercase;font-size:10px;
  color:var(--ink-4);margin-right:7px}

/* The reasoning is present and out of the way. An idea that only works once you have read
   three paragraphs is an idea that failed its own one-line test. */
.idea details{border-top:1px solid var(--rule-soft);padding-top:11px}
.idea summary{list-style:none;cursor:pointer;font-size:10.5px;font-weight:600;
  letter-spacing:.13em;text-transform:uppercase;color:var(--ink-3)}
.idea summary::-webkit-details-marker{display:none}
.idea summary::after{content:" +";font-family:var(--mono);letter-spacing:0}
.idea details[open] summary::after{content:" –"}
.idea summary:hover{color:var(--ink)}
.idea .body{font-size:15px;line-height:1.66;color:var(--ink-2);margin-top:12px}
.idea .body p{margin:0 0 .75em;max-width:52ch}
.idea .body p:last-child{margin-bottom:0}

/* A cut idea stays where it was — the reason for keeping the file. It recedes through the
   words around it, not by fading the material: a greyed plate cannot be re-judged later,
   and "why did we cut that" is a question asked of the picture. */
.idea.cut h3,.idea.cut .sell,.idea.cut .conn{opacity:.5}
.idea.cut .plates{opacity:.72;transition:opacity .18s}
.idea.cut:hover .plates{opacity:1}
.idea .cutline{font-size:13px;line-height:1.55;color:var(--ink-3);
  border-top:1px solid var(--rule-soft);padding-top:11px}
.idea .cutline b{font-size:10px;font-weight:600;letter-spacing:.13em;text-transform:uppercase;
  color:var(--red);display:block;margin-bottom:4px}

/* Connection highlight. Without JS the links still jump, which is the whole behaviour that
   matters; this only shows the shape of the story while the cursor is on one idea. */
.sources{margin-bottom:0}
.sources .srclist{margin-top:14px}

.idea.lit{outline:1px solid var(--ink);outline-offset:14px}
.idea.flash{animation:flash 1.1s ease-out}
@keyframes flash{from{outline:1px solid var(--ink);outline-offset:6px}
  to{outline:1px solid transparent;outline-offset:18px}}
"""

JS = """
(function(){
  var ideas = [].slice.call(document.querySelectorAll('.idea'));
  ideas.forEach(function(el){
    var ids = (el.dataset.connects || '').split(' ').filter(Boolean);
    if (!ids.length) return;
    el.addEventListener('mouseenter', function(){
      ids.forEach(function(id){
        var t = document.getElementById(id);
        if (t) t.classList.add('lit');
      });
    });
    el.addEventListener('mouseleave', function(){
      ideas.forEach(function(o){ o.classList.remove('lit'); });
    });
  });
  window.addEventListener('hashchange', function(){
    var t = document.querySelector(location.hash ? location.hash : null);
    if (!t) return;
    t.classList.remove('flash');
    void t.offsetWidth;
    t.classList.add('flash');
  });
})();
"""


def project_kicker(bd: dict) -> str:
    """` · Client Portal`, or nothing at all in a one-project workspace."""
    key = bd.get("project", "")
    if not MULTI_PROJECT or not key or key == "all":
        return ""
    return " · " + html.escape(PROJECT_LABEL.get(key, key))


def _inline_html(text: str, g: dict) -> str:
    """One line of markdown as inline HTML — the shared renderer with its block wrapper off."""
    out = render_md(text, g).strip()
    return re.sub(r"^<p>|</p>$", "", out).strip()


def plate_html(p: dict, out_dir: Path, g: dict) -> str:
    if p["kind"] == "quote":
        # A quote's attribution stays visible rather than collapsing to a footnote numeral.
        # The house rule is that evidence is quiet, and it is the right rule for a claim
        # inside a paragraph — but here the claim *is* the quote, and who said it is half of
        # what makes it worth pinning up. So the `^[...]` wrapper comes off and the words stay.
        raw = re.sub(r"^\^\[(.*?)\](?:\([^)]*\))?$", r"\1", p["attr"].strip())
        attr = f'<span class="attr">{_inline_html(raw, g)}</span>' if raw else ""
        return (f'<figure class="plate quote"><p>“{html.escape(p["text"])}”</p>'
                f"{attr}</figure>")

    src = p["src"]
    target = (ROOT / src).resolve()
    if not target.exists() or target.suffix.lower() not in IMAGE_SUFFIXES:
        why = "not found" if not target.exists() else "not an image"
        return ('<figure class="plate gone"><div class="path">'
                f'{html.escape(src)}</div>'
                f'<figcaption class="cap">{why} — the board claims evidence it does not '
                f'have</figcaption></figure>')
    # Relative, so the page works opened straight off disk with no server.
    href = os.path.relpath(target, out_dir.resolve())
    cap = (f'<figcaption class="cap">{html.escape(p["caption"])}</figcaption>'
           if p["caption"] else "")
    return (f'<figure class="plate" style="transform:rotate({tilt(src)}deg)">'
            f'<img src="{html.escape(href, quote=True)}" alt="" loading="lazy">'
            f"{cap}</figure>")


def idea_html(idea: dict, index: dict, out_dir: Path, g: dict) -> str:
    size = idea["size"] if idea["size"] in ("full",) else ""
    classes = " ".join(x for x in ("idea", size, "cut" if idea["is_cut"] else "") if x)

    conns, ids = [], []
    for name in idea["connects"]:
        target = index.get(slug(name))
        if target:
            ids.append(target)
            conns.append(f'<a href="#{target}">{html.escape(name)}</a>')
        else:
            conns.append(f'<span title="no idea on this board by that name">'
                         f"{html.escape(name)}</span>")
    conn_html = (f'<div class="conn"><b>connects</b>{" · ".join(conns)}</div>'
                 if conns else "")

    plates = ("".join(plate_html(p, out_dir, g) for p in idea["plates"]))
    detail = (f'<details><summary>how it comes together</summary>'
              f'<div class="body">{render_md(idea["detail"], g)}</div></details>'
              if idea["detail"] else "")
    cutline = (f'<div class="cutline"><b>cut</b>{html.escape(idea["cut"])}</div>'
               if idea["is_cut"] else "")

    return f"""<div class="{classes}" id="{idea['id']}" data-connects="{' '.join(ids)}">
  {f'<div class="plates">{plates}</div>' if plates else ''}
  <h3>{html.escape(idea["title"])}</h3>
  <div class="sell">{render_md(idea["sell"], g) if idea["sell"] else ""}</div>
  {conn_html}
  {cutline}
  {detail}
</div>"""


def build(bd: dict, g: dict) -> str:
    cite_reset()                      # numbering is per page, and this page is built once
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    out_dir = bd["path"].parent
    ideas = [i for n in bd["narratives"] for i in n["ideas"]]
    index = {i["id"]: i["id"] for i in ideas}
    live = sum(1 for i in ideas if not i["is_cut"])
    plates = sum(len(i["plates"]) for i in ideas)
    linked = sum(1 for i in ideas if i["connects"])

    facts = [f'<div class="fact"><b>ideas</b>{live}</div>',
             f'<div class="fact"><b>narratives</b>'
             f'{sum(1 for n in bd["narratives"] if n["name"])}</div>',
             f'<div class="fact"><b>plates</b>{plates}</div>',
             f'<div class="fact"><b>connected</b>{linked} of {len(ideas)}</div>']
    if len(ideas) - live:
        facts.append(f'<div class="fact"><b>cut</b>{len(ideas) - live}</div>')
    if bd["tags"]:
        facts.append('<div class="fact"><b>tags</b>'
                     + html.escape(", ".join(bd["tags"])) + "</div>")

    bands = []
    for n, nar in enumerate(bd["narratives"], 1):
        head = ""
        if nar["name"]:
            head = (f'<div class="head"><div><div class="num">'
                    f'narrative {n:02d}</div><h2>{html.escape(nar["name"])}</h2></div>'
                    f'<div class="story">{render_md(nar["story"], g)}</div></div>')
        cards = "".join(idea_html(i, index, out_dir, g) for i in nar["ideas"])
        bands.append(f'<section class="band">{head}<div class="ideas">{cards}</div></section>')

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(bd["title"])} — {html.escape(PROJECT_NAME)}</title>
{FONT_LINK}<style>{CSS}{PAGE_CSS}</style></head><body>
<div class="wrap">
<div class="top">
  <div class="kicker">{html.escape(PROJECT_NAME)}{project_kicker(bd)} · moodboard</div>
  <h1>{html.escape(bd["title"])}</h1>
  {f'<p class="vision">{html.escape(bd["vision"])}</p>' if bd["vision"] else ""}
  <div class="meta">generated {stamp} from
    <code>{bd["path"].relative_to(ROOT)}</code> — regenerate with
    <code>python3 brain/board.py</code>. Nothing here is decided: picking a direction is
    <code>/explore</code>, and choosing one is a decision that links back to this file.</div>
</div>

<div class="facts">{"".join(facts)}</div>

{"".join(bands)}
{sources_html()}
</div><script>{JS}</script></body></html>"""


def sources_html() -> str:
    """Where the `^[who · where · when]` tags land. A board argues from material somebody
    else produced, so the list of who said what is the part that makes it checkable."""
    srcs = cite_list_html()
    if not srcs:
        return ""
    return f'<section class="band sources"><div class="num">sources</div>{srcs}</section>'


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("files", nargs="*", help="boards to render (default: all)")
    ap.add_argument("--open", action="store_true")
    args = ap.parse_args()

    paths = ([Path(f).resolve() for f in args.files] if args.files
             else sorted(p for p in DIR.glob("*.md") if p.name != "README.md"))
    if not paths:
        print("no moodboards yet — /moodboard writes the first one")
        return 0

    g = glossary()
    written = []
    for p in paths:
        bd = parse(p)
        out = p.with_suffix(".html")
        out.write_text(build(bd, g), encoding="utf-8")
        ideas = [i for n in bd["narratives"] for i in n["ideas"]]
        missing = sum(1 for i in ideas
                      for pl in i["plates"]
                      if pl["kind"] == "image" and not (ROOT / pl["src"]).exists())
        note = f", {missing} plate(s) missing" if missing else ""
        print(f"{out.relative_to(ROOT)}  ·  {len(ideas)} idea(s){note}")
        written.append(out)

    if args.open:
        subprocess.run(["open", *[str(w) for w in written]], check=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
