#!/usr/bin/env python3
"""board.py — render `brain/moodboards/*.md` as a desk you can move around on.

    python3 brain/board.py [file ...] [--open]

A moodboard has two layers and the interesting thing is between them. **Ideas** are the atoms:
one title, one sentence, enough to sell it. **Visions** assemble ideas into a whole brand, and
the same idea appears in several of them. Which ideas build which vision is the argument, and
on a page that argument is invisible — so this draws it, as wires between the two.

The output is a pannable, zoomable canvas rather than a document, because the shape of the
thing is spatial: columns of ideas across the top, visions along the bottom, the connections
running between. Hover either end and the wires light. Open anything for the detail, the
evidence, and a place to write a reaction.

**The markdown file stays the truth.** This writes a projection next to it and is never read
back — same contract as `feed.py` and `spread.py`. Delete the HTML and nothing is lost.

Layout is computed in the browser, not here, because every card's height depends on the text
in it. Python parses the record and emits the data; the runtime measures and places.

Plates are files that already exist in the workspace, linked relatively so the page works
opened straight off disk. A path that does not resolve renders as a visible gap: an idea whose
evidence is missing should look missing, because the alternative is a desk that reads as
grounded when it is not.
"""

from __future__ import annotations

import argparse
import html
import json
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
from feed import FONT_LINK  # noqa: E402

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif", ".svg"}
FACT_KINDS = ("Fixed", "Decided", "Rule", "Open")


# ---------------------------------------------------------------------------------------------
# Reading a desk
# ---------------------------------------------------------------------------------------------

def slug(title: str) -> str:
    out = "".join(c.lower() if c.isalnum() else "-" for c in title).strip("-")
    while "--" in out:
        out = out.replace("--", "-")
    return out or "x"


def sections(body: str) -> dict:
    """`## Name` → its text. A desk is written in named sections and read the same way."""
    out, name, buf = {}, None, []
    for line in body.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            if name:
                out[name.lower()] = "\n".join(buf).strip()
            name, buf = m.group(1), []
        elif name:
            buf.append(line)
    if name:
        out[name.lower()] = "\n".join(buf).strip()
    return out


def plates(text: str, out_dir: Path) -> list:
    """`Plate: <path> — <what to take from it> — <url>`, resolved against this file's folder."""
    found = []
    for m in re.finditer(r"^Plate:\s*(.+)$", text, re.M):
        parts = [p.strip() for p in re.split(r"\s+[—–]\s+", m.group(1).strip())]
        src = parts[0]
        cap = parts[1] if len(parts) > 1 else ""
        url = parts[2] if len(parts) > 2 else ""
        if cap.startswith("http"):
            cap, url = "", cap
        target = (ROOT / src).resolve()
        ok = target.exists() and target.suffix.lower() in IMAGE_SUFFIXES
        found.append({
            "src": (os.path.relpath(target, out_dir.resolve()) if ok else src),
            "cap": cap, "url": url, "missing": not ok,
        })
    return found


def _lines(text: str, key: str) -> list:
    return [m.group(1).strip()
            for m in re.finditer(rf"^{key}:\s*(.+)$", text, re.M)]


def _one(text: str, key: str, default: str = "") -> str:
    got = _lines(text, key)
    return got[0] if got else default


def parse(path: Path) -> dict:
    """One desk file → the shape `brain/moodboards/README.md` specifies.

    Tolerant on purpose: a half-written desk should still render, because seeing the ideas
    that exist with no vision under them is how you notice the assembling never happened.
    """
    text = path.read_text(encoding="utf-8")
    out_dir = path.parent

    body, tags, project = text, [], ""
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
    subtitle = _one(body.split("\n##", 1)[0], "Subtitle")

    sec = sections(body)

    # ── the lenses: the columns ideas are filed under, and the rows a vision answers ──
    lenses = []
    for line in sec.get("lenses", "").splitlines():
        m = re.match(r"^-\s+(.+?)\s+[—–]\s+(.+)$", line.strip())
        if m:
            lenses.append({"id": slug(m.group(1)), "name": m.group(1).strip(),
                           "what": m.group(2).strip()})
        elif line.strip().startswith("- "):
            name = line.strip()[2:].strip()
            lenses.append({"id": slug(name), "name": name, "what": ""})
    lens_by_name = {ln["name"].lower(): ln["id"] for ln in lenses}

    def lens_rows(block: str) -> dict:
        """`<Lens name>: <what this does to that lens>` — only declared lenses count, so a
        stray `Thesis:` or `Plate:` line is never mistaken for one."""
        rows = {}
        for m in re.finditer(r"^([A-Za-z][A-Za-z ’'-]*?):\s*(.+)$", block, re.M):
            lid = lens_by_name.get(m.group(1).strip().lower())
            if lid:
                rows[lid] = m.group(2).strip()
        return rows

    def strip_fields(block: str) -> str:
        known = "|".join(["Lens", "Visions", "Line", "Mark", "Thesis", "Tension", "Asks",
                          "Plate", "Subtitle"]
                         + [re.escape(ln["name"]) for ln in lenses])
        out = re.sub(rf"^(?:{known}):.*$", "", block, flags=re.M)
        out = re.sub(r"```specimen\s*\n.*?```", "", out, flags=re.S)
        return re.sub(r"\n{3,}", "\n\n", out).strip()

    # ── the brief: prose, then the constraints everything on the desk has to survive ──
    brief_raw = sec.get("brief", "")
    facts = []
    for kind in FACT_KINDS:
        for line in _lines(brief_raw, kind):
            src = re.search(r"\^\[(.*?)\](?:\([^)]*\))?\s*$", line)
            facts.append({"kind": kind,
                          "text": re.sub(r"\s*\^\[.*?\](?:\([^)]*\))?\s*$", "", line).strip(),
                          "who": (src.group(1).strip() if src else "")})
    brief_prose = re.sub(rf"^(?:{'|'.join(FACT_KINDS)}):.*$", "", brief_raw, flags=re.M)
    brief_prose = [p.strip() for p in re.split(r"\n\s*\n", brief_prose) if p.strip()]

    # ── what is still open, and who closes it ──
    openq = []
    for line in sec.get("open", "").splitlines():
        m = re.match(r"^-\s+(.+?)\s+[—–]\s+(.+?)(?:\s+[—–]\s+(.+))?$", line.strip())
        if m:
            openq.append({"what": m.group(1).strip(), "text": m.group(2).strip(),
                          "who": (m.group(3) or "").strip()})

    # ── the ideas ──
    ideas = []
    for chunk in re.split(r"^###\s+", sec.get("ideas", ""), flags=re.M)[1:]:
        name, _, rest = chunk.partition("\n")
        name = name.strip()
        ideas.append({
            "id": slug(name), "title": name,
            "lens": lens_by_name.get(_one(rest, "Lens").lower(), ""),
            "visions": [slug(v) for v in
                        (x.strip() for x in _one(rest, "Visions").split(",")) if v],
            "line": _one(rest, "Line"),
            "lenses": lens_rows(rest),
            "plates": plates(rest, out_dir),
            "how": strip_fields(rest),
        })

    # ── the visions ──
    visions = []
    for chunk in re.split(r"^###\s+", sec.get("visions", ""), flags=re.M)[1:]:
        name, _, rest = chunk.partition("\n")
        name = name.strip()
        spec = re.search(r"```specimen\s*\n(.*?)```", rest, re.S)
        visions.append({
            "id": slug(name), "name": name,
            "mark": _one(rest, "Mark", name[:1].upper()),
            "thesis": _one(rest, "Thesis"),
            "lenses": lens_rows(rest),
            "tension": _one(rest, "Tension"),
            "asks": _one(rest, "Asks"),
            "plates": plates(rest, out_dir),
            "specimen": spec.group(1).strip() if spec else "",
            "story": strip_fields(rest),
        })

    # An idea declares which visions it is part of; a vision's list of ideas is derived from
    # that, so the membership is written once and cannot disagree with itself.
    vids = [v["id"] for v in visions]
    for idea in ideas:
        idea["visions"] = [v for v in idea["visions"] if v in vids]
        # A constant is an idea every vision shares. It is the brand whichever way the work
        # goes, which makes it derived rather than authored — claiming it by hand is how a
        # board ends up with a constant that one vision quietly dropped.
        idea["constant"] = bool(vids) and len(idea["visions"]) == len(vids)
    for v in visions:
        v["ideas"] = [i["id"] for i in ideas if v["id"] in i["visions"]]

    return {"path": path, "title": title, "subtitle": subtitle, "tags": tags,
            "project": project, "lenses": lenses, "facts": facts, "brief": brief_prose,
            "open": openq, "ideas": ideas, "visions": visions}


# ---------------------------------------------------------------------------------------------
# The page
# ---------------------------------------------------------------------------------------------

CSS = """
:root{
  --desk:#f4f4f2; --paper:#ffffff; --ink:#0d0d0e; --ink-2:#333336; --muted:#6b6b70;
  --faint:#a3a3a8; --rule:#e2e2df; --wash:#fbfbf9; --blue:#12408f; --red:#a52218;
  --sans:"Inter","Inter var",-apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
}
*,*::before,*::after{box-sizing:border-box}
html,body{height:100%;margin:0}
body{background:var(--desk);color:var(--ink);overflow:hidden;
  font:400 15px/1.5 var(--sans);-webkit-font-smoothing:antialiased;
  -moz-osx-font-smoothing:grayscale;font-feature-settings:"kern" 1,"liga" 1,"calt" 1}
button{font:inherit;color:inherit}
a{color:var(--blue);text-decoration:none}
a:hover{text-decoration:underline}
:focus-visible{outline:2px solid var(--blue);outline-offset:2px}

/* ── the bar: where you are, and the way to everywhere else ─────────── */
.bar{position:fixed;top:0;left:0;right:0;height:52px;z-index:40;display:flex;
  align-items:center;gap:14px;padding:0 18px;background:rgba(255,255,255,.93);
  backdrop-filter:blur(6px);border-bottom:1px solid var(--rule)}
.bar .title{font-weight:600;letter-spacing:-.012em;white-space:nowrap}
.bar .sub{color:var(--muted);font-size:13.5px;white-space:nowrap;overflow:hidden;
  text-overflow:ellipsis}
.bar .idx{display:flex;gap:2px;margin-left:auto}
.bar .idx button,.bar .zoom button{appearance:none;background:none;border:0;padding:7px 10px;
  border-radius:3px;cursor:pointer;color:var(--muted);font-size:13.5px;white-space:nowrap}
.bar .idx button:hover,.bar .zoom button:hover{background:#f0f0ee;color:var(--ink)}
.bar .idx button.on{color:var(--ink);font-weight:600}
.bar .zoom{display:flex;gap:2px;border-left:1px solid var(--rule);padding-left:10px}
.bar .zoom .pct{color:var(--muted);font-size:13px;min-width:44px;text-align:center;
  align-self:center;font-variant-numeric:tabular-nums}

/* ── the desk itself ─────────────────────────────────────────────────── */
.desk{position:fixed;inset:52px 0 0 0;overflow:hidden;cursor:grab;touch-action:none}
.desk.dragging{cursor:grabbing}
.canvas{position:absolute;left:0;top:0;transform-origin:0 0;will-change:transform}
.canvas.anim{transition:transform .55s cubic-bezier(.2,.7,.2,1)}
.wires{position:absolute;left:0;top:0;pointer-events:none;z-index:0}
.card,.lenshead{z-index:1}
.wires path{fill:none;stroke:#d6d6d2;stroke-width:1.5;transition:stroke .15s,opacity .15s}
.wires path.on{stroke:var(--ink)}
.wires.focus path:not(.on){opacity:.12}

.card{position:absolute;background:var(--paper);border:1px solid var(--rule);
  border-radius:2px;transition:opacity .15s,border-color .15s}
.canvas.focus .card:not(.on){opacity:.3}
.card.on{border-color:var(--ink)}

.brief{padding:34px 36px 30px}
.brief h1{font:600 33px/1.12 var(--sans);letter-spacing:-.028em;margin:0 0 14px;max-width:17ch}
.brief p{margin:0 0 14px;max-width:62ch;color:var(--ink-2)}
.brief .facts{margin:22px 0 0;border-top:1px solid var(--rule)}
.brief .fact{display:grid;grid-template-columns:132px 1fr;gap:16px;padding:11px 0;
  border-bottom:1px solid var(--rule);font-size:14px}
.brief .fact b{font-weight:600}
.brief .fact span{color:var(--ink-2)}
.brief .fact small{display:block;color:var(--faint);font-size:12px;margin-top:2px}
.brief .howto{margin:22px 0 0;color:var(--muted);font-size:13.5px;max-width:60ch}

/* ── ideas, in a column per lens ─────────────────────────────────────── */
.lenshead{position:absolute}
.lenshead h2{font:600 18px/1.2 var(--sans);letter-spacing:-.012em;margin:0 0 4px}
.lenshead p{margin:0;color:var(--muted);font-size:13.5px;line-height:1.45}
.idea{padding:16px 18px 14px;cursor:pointer;display:flex;flex-direction:column;gap:6px}
.idea:hover{border-color:#bdbdb8}
.idea h3{font:600 17px/1.25 var(--sans);letter-spacing:-.014em;margin:0}
.idea p{margin:0;font-size:14px;line-height:1.45;color:var(--ink-2)}
.idea .foot{display:flex;align-items:center;gap:6px;margin-top:2px;min-height:14px}
.idea .foot i{display:block;width:9px;height:9px;border-radius:50%;background:var(--ink)}
.idea .foot em{font-style:normal;color:var(--faint);font-size:12px;margin-left:auto}
/* An idea every vision shares is the brand whichever way this goes. It is stated, not
   drawn louder: the desk's job is to show what differs. */
.idea.constant{background:var(--wash)}
.idea.constant h3::after{content:" — constant";font-weight:400;color:var(--faint);
  font-size:13px}
.idea.orphan h3::after{content:" — in no vision";font-weight:400;color:var(--red);
  font-size:13px}

.side,.legend{padding:26px 28px}
.side h2,.legend h2{font:600 18px/1.2 var(--sans);letter-spacing:-.012em;margin:0 0 12px}
.side .row{display:grid;grid-template-columns:118px 1fr;gap:14px;padding:9px 0;
  border-top:1px solid var(--rule);font-size:14px}
.side .row b{font-weight:600}
.side .row span{color:var(--ink-2)}
.side .row .who{color:var(--faint);font-size:12.5px;display:block}
.legend p{margin:0 0 10px;font-size:14px;color:var(--ink-2)}
.legend .k{display:flex;align-items:center;gap:10px;font-size:13.5px;color:var(--muted);
  margin:6px 0}
.legend .k i{width:9px;height:9px;border-radius:50%;background:var(--ink);display:inline-block}
.legend .k s{width:36px;height:0;border-top:1.5px solid #d6d6d2;display:inline-block;
  text-decoration:none}
.legend .k s.on{border-color:var(--ink)}

/* ── visions: the assemblies ─────────────────────────────────────────── */
.vision{padding:34px 36px 30px;display:flex;flex-direction:column;gap:22px}
.vision header{display:flex;align-items:flex-start;gap:24px;cursor:pointer}
.vision header .mark{width:44px;height:44px;flex:none;border:1.5px solid var(--ink);
  border-radius:50%;display:flex;align-items:center;justify-content:center;
  font-weight:600;font-size:15px}
.vision header h2{font:600 33px/1.08 var(--sans);letter-spacing:-.028em;margin:0}
.vision header .thesis{font-size:20px;line-height:1.35;color:var(--ink-2);margin:8px 0 0;
  max-width:40ch}
.vision header .open{margin-left:auto;flex:none;color:var(--muted);font-size:13.5px;
  padding-top:6px}
.vision .story{font-size:15px;line-height:1.58;color:var(--ink-2);max-width:78ch;margin:0}
.vision .specimen{border:1px solid var(--rule);overflow:hidden}
.vision .specimen iframe{display:block;width:100%;aspect-ratio:16/9;border:0}
.vision .two{display:grid;grid-template-columns:1fr 1fr;gap:28px}
.vision h4{font:600 13.5px/1.2 var(--sans);color:var(--muted);margin:0 0 8px}
.vision .lenses{display:grid;grid-template-columns:104px 1fr;gap:6px 14px;font-size:14px}
.vision .lenses b{font-weight:600}
.vision .lenses span{color:var(--ink-2)}
.vision .chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{appearance:none;background:none;border:1px solid var(--rule);border-radius:999px;
  padding:4px 11px;font-size:13px;cursor:pointer;color:var(--ink-2)}
.chip:hover{border-color:var(--ink)}
.chip.constant{color:var(--muted)}
.vision .tension{font-size:14px;line-height:1.5;color:var(--ink-2);margin:0;padding-top:14px;
  border-top:1px solid var(--rule)}
.vision .tension b{color:var(--red);font-weight:600}
.vision .asks{font-size:14px;color:var(--ink-2);margin:0}
.vision .asks b{font-weight:600}

/* ── plates: the material, and the gaps where there is none ──────────── */
.strip{display:flex;gap:12px;overflow:hidden}
.clip{width:196px;flex:none;margin:0}
.clip img{width:100%;aspect-ratio:16/10;object-fit:cover;object-position:top;display:block;
  border:1px solid var(--rule);background:#eee}
.clip .gone{width:100%;aspect-ratio:16/10;border:1px dashed var(--rule);background:var(--wash);
  display:flex;align-items:center;justify-content:center;padding:10px;
  font-family:var(--mono);font-size:10px;line-height:1.4;color:var(--red);
  word-break:break-all;text-align:center}
.clip figcaption{font-size:12.5px;line-height:1.35;color:var(--ink-2);margin-top:6px}

/* ── the drawer: the detail, and where a reaction goes ───────────────── */
.drawer{position:fixed;top:52px;right:0;bottom:0;width:460px;max-width:100%;
  background:var(--paper);border-left:1px solid var(--rule);z-index:50;
  transform:translateX(100%);transition:transform .3s cubic-bezier(.2,.7,.2,1);
  overflow:auto;padding:28px 30px 40px}
.drawer.open{transform:none}
.drawer .close{position:absolute;top:14px;right:14px;appearance:none;background:none;
  border:0;font-size:22px;line-height:1;color:var(--muted);cursor:pointer;padding:6px}
.drawer .kind{color:var(--muted);font-size:13px;margin-bottom:6px}
.drawer h2{font:600 26px/1.15 var(--sans);letter-spacing:-.022em;margin:0 0 10px;
  padding-right:30px}
.drawer .line{font-size:17px;line-height:1.4;color:var(--ink-2);margin:0 0 18px}
.drawer h5{font:600 13.5px/1.2 var(--sans);color:var(--muted);margin:22px 0 8px}
.drawer p{font-size:14.5px;line-height:1.58;color:var(--ink-2);margin:0 0 10px}
.drawer .lenses{display:grid;grid-template-columns:92px 1fr;gap:6px 12px;font-size:14px}
.drawer .lenses b{font-weight:600}
.drawer .lenses span{color:var(--ink-2)}
.drawer .ev{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.drawer .ev .clip{width:auto}
.drawer .chips{display:flex;flex-wrap:wrap;gap:6px}
.drawer textarea{width:100%;min-height:96px;border:1px solid var(--rule);border-radius:2px;
  padding:10px 12px;font:inherit;font-size:14px;resize:vertical;background:var(--wash)}
.drawer textarea:focus{border-color:var(--ink);outline:none}
.drawer .saved{font-size:12.5px;color:var(--faint);margin-top:4px;min-height:16px}
.drawer .src{font-size:12.5px;color:var(--faint);margin-top:22px;line-height:1.5;
  border-top:1px solid var(--rule);padding-top:12px}

/* ── minimap and the one line of instruction ─────────────────────────── */
.mini{position:fixed;left:16px;bottom:16px;width:232px;height:120px;overflow:hidden;
  background:rgba(255,255,255,.94);border:1px solid var(--rule);z-index:45;cursor:pointer}
.mini div{position:absolute;background:#e8e8e5}
.mini .vp{background:none;border:1.5px solid var(--ink)}
.hint{position:fixed;left:0;right:0;bottom:22px;text-align:center;color:var(--muted);
  font-size:13px;z-index:44;pointer-events:none;transition:opacity .4s}
.hint.gone{opacity:0}
@media (max-width:760px){.mini{display:none}.drawer{width:100%}}
"""

# The runtime. It measures every card after it is in the DOM and places it, because a card's
# height is its text's height and Python cannot know that. Everything below is driven by DATA.
JS = r"""
var $=function(s,r){return (r||document).querySelector(s)},
    $$=function(s,r){return [].slice.call((r||document).querySelectorAll(s))};
function el(tag,cls,h){var e=document.createElement(tag); if(cls)e.className=cls;
  if(h!=null)e.innerHTML=h; return e;}
function esc(s){return String(s==null?'':s)
  .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function para(t){return String(t||'').split(/\n\s*\n/).filter(Boolean)
  .map(function(p){return '<p>'+esc(p).replace(/\n/g,' ')+'</p>'}).join('');}

var LENSES=DATA.lenses, IDEAS=DATA.ideas, VISIONS=DATA.visions;
var byId={}; IDEAS.forEach(function(i){byId[i.id]=i});
var visById={}; VISIONS.forEach(function(v){visById[v.id]=v});
var lensById={}; LENSES.forEach(function(l){lensById[l.id]=l});

var COLW=330, COLGAP=30, ROWGAP=22, COLTOP=120, CARDGAP=60;
var BRIEFW=860, SIDEW=700, VISW=1380, VISGAP=60, PAD=40;

var canvas=$('#canvas'), wires=$('#wires'), desk=$('#desk');
var REGIONS={}, ideaEl={}, visEl={};

function place(node,x,y,w){node.style.left=x+'px'; node.style.top=y+'px';
  if(w) node.style.width=w+'px'; canvas.appendChild(node); return node;}

/* ── the brief ─────────────────────────────────────────────────────── */
var facts=DATA.facts.map(function(f){
  return '<div class="fact"><b>'+esc(f.kind)+'</b><span>'+esc(f.text)
    +(f.who?'<small>'+esc(f.who)+'</small>':'')+'</span></div>';}).join('');
var brief=el('div','card brief',
  '<h1>'+esc(DATA.title)+'</h1>'+para(DATA.brief.join('\n\n'))
  +(facts?'<div class="facts">'+facts+'</div>':'')
  +'<p class="howto">Every claim about someone else here is our reading of their public '
  +'material. Every claim about this engagement carries who said it and when.</p>');
brief.id='brief'; place(brief,PAD,PAD,BRIEFW);

/* ── ideas, a column per lens ──────────────────────────────────────── */
var ideasX=PAD+BRIEFW+CARDGAP, col={}, bottom=PAD;
LENSES.forEach(function(L,i){
  var x=ideasX+i*(COLW+COLGAP);
  var h=el('div','lenshead','<h2>'+esc(L.name)+'</h2><p>'+esc(L.what)+'</p>');
  place(h,x,PAD,COLW);
  col[L.id]={x:x,y:PAD+COLTOP};
});
var unfiled={x:ideasX+LENSES.length*(COLW+COLGAP),y:PAD+COLTOP};
IDEAS.forEach(function(idea){
  var c=col[idea.lens]||unfiled;
  var dots=idea.visions.map(function(v){
    return '<i title="'+esc(visById[v].name)+'"></i>'}).join('');
  var n=VISIONS.length;
  var cls='card idea'+(idea.constant?' constant':'')+(idea.visions.length?'':' orphan');
  var card=el('div',cls,'<h3>'+esc(idea.title)+'</h3><p>'+esc(idea.line)+'</p>'
    +'<div class="foot">'+dots+'<em>'+idea.visions.length+' of '+n+'</em></div>');
  card.id='i-'+idea.id; card.tabIndex=0; card.setAttribute('role','button');
  card.dataset.idea=idea.id;
  place(card,c.x,c.y,COLW);
  c.y+=card.offsetHeight+ROWGAP;
  bottom=Math.max(bottom,c.y);
  ideaEl[idea.id]=card;
});
REGIONS.ideas={x:ideasX-20,y:PAD-20,w:(LENSES.length||1)*(COLW+COLGAP)+40,h:bottom-PAD+40};

/* ── what is still open, and the legend ────────────────────────────── */
var sideX=ideasX+((LENSES.length||1)+(unfiled.y>PAD+COLTOP?1:0))*(COLW+COLGAP)+CARDGAP;
var sideY=PAD;
if(DATA.open.length){
  var rows=DATA.open.map(function(o){
    return '<div class="row"><b>'+esc(o.what)+'</b><span>'+esc(o.text)
      +(o.who?'<span class="who">'+esc(o.who)+'</span>':'')+'</span></div>';}).join('');
  var side=el('div','card side','<h2>What is still open, and who closes it</h2>'+rows);
  side.id='side'; place(side,sideX,sideY,SIDEW);
  sideY+=side.offsetHeight+CARDGAP;
}
var legend=el('div','card legend','<h2>Reading the desk</h2>'
  +'<p>Columns are the lenses this brand has to answer. Cards are ideas — one title, one '
  +'sentence. Visions below assemble the ideas into one whole brand.</p>'
  +'<div class="k"><i></i> a vision this idea is part of</div>'
  +'<div class="k"><s></s> the idea feeds this vision</div>'
  +'<div class="k"><s class="on"></s> lit when you hover either end</div>'
  +'<p style="margin-top:12px">An idea marked <em>constant</em> is in every vision: it is the '
  +'brand whichever way this goes.</p>'
  +'<p>Nothing on this desk is chosen. Picking a vision is a decision that gets its own '
  +'file, and it links back here.</p>');
legend.id='legend'; place(legend,sideX,sideY,SIDEW);
var briefH=Math.max(brief.offsetHeight, legend.offsetTop+legend.offsetHeight-PAD);
REGIONS.brief={x:PAD-20,y:PAD-20,w:BRIEFW+40,h:brief.offsetHeight+40};
bottom=Math.max(bottom,PAD+briefH);

/* ── the visions ───────────────────────────────────────────────────── */
var visY=bottom+140, visRight=PAD;
VISIONS.forEach(function(v,i){
  var x=PAD+i*(VISW+VISGAP);
  var lens=Object.keys(v.lenses).map(function(k){
    return '<b>'+esc(lensById[k]?lensById[k].name:k)+'</b><span>'+esc(v.lenses[k])+'</span>';
  }).join('');
  var chips=v.ideas.map(function(id){var it=byId[id];
    return '<button class="chip'+(it.constant?' constant':'')+'" data-open="'+id+'">'
      +esc(it.title)+'</button>';}).join('');
  var card=el('section','card vision',
    '<header data-vopen="'+v.id+'"><div class="mark">'+esc(v.mark)+'</div><div><h2>'
      +esc(v.name)+'</h2><p class="thesis">'+esc(v.thesis)+'</p></div>'
      +'<span class="open">Open</span></header>'
    +'<div class="story">'+para(v.story)+'</div>'
    +(v.specimen?'<div class="specimen"><iframe sandbox loading="lazy" title="'
      +esc(v.name)+' — specimen" srcdoc="'+esc(v.specimenDoc)+'"></iframe></div>':'')
    +(lens||chips?'<div class="two">'
      +'<div><h4>How it comes together</h4><div class="lenses">'+lens+'</div></div>'
      +'<div><h4>Made of</h4><div class="chips">'+chips+'</div></div></div>':'')
    +(v.plates.length?'<div><h4>Evidence</h4><div class="strip">'
      +v.plates.map(clip).join('')+'</div></div>':'')
    +(v.tension?'<p class="tension"><b>Tension.</b> '+esc(v.tension)+'</p>':'')
    +(v.asks?'<p class="asks"><b>It asks for:</b> '+esc(v.asks)+'</p>':''));
  card.id='v-'+v.id; card.dataset.vis=v.id;
  place(card,x,visY,VISW);
  visEl[v.id]=card;
  REGIONS['v-'+v.id]={x:x-20,y:visY-20,w:VISW+40,h:card.offsetHeight+40};
  visRight=x+VISW;
});

function clip(p){
  var body=p.missing
    ? '<div class="gone">'+esc(p.src)+'</div>'
    : '<img src="'+esc(p.src)+'" alt="" loading="lazy">';
  var cap=p.url?'<a href="'+esc(p.url)+'" target="_blank" rel="noreferrer">'+esc(p.cap||p.url)
    +'</a>':esc(p.cap);
  return '<figure class="clip">'+body+(cap?'<figcaption>'+cap+'</figcaption>':'')+'</figure>';
}

/* ── the canvas is as big as what is on it ─────────────────────────── */
var CW=Math.max(visRight,sideX+SIDEW,ideasX+(LENSES.length||1)*(COLW+COLGAP))+PAD;
var CH=visY+Math.max.apply(null,VISIONS.map(function(v){
  return visEl[v.id].offsetHeight;}).concat([0]))+PAD;
canvas.style.width=CW+'px'; canvas.style.height=CH+'px';
wires.setAttribute('width',CW); wires.setAttribute('height',CH);
wires.style.width=CW+'px'; wires.style.height=CH+'px';

/* ── the wires: which ideas build which vision ─────────────────────── */
function drawWires(){
  wires.innerHTML='';
  IDEAS.forEach(function(idea,n){
    var a=ideaEl[idea.id];
    var ax=a.offsetLeft+a.offsetWidth/2, ay=a.offsetTop+a.offsetHeight;
    idea.visions.forEach(function(vid,k){
      var b=visEl[vid]; if(!b) return;
      var off=(k-(idea.visions.length-1)/2)*10;
      var x1=ax+off, y1=ay;
      var x2=b.offsetLeft+b.offsetWidth/2+((n%9)-4)*40, y2=b.offsetTop;
      var cy=(y1+y2)/2;
      var p=document.createElementNS('http://www.w3.org/2000/svg','path');
      p.setAttribute('d','M'+x1+' '+y1+' C'+x1+' '+cy+' '+x2+' '+cy+' '+x2+' '+y2);
      p.dataset.idea=idea.id; p.dataset.vis=vid;
      wires.appendChild(p);
    });
  });
}
drawWires();

/* ── hover: the shape of the argument ──────────────────────────────── */
function lightPaths(test){$$('path',wires).forEach(function(p){
  p.classList.toggle('on',test(p));});}
function focusIdea(id){
  canvas.classList.add('focus'); wires.classList.add('focus');
  $$('.card').forEach(function(c){c.classList.remove('on')});
  ideaEl[id].classList.add('on');
  byId[id].visions.forEach(function(v){if(visEl[v])visEl[v].classList.add('on')});
  lightPaths(function(p){return p.dataset.idea===id});
}
function focusVis(vid){
  canvas.classList.add('focus'); wires.classList.add('focus');
  $$('.card').forEach(function(c){c.classList.remove('on')});
  visEl[vid].classList.add('on');
  visById[vid].ideas.forEach(function(i){if(ideaEl[i])ideaEl[i].classList.add('on')});
  lightPaths(function(p){return p.dataset.vis===vid});
}
function unfocus(){
  canvas.classList.remove('focus'); wires.classList.remove('focus');
  $$('.card.on').forEach(function(c){c.classList.remove('on')});
  $$('path.on',wires).forEach(function(p){p.classList.remove('on')});
}
Object.keys(ideaEl).forEach(function(id){
  ideaEl[id].addEventListener('mouseenter',function(){focusIdea(id)});
  ideaEl[id].addEventListener('mouseleave',unfocus);});
Object.keys(visEl).forEach(function(v){
  visEl[v].addEventListener('mouseenter',function(){focusVis(v)});
  visEl[v].addEventListener('mouseleave',unfocus);});

/* ── the drawer ────────────────────────────────────────────────────── */
var drawer=$('#drawer'), dbody=$('#dbody');
var NOTES='desk-notes-'+DATA.key; var notes={};
try{notes=JSON.parse(localStorage.getItem(NOTES)||'{}')}catch(e){notes={}}
function saveNote(k,v){notes[k]=v;
  try{localStorage.setItem(NOTES,JSON.stringify(notes))}catch(e){}}
function lensRows(obj){return Object.keys(obj).map(function(k){
  return '<b>'+esc(lensById[k]?lensById[k].name:k)+'</b><span>'+esc(obj[k])+'</span>';
}).join('');}
function noteBox(key){
  return '<h5>Your note</h5><textarea data-note="'+esc(key)+'" placeholder="What you '
    +'think. Kept in this browser only.">'+esc(notes[key]||'')+'</textarea>'
    +'<div class="saved"></div>';
}
function show(h){dbody.innerHTML=h; drawer.classList.add('open'); drawer.scrollTop=0;}
function openIdea(id){
  var i=byId[id]; if(!i) return;
  var where=i.visions.map(function(v){return visById[v].name}).join(', ')||'no vision yet';
  show('<div class="kind">Idea · '+esc(lensById[i.lens]?lensById[i.lens].name:'unfiled')
    +'</div><h2>'+esc(i.title)+'</h2><p class="line">'+esc(i.line)+'</p>'
    +(i.how?'<h5>How it works</h5>'+para(i.how):'')
    +(Object.keys(i.lenses).length?'<h5>What it does</h5><div class="lenses">'
      +lensRows(i.lenses)+'</div>':'')
    +(i.plates.length?'<h5>Evidence</h5><div class="ev">'+i.plates.map(clip).join('')
      +'</div>':'')
    +'<h5>In</h5><p>'+esc(where)+'</p>'+noteBox('i:'+id));
  focusIdea(id);
}
function openVis(vid){
  var v=visById[vid]; if(!v) return;
  show('<div class="kind">Vision</div><h2>'+esc(v.name)+'</h2>'
    +'<p class="line">'+esc(v.thesis)+'</p>'+para(v.story)
    +(Object.keys(v.lenses).length?'<h5>How it comes together</h5><div class="lenses">'
      +lensRows(v.lenses)+'</div>':'')
    +(v.tension?'<h5>Tension</h5><p>'+esc(v.tension)+'</p>':'')
    +(v.asks?'<h5>It asks for</h5><p>'+esc(v.asks)+'</p>':'')
    +(v.plates.length?'<h5>Evidence</h5><div class="ev">'+v.plates.map(clip).join('')
      +'</div>':'')
    +noteBox('v:'+vid));
  focusVis(vid);
}
$('#dclose').addEventListener('click',function(){drawer.classList.remove('open'); unfocus();});
document.addEventListener('keydown',function(e){
  if(e.key==='Escape'){drawer.classList.remove('open'); unfocus();}});
document.addEventListener('click',function(e){
  var chip=e.target.closest('[data-open]'); if(chip){openIdea(chip.dataset.open); return;}
  var vh=e.target.closest('[data-vopen]'); if(vh){openVis(vh.dataset.vopen); return;}
  var idea=e.target.closest('.idea'); if(idea){openIdea(idea.dataset.idea);}
});
document.addEventListener('input',function(e){
  var t=e.target;
  if(t.matches&&t.matches('textarea[data-note]')){
    saveNote(t.dataset.note,t.value);
    var s=t.parentNode.querySelector('.saved');
    if(s){s.textContent='Saved in this browser.'; clearTimeout(s._t);
      s._t=setTimeout(function(){s.textContent=''},1400);}
  }});
document.addEventListener('keydown',function(e){
  if(e.key==='Enter'&&document.activeElement
     &&document.activeElement.classList.contains('idea')){
    openIdea(document.activeElement.dataset.idea);}});

/* ── pan, zoom, fit, minimap ───────────────────────────────────────── */
var view={x:0,y:0,z:1}, drag=null, moved=0;
function apply(anim){
  canvas.classList.toggle('anim',!!anim);
  canvas.style.transform='translate('+view.x+'px,'+view.y+'px) scale('+view.z+')';
  $('#pct').textContent=Math.round(view.z*100)+'%'; drawMini();
}
function clampZ(z){return Math.min(1.6,Math.max(0.1,z))}
function zoomAt(f,cx,cy){
  var z2=clampZ(view.z*f), k=z2/view.z;
  view.x=cx-(cx-view.x)*k; view.y=cy-(cy-view.y)*k; view.z=z2; apply(false);
}
function fitRect(x,y,w,h,pad){
  pad=pad||40; var r=desk.getBoundingClientRect();
  var z=clampZ(Math.min((r.width-pad*2)/w,(r.height-pad*2)/h));
  view.z=z; view.x=(r.width-w*z)/2-x*z; view.y=(r.height-h*z)/2-y*z; apply(true);
}
desk.addEventListener('wheel',function(e){
  e.preventDefault(); var r=desk.getBoundingClientRect();
  if(e.ctrlKey||e.metaKey){zoomAt(Math.exp(-e.deltaY*0.0022),e.clientX-r.left,e.clientY-r.top);}
  else{view.x-=e.deltaX; view.y-=e.deltaY; apply(false);}
},{passive:false});
desk.addEventListener('pointerdown',function(e){
  if(e.button!==0) return;
  var soft=!!e.target.closest('a,button,textarea,.idea,header,.chip,iframe');
  drag={x:e.clientX,y:e.clientY,vx:view.x,vy:view.y,soft:soft};
  if(!soft) desk.classList.add('dragging');
  moved=0; try{desk.setPointerCapture(e.pointerId)}catch(err){}
});
desk.addEventListener('pointermove',function(e){
  if(!drag) return;
  var dx=e.clientX-drag.x, dy=e.clientY-drag.y;
  moved=Math.max(moved,Math.abs(dx)+Math.abs(dy));
  if(drag.soft&&moved<6) return;
  view.x=drag.vx+dx; view.y=drag.vy+dy; apply(false);
});
function endDrag(){drag=null; desk.classList.remove('dragging');}
desk.addEventListener('pointerup',endDrag); desk.addEventListener('pointercancel',endDrag);
desk.addEventListener('click',function(e){
  if(moved>6){e.stopPropagation(); e.preventDefault();}},true);
$('#zin').addEventListener('click',function(){
  var r=desk.getBoundingClientRect(); zoomAt(1.25,r.width/2,r.height/2);});
$('#zout').addEventListener('click',function(){
  var r=desk.getBoundingClientRect(); zoomAt(0.8,r.width/2,r.height/2);});
$('#zfit').addEventListener('click',function(){fitRect(0,0,CW,CH,20);});
$('#idx').addEventListener('click',function(e){
  var b=e.target.closest('button[data-go]'); if(!b) return;
  var R=REGIONS[b.dataset.go]; if(R) fitRect(R.x,R.y,R.w,R.h,48);
  $$('#idx button').forEach(function(x){x.classList.toggle('on',x===b)});
});
Object.keys(visEl).forEach(function(v){
  visEl[v].addEventListener('dblclick',function(e){
    if(e.target.closest('a,button,textarea')) return;
    fitRect(REGIONS['v-'+v].x,REGIONS['v-'+v].y,REGIONS['v-'+v].w,REGIONS['v-'+v].h,48);
  });});

var mini=$('#mini'), ms=Math.min(230/CW,118/CH);
function drawMini(){
  mini.innerHTML='';
  Object.keys(REGIONS).forEach(function(k){
    var R=REGIONS[k], d=el('div');
    d.style.cssText='left:'+R.x*ms+'px;top:'+R.y*ms+'px;width:'+R.w*ms+'px;height:'
      +R.h*ms+'px'; mini.appendChild(d);
  });
  var r=desk.getBoundingClientRect(), vp=el('div','vp');
  vp.style.cssText='left:'+(-view.x/view.z*ms)+'px;top:'+(-view.y/view.z*ms)+'px;width:'
    +(r.width/view.z*ms)+'px;height:'+(r.height/view.z*ms)+'px';
  mini.appendChild(vp);
}
mini.addEventListener('click',function(e){
  var mr=mini.getBoundingClientRect();
  var cx=(e.clientX-mr.left)/ms, cy=(e.clientY-mr.top)/ms;
  var r=desk.getBoundingClientRect();
  view.x=r.width/2-cx*view.z; view.y=r.height/2-cy*view.z; apply(true);
});
window.addEventListener('resize',function(){apply(false)});

fitRect(0,0,CW,CH,20);
setTimeout(function(){$('#hint').classList.add('gone')},6000);
"""


def project_kicker(bd: dict) -> str:
    """` · Client Portal`, or nothing at all in a one-project workspace."""
    key = bd.get("project", "")
    if not MULTI_PROJECT or not key or key == "all":
        return ""
    return " · " + PROJECT_LABEL.get(key, key)


def data_blob(bd: dict) -> str:
    """Everything the runtime needs, and nothing it does not. A specimen is wrapped into a
    whole document here so the iframe can be sandboxed: a vision's own type and colour are
    its own, and its CSS cannot leak into the desk around it."""
    def vision(v):
        out = dict(v)
        out.pop("specimen", None)
        out["specimen"] = bool(v["specimen"])
        out["specimenDoc"] = (
            '<!doctype html><meta charset="utf-8">' + FONT_LINK
            + '<style>html,body{margin:0;height:100%;'
              'font-family:"Inter",system-ui,sans-serif}</style>' + v["specimen"]
        ) if v["specimen"] else ""
        return out

    return json.dumps({
        "key": bd["path"].stem,
        "title": bd["title"],
        "brief": bd["brief"],
        "facts": bd["facts"],
        "open": bd["open"],
        "lenses": bd["lenses"],
        "ideas": bd["ideas"],
        "visions": [vision(v) for v in bd["visions"]],
    }, ensure_ascii=False)


def build(bd: dict) -> str:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    sub = bd["subtitle"] or f'{len(bd["ideas"])} ideas, {len(bd["visions"])} visions'
    idx = ['<button data-go="brief">Brief</button>', '<button data-go="ideas">Ideas</button>']
    idx += [f'<button data-go="v-{v["id"]}">{html.escape(v["name"])}</button>'
            for v in bd["visions"]]

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(bd["title"])} — {html.escape(PROJECT_NAME)}</title>
{FONT_LINK}<style>{CSS}</style></head><body>

<div class="bar">
  <span class="title">{html.escape(PROJECT_NAME)}{html.escape(project_kicker(bd))}</span>
  <span class="sub">{html.escape(sub)}</span>
  <span class="idx" id="idx">{"".join(idx)}</span>
  <span class="zoom">
    <button id="zout" title="Zoom out">−</button>
    <span class="pct" id="pct">100%</span>
    <button id="zin" title="Zoom in">+</button>
    <button id="zfit">Fit</button>
  </span>
</div>

<div class="desk" id="desk">
  <div class="canvas" id="canvas">
    <svg class="wires" id="wires" xmlns="http://www.w3.org/2000/svg"></svg>
  </div>
</div>

<div class="mini" id="mini"></div>
<div class="hint" id="hint">Drag to move · scroll to pan · ⌘/Ctrl-scroll to zoom ·
  click a card for the detail</div>

<aside class="drawer" id="drawer">
  <button class="close" id="dclose" aria-label="Close">×</button>
  <div id="dbody"></div>
  <div class="src">Generated {stamp} from <code>{bd["path"].relative_to(ROOT)}</code>.
    Nothing here is decided — picking a vision is a decision that links back to that file.</div>
</aside>

<script>var DATA={data_blob(bd)};</script>
<script>{JS}</script>
</body></html>"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("files", nargs="*", help="desks to render (default: all)")
    ap.add_argument("--open", action="store_true")
    args = ap.parse_args()

    paths = ([Path(f).resolve() for f in args.files] if args.files
             else sorted(p for p in DIR.glob("*.md") if p.name != "README.md"))
    if not paths:
        print("no moodboards yet — /moodboard writes the first one")
        return 0

    written = []
    for p in paths:
        bd = parse(p)
        out = p.with_suffix(".html")
        out.write_text(build(bd), encoding="utf-8")
        gone = sum(1 for i in bd["ideas"] + bd["visions"]
                   for pl in i["plates"] if pl["missing"])
        orphan = sum(1 for i in bd["ideas"] if not i["visions"])
        note = "".join([f", {gone} plate(s) missing" if gone else "",
                        f", {orphan} idea(s) in no vision" if orphan else ""])
        print(f"{out.relative_to(ROOT)}  ·  {len(bd['ideas'])} idea(s), "
              f"{len(bd['visions'])} vision(s){note}")
        written.append(out)

    if args.open:
        subprocess.run(["open", *[str(w) for w in written]], check=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
