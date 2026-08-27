#!/usr/bin/env python3
"""Render `brain/feed.html` — where we are, and what is waiting on the owner.

    python3 brain/feed.py            write brain/feed.html
    python3 brain/feed.py --open     ... and open it
    python3 brain/feed.py --check    is the page older than what it projects?

## Why this is generated and not written

**The feed is a projection, exactly as the external tracker is** — written outward, never read
back as authority. A hand-written page would restate `now.md`, the plan, the ADRs and the task
list in a fifth place, and the record-keeping invariant this workspace runs on is *one owner per
class of information; everything else links, never restates*. So the page is a function of the
files: position from `now.md`, the arc from `plan.md`, the current stage's exit conditions from
the decision that owns them, tasks from `tasks.md`, and the decisions waiting on the owner from
`feed-items.md`, which is the one file this adds.

**The problem it solves is the reading cost, not the writing cost.** Every sentence in this
workspace is dense with references — `0012`, `Q9`, `PROJ-7`, `[[an-insight-slug]]` — and each one
is a file the reader has to go and find. The compression is right for the record and wrong for a
person scanning it. So the glossary is built from the files themselves and every reference on the
page carries its own definition on hover and its own link on click. **Nothing here is a summary
someone maintains**; if a decision's title changes, the tooltip changes with it.

Dependency-free and offline, matching the rest of the tree. The page is a local file rather than
anything hosted: it may carry confidential project facts, and `file://` links into the repo only
resolve from a local page anyway.
"""

import argparse
import hashlib
import html
import math
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path

BRAIN = Path(__file__).resolve().parent
ROOT = BRAIN.parent
OUT = BRAIN / "feed.html"

# Project constants live in brain/workspace.toml and are read through config.py — never
# duplicated here. `doctor.py` reads the same file, so a prefix cannot disagree with itself.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import PROJECT_NAME, TRACKER_PREFIX  # noqa: E402

_KEY = rf"{TRACKER_PREFIX}-\d+" if TRACKER_PREFIX else r"(?!x)x"   # never-matching if None

SOURCES = ("now.md", "plan.md", "tasks.md", "feed-items.md", "open-questions.md",
           "tags.md", "glossary.md")


# ---------------------------------------------------------------------------------------------
# The glossary — every reference on the page defines itself
# ---------------------------------------------------------------------------------------------

def _first_para(text: str, after: str | None = None, limit: int = 340) -> str:
    """The first real paragraph, optionally after a heading. Front matter and blockquotes skipped."""
    body = text
    if body.startswith("---"):
        end = body.find("\n---", 3)
        if end != -1:
            body = body[end + 4:]
    if after:
        i = body.find(after)
        if i == -1:
            return ""
        body = body[i + len(after):]
    for block in re.split(r"\n\s*\n", body):
        block = block.strip()
        if not block or block.startswith(("#", ">", "```", "|", "---")):
            continue
        # A tooltip is plain text, so the markdown comes out here rather than being escaped into
        # visible `**` and backticks in an attribute a reader hovers.
        flat = " ".join(block.split())
        flat = re.sub(r"\[\[([^\]]+)\]\]", r"\1", flat)
        flat = re.sub(r"\*\*|`|(?<!\w)\*(?!\s)|(?<!\s)\*(?!\w)", "", flat)
        return flat if len(flat) <= limit else flat[:limit - 1].rstrip() + "…"
    return ""


def glossary() -> dict:
    """`{key: {kind, title, gloss, path}}` for every referable thing in the brain.

    Built by reading, never by hand. The keys are exactly the tokens the prose already uses, which
    is what lets the linkifier be conservative: a token becomes a link **only if it resolves here**,
    so a four-digit number that is not a decision stays plain text rather than becoming a dead tooltip.
    """
    g: dict = {}

    for path in sorted((BRAIN / "decisions").glob("*.md")):
        m = re.match(r"^(\d{4})-", path.name)
        if not m:
            continue
        text = path.read_text()
        head = re.search(r"^#\s*(\d{4})\s*[—-]\s*(.+)$", text, re.M)
        title = head.group(2).strip() if head else path.stem
        status = re.search(r"^Date:.*·\s*Status:\s*(.+)$", text, re.M)
        g[m.group(1)] = {
            "kind": "decision " + m.group(1),
            "title": title,
            "gloss": _first_para(text, after="## Decision"),
            "note": (status.group(1).strip() if status else ""),
            "path": path,
        }
        g[path.stem] = g[m.group(1)]          # the full [[0011-slug]] form

    for path in sorted((BRAIN / "insights").glob("*.md")):
        text = path.read_text()
        head = re.search(r"^#\s+(.+)$", text, re.M)
        g[path.stem] = {"kind": "insight", "title": (head.group(1).strip() if head else path.stem),
                        "gloss": _first_para(text), "note": "", "path": path}

    # Tasks. The title is on the header line and the substance is the indented note under it, so the
    # gloss is the first indented line — which is where every task in that file puts its result.
    tasks = (BRAIN / "tasks.md").read_text().splitlines()
    for i, line in enumerate(tasks):
        m = re.match(rf"^-\s+`(\w+)`\s*·\s*(P\d)\s*·\s*(.*?)·\s*({_KEY}|skip|—)\s*—\s*\*\*(.+?)\*\*",
                     line)
        if not m:
            continue
        status, prio, labels, pointer, title = m.groups()
        gloss = ""
        for nxt in tasks[i + 1:]:
            if not nxt.startswith("      "):
                break
            if nxt.strip():
                gloss = " ".join(nxt.split())
                break
        entry = {"kind": f"task · {status}", "title": title,
                 "gloss": re.sub(r"\*\*", "", gloss)[:340],
                 "note": f"{prio} · {labels.strip().strip('·').strip() or 'no label'}",
                 "path": BRAIN / "tasks.md"}
        if TRACKER_PREFIX and pointer.startswith(TRACKER_PREFIX + "-"):
            g[pointer] = entry

    # Open questions. `Qnn` appears at the end of a bullet or inline; the useful gloss is the
    # bulleted paragraph that carries it, with its owner tag intact — the owner is the whole point
    # of the question file, so a tooltip that dropped it would hide who can answer.
    qtext = (BRAIN / "open-questions.md").read_text()
    answered_at = qtext.find("\n## Answered")
    for m in re.finditer(r"\bQ(\d{1,2})\b", qtext):
        key = f"Q{m.group(1)}"
        if key in g:
            continue
        start = qtext.rfind("\n- ", 0, m.start())
        if start == -1:
            continue
        end = qtext.find("\n- ", m.end())
        block = qtext[start:end if end != -1 else m.end() + 400]
        owner = re.search(r"\*\*\[([^\]]+)\]", block)
        g[key] = {
            "kind": "question",
            "title": key + (f" · owner: {owner.group(1)}" if owner else ""),
            "gloss": _first_para(block.lstrip("\n- ")),
            "note": "answered" if (answered_at != -1 and m.start() > answered_at) else "open",
            "path": BRAIN / "open-questions.md",
        }
    return g


# ---------------------------------------------------------------------------------------------
# A small markdown renderer — enough for the prose this repo writes, and nothing more
# ---------------------------------------------------------------------------------------------

def _inline(text: str, g: dict) -> str:
    """Escape → lift every tag out behind a sentinel → emphasise → put the tags back.

    **The lift is not tidiness, it is correctness.** A tooltip's `data-gloss` is prose read out of
    another file, and that prose contains `**bold**` and backticks. Running the emphasis pass over a
    string that already holds those attributes rewrites the *inside of an attribute* into a `<strong>`
    tag, which produces exactly the unbalanced markup an HTML validator then reports. Emphasis
    therefore only ever sees text with no tags in it, and the tags are restored afterwards.
    """
    out = html.escape(text)
    lifted: list[str] = []

    def lift(markup: str) -> str:
        lifted.append(markup)
        return f"\x00{len(lifted) - 1}\x00"

    def ref(key: str, label: str) -> str:
        e = g[key]
        rel = e["path"].relative_to(ROOT)
        return lift(f'<a class="ref" href="{html.escape(str(e["path"]))}" '
                    f'data-title="{html.escape(e["title"])}" '
                    f'data-kind="{html.escape(e["kind"])}" '
                    f'data-note="{html.escape(e.get("note", ""))}" '
                    f'data-gloss="{html.escape(e["gloss"])}" '
                    f'data-path="{html.escape(str(rel))}">') + label + lift("</a>")

    # [[wiki-links]] — the repo's own cross-reference form.
    def wiki(m):
        key = m.group(1)
        label = html.escape(g[key]["title"]) if key in g else html.escape(key)
        if key in g:
            return ref(key, label)
        return lift('<span class="ref dead">') + label + lift("</span>")
    out = re.sub(r"\[\[([^\]]+)\]\]", wiki, out)

    # Bare tokens: decision numbers, question numbers, task pointers. Conservative by construction —
    # only linkified when the key resolves in the glossary.
    def bare(m):
        key = m.group(0)
        return ref(key, key) if key in g else key
    out = re.sub(rf"\b(?:{_KEY}|Q\d{{1,2}}|0\d{{3}})\b", bare, out)

    # `code` — a backticked path that exists on disk becomes openable.
    def code(m):
        inner = m.group(1)
        target = ROOT / inner.rstrip("/")
        if "/" in inner and target.exists():
            return lift(f'<a class="path" href="{html.escape(str(target))}" '
                        f'title="open {html.escape(inner)}"><code>{inner}</code></a>')
        return lift(f"<code>{inner}</code>")
    out = re.sub(r"`([^`]+)`", code, out)

    def link(m):
        return lift(f'<a href="{html.escape(m.group(2))}" target="_blank" '
                    f'rel="noreferrer">') + m.group(1) + lift("</a>")
    out = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", link, out)

    # Emphasis, on text that now contains no tags at all — only sentinels.
    out = re.sub(r"\*\*(.+?)\*\*", lambda m: lift("<strong>") + m.group(1) + lift("</strong>"),
                 out, flags=re.S)
    out = re.sub(r"(?<![\w*\x00])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])",
                 lambda m: lift("<em>") + m.group(1) + lift("</em>"), out, flags=re.S)

    return re.sub(r"\x00(\d+)\x00", lambda m: lifted[int(m.group(1))], out)


def render_md(text: str, g: dict) -> str:
    """Paragraphs, headings, bullets and rules. Deliberately not a full markdown implementation."""
    parts = []
    for block in re.split(r"\n\s*\n", text.strip()):
        block = block.strip()
        if not block:
            continue
        if re.match(r"^-{3,}$", block):
            parts.append("<hr>")
            continue
        h = re.match(r"^(#{1,4})\s+(.*)$", block)
        if h:
            level = min(len(h.group(1)) + 1, 5)
            parts.append(f"<h{level}>{_inline(h.group(2), g)}</h{level}>")
            continue
        lines = block.splitlines()
        if all(re.match(r"^\s*[-*]\s+", ln) or ln.startswith("  ") for ln in lines) \
                and re.match(r"^\s*[-*]\s+", lines[0]):
            items, cur = [], ""
            for ln in lines:
                if re.match(r"^\s*[-*]\s+", ln):
                    if cur:
                        items.append(cur)
                    cur = re.sub(r"^\s*[-*]\s+", "", ln)
                else:
                    cur += " " + ln.strip()
            if cur:
                items.append(cur)
            parts.append("<ul>" + "".join(f"<li>{_inline(i, g)}</li>" for i in items) + "</ul>")
            continue
        parts.append(f"<p>{_inline(' '.join(ln.strip() for ln in lines), g)}</p>")
    return "\n".join(parts)


# ---------------------------------------------------------------------------------------------
# Reading the sources
# ---------------------------------------------------------------------------------------------

def feed_items() -> list[dict]:
    text = (BRAIN / "feed-items.md").read_text()
    items = []
    for chunk in re.split(r"\n(?=## FEED-)", text)[1:]:
        head, _, rest = chunk.partition("\n")
        m = re.match(r"##\s*FEED-(\d+)\s*·\s*(\S+)\s*·\s*(\S+)", head)
        if not m:
            continue
        item = {"id": f"FEED-{m.group(1)}", "n": int(m.group(1)),
                "date": m.group(2), "status": m.group(3), "keys": {}}
        title = re.match(r"\s*\*\*(.+?)\*\*\s*$", rest.split("\n")[0].strip() or "\n")
        lines = [ln for ln in rest.splitlines()]
        body_start = 0
        for i, ln in enumerate(lines):
            s = ln.strip()
            if not s:
                continue
            if title is None and s.startswith("**") and s.endswith("**"):
                title = re.match(r"\*\*(.+)\*\*", s)
                body_start = i + 1
                continue
            kv = re.match(r"^(owner|blocks|cost|options|answered):\s*(.*)$", s)
            if kv:
                item["keys"][kv.group(1)] = kv.group(2).strip()
                body_start = i + 1
                continue
            if title is not None and item["keys"]:
                break
        item["title"] = title.group(1) if title else item["id"]
        item["body"] = "\n".join(lines[body_start:]).strip()
        item["options"] = [o.strip() for o in item["keys"].get("options", "").split("|") if o.strip()]
        items.append(item)
    return sorted(items, key=lambda i: -i["n"])


def bar_conditions() -> tuple[str, list[dict]]:
    """The current stage's exit conditions, from the decision that owns them.

    The **text** is read from the decision — never retyped here, so it cannot drift from the decision.
    The **status** of each is a judgment, and it is read from `feed-items.md`'s `## BAR` block,
    which is the one place this tool asks to be told something rather than deriving it.
    """
    plan = (BRAIN / "plan.md").read_text()
    m = re.search(r"^## (Stage \d+ · [^\n]*?) — \*\*current\*\*", plan, re.M)
    stage = m.group(1) if m else "current stage"
    bar_ref = re.search(r"\*\*Bar: \[\[([^\]]+)\]\]", plan)
    conds = []
    if bar_ref:
        path = BRAIN / "decisions" / f"{bar_ref.group(1)}.md"
        if path.exists():
            body = path.read_text()
            dec = body.split("## Decision", 1)[-1].split("\n## ", 1)[0]
            for cm in re.finditer(r"^(\d)\.\s+\*\*(.+?)\*\*(.*?)(?=^\d\.\s+\*\*|\Z)",
                                  dec, re.M | re.S):
                conds.append({"n": cm.group(1), "claim": " ".join(cm.group(2).split()),
                              "detail": " ".join(cm.group(3).split())[:400], "status": "unknown"})
    status = {}
    block = re.search(r"^## BAR\s*\n(.*?)(?=^## |\Z)", (BRAIN / "feed-items.md").read_text(),
                      re.M | re.S)
    if block:
        for ln in block.group(1).splitlines():
            sm = re.match(r"^\s*(\d)\s*:\s*(met|not-met|partly)\s*·\s*(.*)$", ln.strip())
            if sm:
                status[sm.group(1)] = (sm.group(2), sm.group(3))
    for c in conds:
        if c["n"] in status:
            c["status"], c["evidence"] = status[c["n"]]
        else:
            c["evidence"] = ""
    return stage, conds


def comms() -> list[dict]:
    """The external thread from `comms/`, newest first — rendered only if the folder exists."""
    out = []
    for direction in ("outbound", "inbound"):
        folder = ROOT / "comms" / direction
        if not folder.exists():
            continue
        for path in folder.glob("*.md"):
            m = re.match(r"^(\d{4}-\d{2}-\d{2})-(.+)\.md$", path.name)
            if not m:
                continue
            first = ""
            for ln in path.read_text().splitlines():
                if ln.startswith("# "):
                    first = ln[2:].strip()
                    break
            title = re.sub(r"\*\*|`", "", first) or m.group(2).replace("-", " ")
            out.append({"date": m.group(1), "direction": direction, "path": path,
                        "title": title, "draft": "DRAFT" in path.name})
    return sorted(out, key=lambda c: c["date"], reverse=True)


def freshness() -> tuple[bool, list[str]]:
    if not OUT.exists():
        return False, ["feed.html does not exist"]
    age = OUT.stat().st_mtime
    stale = [s for s in SOURCES if (BRAIN / s).exists() and (BRAIN / s).stat().st_mtime > age]
    return not stale, stale


# ---------------------------------------------------------------------------------------------
# The graph — the brain as nodes, without requiring anything to be installed
# ---------------------------------------------------------------------------------------------
#
# The visualization question has an obvious wrong answer: emit a format only one app can read.
# A `.canvas` is trivial to write and, outside Obsidian, its `file` nodes are dead paths; every
# other viewer is either a cloud app (uploading a client's material) or an npm dependency. So
# the primary artifact is an **inline SVG in this page** — stdlib-only, self-contained, opens
# in any browser, nothing leaves the machine. The `.canvas` is written too, because it costs
# forty lines and hands a graph to anyone who does open `brain/` as a vault. Nothing depends
# on it.
#
# Layout is Fruchterman-Reingold with a golden-angle starting spiral and a fixed iteration
# count: **deterministic**, so regenerating the page produces the same picture and a diff means
# the brain changed, not that the simulation wobbled.

GRAPH_DIRS = ("decisions", "insights", "braindumps", "briefings")
KIND_OF = {"decisions": "decision", "insights": "insight",
           "braindumps": "braindump", "briefings": "briefing"}


def _frontmatter_tags(text: str) -> list:
    if not text.startswith("---"):
        return []
    end = text.find("\n---", 3)
    if end == -1:
        return []
    m = re.search(r"^tags:\s*\[(.*?)\]", text[3:end], re.M)
    if not m:
        return []
    return [t.strip().strip("\"'") for t in m.group(1).split(",") if t.strip()]


def graph_data() -> tuple:
    """Nodes are brain files plus one node per tag in use; edges are wiki-links between files
    and membership between a file and its tags.

    Tags are nodes rather than invisible grouping because a tag shared by a decision and an
    insight is the thing the owner asked to be able to see."""
    nodes, edges = [], []
    texts = {}
    for d in GRAPH_DIRS:
        folder = BRAIN / d
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.md")):
            if path.name == "README.md" or path.stem.startswith("0000"):
                continue
            texts[path] = path.read_text(encoding="utf-8")
            head = re.search(r"^#\s+(.+)$", texts[path], re.M)
            label = head.group(1).strip() if head else path.stem
            label = re.sub(r"^\d{4}\s*[—-]\s*", "", label)
            nodes.append({"id": path.stem, "label": label, "kind": KIND_OF[d],
                          "path": path, "tags": _frontmatter_tags(texts[path])})

    by_id = {n["id"]: n for n in nodes}
    numbered = {n["id"][:4]: n["id"] for n in nodes if re.match(r"^\d{4}-", n["id"])}

    for path, text in texts.items():
        src = path.stem
        seen = set()
        body = text
        for target in re.findall(r"\[\[([^\]|#]+?)\]\]", body):
            t = target.strip()
            t = numbered.get(t, t)
            if t in by_id and t != src:
                seen.add(t)
        for num, full in numbered.items():
            if full == src:
                continue
            if re.search(rf"(?<![\w-]){num}(?![\w-])", body):
                seen.add(full)
        for t in seen:
            edges.append({"a": src, "b": t, "kind": "link"})

    tag_use: dict = {}
    for n in nodes:
        for t in n["tags"]:
            tag_use.setdefault(t, []).append(n["id"])
    for tag, members in sorted(tag_use.items()):
        tid = f"tag:{tag}"
        nodes.append({"id": tid, "label": tag, "kind": "tag", "path": BRAIN / "tags.md",
                      "tags": []})
        for m in members:
            edges.append({"a": m, "b": tid, "kind": "tag"})

    deg: dict = {n["id"]: 0 for n in nodes}
    for e in edges:
        deg[e["a"]] = deg.get(e["a"], 0) + 1
        deg[e["b"]] = deg.get(e["b"], 0) + 1
    for n in nodes:
        n["deg"] = deg.get(n["id"], 0)
    return nodes, edges


def layout(nodes: list, edges: list, w: float = 900, h: float = 560) -> None:
    """Fruchterman-Reingold, deterministic. Sets x/y on each node in place."""
    n = len(nodes)
    if n == 0:
        return
    golden = math.pi * (3 - math.sqrt(5))
    for i, node in enumerate(nodes):
        r = (w / 2.6) * math.sqrt((i + 0.5) / n)
        node["x"] = w / 2 + r * math.cos(i * golden)
        node["y"] = h / 2 + r * math.sin(i * golden)
    if n == 1:
        return

    idx = {node["id"]: i for i, node in enumerate(nodes)}
    pairs = [(idx[e["a"]], idx[e["b"]]) for e in edges if e["a"] in idx and e["b"] in idx]
    k = math.sqrt((w * h) / n)
    temp = w / 8
    iters = 260
    for step in range(iters):
        dx = [0.0] * n
        dy = [0.0] * n
        for i in range(n):
            for j in range(i + 1, n):
                ddx = nodes[i]["x"] - nodes[j]["x"]
                ddy = nodes[i]["y"] - nodes[j]["y"]
                d2 = ddx * ddx + ddy * ddy
                if d2 < 0.01:
                    ddx, ddy, d2 = 0.1 * (i - j + 1), 0.1, 0.02
                force = (k * k) / d2
                dx[i] += ddx * force
                dy[i] += ddy * force
                dx[j] -= ddx * force
                dy[j] -= ddy * force
        for a, b in pairs:
            ddx = nodes[a]["x"] - nodes[b]["x"]
            ddy = nodes[a]["y"] - nodes[b]["y"]
            d = math.hypot(ddx, ddy) or 0.01
            force = (d * d) / k / d
            dx[a] -= ddx * force
            dy[a] -= ddy * force
            dx[b] += ddx * force
            dy[b] += ddy * force
        for i, node in enumerate(nodes):
            d = math.hypot(dx[i], dy[i]) or 1.0
            node["x"] += dx[i] / d * min(d, temp)
            node["y"] += dy[i] / d * min(d, temp)
            # A weak pull to centre keeps disconnected islands from drifting off the canvas.
            node["x"] += (w / 2 - node["x"]) * 0.012
            node["y"] += (h / 2 - node["y"]) * 0.012
        temp = max(temp * 0.955, 0.6)

    # Rotate the settled cloud so its widest spread runs horizontally. A force layout has no
    # preferred orientation, so without this the same graph lands portrait or landscape at
    # random-looking whim — and a page 900 wide by 660 tall wants landscape. Principal axis
    # via the covariance matrix; deterministic, and it changes nothing about the topology.
    cx = sum(node["x"] for node in nodes) / n
    cy = sum(node["y"] for node in nodes) / n
    sxx = sum((node["x"] - cx) ** 2 for node in nodes)
    syy = sum((node["y"] - cy) ** 2 for node in nodes)
    sxy = sum((node["x"] - cx) * (node["y"] - cy) for node in nodes)
    theta = 0.5 * math.atan2(2 * sxy, sxx - syy)
    cos_t, sin_t = math.cos(-theta), math.sin(-theta)
    for node in nodes:
        ox, oy = node["x"] - cx, node["y"] - cy
        node["x"] = cx + ox * cos_t - oy * sin_t
        node["y"] = cy + ox * sin_t + oy * cos_t


def graph_svg(nodes: list, edges: list, g: dict) -> str:
    """Inline SVG. Node anchors carry the same `data-*` attributes as a prose reference, so the
    page's existing tooltip and click-to-open handlers work on the graph for free."""
    if not nodes:
        return ('<p style="font-size:13.5px;color:var(--dim);margin:0">Nothing to draw yet — '
                'the graph fills in as decisions, insights and tags accumulate.</p>')
    # Scale to fill the width, then let the viewBox height follow the content's own aspect.
    # A force layout settles into a roughly circular blob; fitting it into a fixed rectangle
    # leaves dead space that reads as a drawing error rather than as a graph drawn to fit.
    W, pad, H_MAX = 900, 46, 660
    xs = [n["x"] for n in nodes]
    ys = [n["y"] for n in nodes]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    span_x, span_y = max(maxx - minx, 1), max(maxy - miny, 1)
    sc = (W - 2 * pad) / span_x
    if span_y * sc + 2 * pad > H_MAX:
        sc = (H_MAX - 2 * pad) / span_y
    H = round(span_y * sc + 2 * pad)
    offx = (W - span_x * sc) / 2
    offy = (H - span_y * sc) / 2
    for n in nodes:
        n["px"] = offx + (n["x"] - minx) * sc
        n["py"] = offy + (n["y"] - miny) * sc

    pos = {n["id"]: (n["px"], n["py"]) for n in nodes}
    out = [f'<svg class="graph" viewBox="0 0 {W} {H}" role="img" '
           f'aria-label="the brain as a graph of {len(nodes)} notes and tags">']
    for e in edges:
        if e["a"] not in pos or e["b"] not in pos:
            continue
        x1, y1 = pos[e["a"]]
        x2, y2 = pos[e["b"]]
        cls = "e-tag" if e["kind"] == "tag" else "e-link"
        out.append(f'<line class="{cls}" x1="{x1:.1f}" y1="{y1:.1f}" '
                   f'x2="{x2:.1f}" y2="{y2:.1f}"/>')
    # Labels, placed so they do not collide. A force layout puts nodes where the forces want
    # them, not where two captions both fit, and overlapping text is the difference between a
    # diagram and a mess. Highest-degree nodes claim their spot first; a label with nowhere to
    # go is dropped rather than drawn on top of another.
    placed: list = []

    def fits(cx_: float, cy_: float, text: str) -> bool:
        w2 = len(text) * 2.35 + 3
        box = (cx_ - w2, cy_ - 6, cx_ + w2, cy_ + 5)
        for b in placed:
            if not (box[2] < b[0] or box[0] > b[2] or box[3] < b[1] or box[1] > b[3]):
                return False
        placed.append(box)
        return True

    show_all = len(nodes) <= 44
    for n in sorted(nodes, key=lambda z: -z["deg"]):
        r = 5.0 + min(n["deg"], 9) * 1.15
        label = n["label"] if len(n["label"]) <= 24 else n["label"][:23].rstrip(" ,;:") + "…"
        entry = g.get(n["id"])
        attrs = ""
        if entry:
            attrs = (f' class="ref gnode {n["kind"]}"'
                     f' href="{html.escape(str(entry["path"]))}"'
                     f' data-title="{html.escape(entry["title"])}"'
                     f' data-kind="{html.escape(entry["kind"])}"'
                     f' data-note="{html.escape(entry.get("note", ""))}"'
                     f' data-gloss="{html.escape(entry["gloss"])}"'
                     f' data-path="{html.escape(str(entry["path"].relative_to(ROOT)))}"')
        elif n["kind"] == "tag":
            members = sum(1 for e in edges if e["kind"] == "tag" and e["b"] == n["id"])
            attrs = (f' class="ref gnode tag" href="{html.escape(str(BRAIN / "tags.md"))}"'
                     f' data-title="{html.escape(n["label"])}" data-kind="tag"'
                     f' data-note="{members} file(s)"'
                     f' data-gloss="A theme shared across the brain. Defined in tags.md."'
                     f' data-path="brain/tags.md"')
        else:
            attrs = (f' class="ref gnode {n["kind"]}"'
                     f' href="{html.escape(str(n["path"]))}"'
                     f' data-title="{html.escape(n["label"])}"'
                     f' data-kind="{n["kind"]}" data-note=""'
                     f' data-gloss="{html.escape(_first_para(n["path"].read_text()))}"'
                     f' data-path="{html.escape(str(n["path"].relative_to(ROOT)))}"')
        out.append(f'<a{attrs}>')
        if n["kind"] == "tag":
            out.append(f'<rect class="n-{n["kind"]}" x="{n["px"] - r:.1f}" '
                       f'y="{n["py"] - r:.1f}" width="{2 * r:.1f}" height="{2 * r:.1f}" '
                       f'rx="2.5" transform="rotate(45 {n["px"]:.1f} {n["py"]:.1f})"/>')
        else:
            out.append(f'<circle class="n-{n["kind"]}" cx="{n["px"]:.1f}" '
                       f'cy="{n["py"]:.1f}" r="{r:.1f}"/>')
        if show_all or n["deg"] >= 3 or n["kind"] == "tag":
            below, above = n["py"] + r + 10, n["py"] - r - 5
            ly = below if fits(n["px"], below, label) else (
                above if fits(n["px"], above, label) else None)
            if ly is not None:
                out.append(f'<text class="l-{n["kind"]}" x="{n["px"]:.1f}" '
                           f'y="{ly:.1f}">{html.escape(label)}</text>')
        out.append("</a>")
    out.append("</svg>")

    counts = Counter(n["kind"] for n in nodes)
    legend = " · ".join(f'<span class="lg {k}">{counts[k]} {k}{"s" if counts[k] != 1 else ""}</span>'
                        for k in ("decision", "insight", "braindump", "briefing", "tag")
                        if counts.get(k))
    links = sum(1 for e in edges if e["kind"] == "link")
    return (f'<div class="legend">{legend} · '
            f'<span class="lg">{links} link{"s" if links != 1 else ""}</span></div>'
            + "".join(out))


def write_canvas(nodes: list, edges: list) -> int:
    """Also emit `brain/brain.canvas` (JSON Canvas 1.0) — for anyone who opens `brain/` as an
    Obsidian vault. Optional by construction: nothing reads it back, and deleting it changes
    nothing. Ids are md5-derived so they are stable across runs."""
    if not nodes:
        return 0

    def nid(key: str) -> str:
        return hashlib.md5(key.encode()).hexdigest()[:16]

    cnodes, cedges = [], []
    for n in nodes:
        if n["kind"] == "tag":
            cnodes.append({"id": nid(n["id"]), "type": "text",
                           "text": f"#{n['label']}", "x": int(n["x"] * 2.2),
                           "y": int(n["y"] * 2.2), "width": 180, "height": 60,
                           "color": "5"})
        else:
            cnodes.append({"id": nid(n["id"]), "type": "file",
                           "file": str(n["path"].relative_to(BRAIN)),
                           "x": int(n["x"] * 2.2), "y": int(n["y"] * 2.2),
                           "width": 320, "height": 120})
    ids = {c["id"] for c in cnodes}
    for e in edges:
        a, b = nid(e["a"]), nid(e["b"])
        if a not in ids or b not in ids:
            continue          # never emit a dangling fromNode/toNode
        cedges.append({"id": nid(e["a"] + "->" + e["b"]), "fromNode": a, "fromSide": "right",
                       "toNode": b, "toSide": "left"})
    assert len({c["id"] for c in cnodes}) == len(cnodes), "duplicate canvas node id"
    (BRAIN / "brain.canvas").write_text(
        json.dumps({"nodes": cnodes, "edges": cedges}, indent=1), encoding="utf-8")
    return len(cnodes)



# ---------------------------------------------------------------------------------------------
# The page
# ---------------------------------------------------------------------------------------------

CSS = """
*,*::before,*::after{box-sizing:border-box}
:root{
  --bg:#fbfaf8; --panel:#fff; --ink:#1a1a1a; --dim:#6b6b6b; --faint:#8f8f8f;
  --line:#e6e3dd; --accent:#7a5cff; --accent-soft:#efeaff;
  --warn:#b4531a; --warn-soft:#fdf0e6; --ok:#2f7a4f; --ok-soft:#e9f5ee;
  --shadow:0 1px 2px rgba(0,0,0,.05),0 8px 24px rgba(0,0,0,.05);
  --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#131316; --panel:#1a1a1f; --ink:#eceaf2; --dim:#a2a0ab; --faint:#807e8a;
  --line:#2c2c34; --accent:#a78bfa; --accent-soft:#2a2340;
  --warn:#f0a06a; --warn-soft:#3a2618; --ok:#7fd6a4; --ok-soft:#16301f;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px rgba(0,0,0,.35);
}}
:root[data-theme="dark"]{
  --bg:#131316; --panel:#1a1a1f; --ink:#eceaf2; --dim:#a2a0ab; --faint:#807e8a;
  --line:#2c2c34; --accent:#a78bfa; --accent-soft:#2a2340;
  --warn:#f0a06a; --warn-soft:#3a2618; --ok:#7fd6a4; --ok-soft:#16301f;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px rgba(0,0,0,.35);
}
body{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.62 ui-serif,Georgia,"Iowan Old Style",serif;
  -webkit-font-smoothing:antialiased}
.wrap{max-width:820px;margin:0 auto;padding:32px 20px 120px}
h1,h2,h3,h4,h5{font-family:ui-sans-serif,-apple-system,"Segoe UI",system-ui,sans-serif;
  line-height:1.25;margin:0 0 .4em}
h1{font-size:26px;letter-spacing:-.02em}
h3{font-size:19px;letter-spacing:-.01em}
h4{font-size:16px}
h5{font-size:14px;color:var(--dim)}
p{margin:0 0 .85em}
ul{margin:0 0 .9em;padding-left:1.15em}
li{margin:.25em 0}
code{font-family:var(--mono);font-size:.86em;background:var(--accent-soft);
  padding:.08em .34em;border-radius:4px;word-break:break-word}
hr{border:0;border-top:1px solid var(--line);margin:1.4em 0}
a{color:inherit}
.kicker{font-family:ui-sans-serif,system-ui,sans-serif;font-size:11px;font-weight:600;
  letter-spacing:.1em;text-transform:uppercase;color:var(--faint);margin:0 0 10px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:14px;
  padding:22px 24px;margin:0 0 20px;box-shadow:var(--shadow)}
.panel.tight{padding:16px 20px}

/* ── top bar ─────────────────────────────────────────────────────────── */
.top{display:flex;align-items:baseline;justify-content:space-between;gap:14px;
  flex-wrap:wrap;margin-bottom:22px}
.top .meta{font-family:ui-sans-serif,system-ui,sans-serif;font-size:12px;color:var(--faint)}
.pill{display:inline-block;font-family:ui-sans-serif,system-ui,sans-serif;font-size:11px;
  font-weight:600;padding:3px 9px;border-radius:999px;background:var(--accent-soft);
  color:var(--accent);letter-spacing:.02em}
.pill.warn{background:var(--warn-soft);color:var(--warn)}
.pill.ok{background:var(--ok-soft);color:var(--ok)}
button{font:inherit;font-family:ui-sans-serif,system-ui,sans-serif;cursor:pointer}

/* ── stage strip ─────────────────────────────────────────────────────── */
.stages{display:flex;gap:6px;margin:2px 0 18px;flex-wrap:wrap}
.stage{flex:1 1 90px;min-width:90px;padding:8px 10px;border-radius:9px;border:1px solid var(--line);
  background:var(--panel);font-family:ui-sans-serif,system-ui,sans-serif;font-size:11.5px;
  color:var(--faint);text-align:center}
.stage.done{background:var(--ok-soft);color:var(--ok);border-color:transparent}
.stage.here{background:var(--accent);color:#fff;border-color:transparent;font-weight:600;
  box-shadow:var(--shadow)}
.cond{display:flex;gap:11px;padding:11px 0;border-top:1px solid var(--line);align-items:flex-start}
.cond:first-of-type{border-top:0}
.cond .dot{flex:0 0 auto;width:19px;height:19px;border-radius:50%;margin-top:2px;
  font-family:ui-sans-serif,system-ui,sans-serif;font-size:11px;font-weight:700;
  display:grid;place-items:center;background:var(--line);color:var(--dim)}
.cond.met .dot{background:var(--ok);color:#fff}
.cond.partly .dot{background:var(--warn);color:#fff}
.cond .claim{font-size:14.5px}
.cond .ev{font-family:ui-sans-serif,system-ui,sans-serif;font-size:12.5px;color:var(--dim);
  margin-top:3px}
.cond .more{font-size:13.5px;color:var(--dim);margin-top:6px;display:none}
.cond.open .more{display:block}
.cond .claim{cursor:pointer}

/* ── the graph ───────────────────────────────────────────────────────── */
svg.graph{display:block;width:100%;height:auto;overflow:visible;touch-action:pan-y}
svg.graph line{stroke:var(--line)}
svg.graph line.e-link{stroke-width:1.5;stroke:var(--faint);opacity:.7}
svg.graph line.e-tag{stroke-width:1.1;stroke:var(--accent);stroke-dasharray:2 4;opacity:.5}
svg.graph .n-decision{fill:var(--accent)}
svg.graph .n-insight{fill:var(--ok)}
svg.graph .n-braindump{fill:var(--warn)}
svg.graph .n-briefing{fill:var(--dim)}
svg.graph .n-tag{fill:none;stroke:var(--faint);stroke-width:1.6}
svg.graph text{font-family:ui-sans-serif,system-ui,sans-serif;font-size:9.5px;
  text-anchor:middle;fill:var(--dim);pointer-events:none}
svg.graph text.l-tag{fill:var(--faint);font-size:9px;letter-spacing:.04em;text-transform:uppercase}
svg.graph a.gnode{cursor:pointer}
svg.graph a.gnode:hover circle,svg.graph a.gnode:hover rect{stroke:var(--ink);stroke-width:2}
svg.graph a.gnode:hover text{fill:var(--ink)}
.legend{display:flex;flex-wrap:wrap;gap:10px;margin:-2px 0 8px;
  font-family:ui-sans-serif,system-ui,sans-serif;font-size:11.5px;color:var(--dim)}
.legend .lg{display:inline-flex;align-items:center;gap:5px}
.legend .lg::before{content:"";width:8px;height:8px;border-radius:50%;background:var(--line)}
.legend .lg.decision::before{background:var(--accent)}
.legend .lg.insight::before{background:var(--ok)}
.legend .lg.braindump::before{background:var(--warn)}
.legend .lg.briefing::before{background:var(--dim)}
.legend .lg.tag::before{background:transparent;border:1.5px solid var(--faint);
  border-radius:1px;transform:rotate(45deg);width:7px;height:7px}

/* ── feed cards ──────────────────────────────────────────────────────── */
.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;
  padding:20px 22px;margin:0 0 16px;box-shadow:var(--shadow);position:relative}
.card.answered{opacity:.6}
.card.answered:hover{opacity:1}
/* A settled item folds to its title and its answer. Live ones are open, and can still be
   folded away by hand. */
details.fold>summary{font-family:ui-sans-serif,system-ui,sans-serif;font-size:12.5px;
  color:var(--dim);cursor:pointer;list-style:none;padding:2px 0 8px}
details.fold>summary::-webkit-details-marker{display:none}
details.fold>summary::before{content:"▸ ";color:var(--accent)}
details.fold[open]>summary::before{content:"▾ "}
details.fold[open]>summary{color:var(--faint)}
.card .cardhead{display:flex;gap:10px;align-items:baseline;flex-wrap:wrap;margin-bottom:6px}
.card .idtag{font-family:var(--mono);font-size:11px;color:var(--faint)}
.card h3{margin:0 0 10px}
.facts{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 14px}
.fact{font-family:ui-sans-serif,system-ui,sans-serif;font-size:11.5px;color:var(--dim);
  background:var(--bg);border:1px solid var(--line);border-radius:7px;padding:3px 9px}
.fact b{color:var(--ink);font-weight:600}
.body{font-size:15px}
.body p:last-child{margin-bottom:0}
details.body-more>summary{font-family:ui-sans-serif,system-ui,sans-serif;font-size:12.5px;
  color:var(--accent);cursor:pointer;list-style:none;padding:4px 0;font-weight:600}
details.body-more>summary::-webkit-details-marker{display:none}
details.body-more>summary::before{content:"▸ ";display:inline-block;transition:transform .15s}
details.body-more[open]>summary::before{content:"▾ "}

/* ── answering ───────────────────────────────────────────────────────── */
.answer{margin-top:15px;padding-top:14px;border-top:1px dashed var(--line)}
.opts{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:9px}
.opt{border:1px solid var(--line);background:var(--panel);color:var(--ink);
  border-radius:9px;padding:7px 13px;font-size:13.5px;transition:.12s}
.opt:hover{border-color:var(--accent);color:var(--accent)}
.opt.picked{background:var(--accent);border-color:var(--accent);color:#fff;font-weight:600}
textarea{width:100%;min-height:52px;resize:vertical;font:14px/1.5 ui-sans-serif,system-ui,sans-serif;
  color:var(--ink);background:var(--bg);border:1px solid var(--line);border-radius:9px;
  padding:9px 11px}
textarea:focus{outline:2px solid var(--accent);outline-offset:-1px;border-color:transparent}
.saved{font-family:ui-sans-serif,system-ui,sans-serif;font-size:11.5px;color:var(--ok);
  margin-top:6px;height:14px}

/* ── reference tooltips ──────────────────────────────────────────────── */
a.ref{color:var(--accent);text-decoration:none;border-bottom:1px dotted var(--accent);
  cursor:help}
a.ref:hover{background:var(--accent-soft)}
span.ref.dead{color:var(--dim);border-bottom:1px dotted var(--dim)}
a.path{color:var(--accent);text-decoration:none}
a.path:hover code{outline:1px solid var(--accent)}
#tip{position:fixed;z-index:99;max-width:400px;background:var(--panel);color:var(--ink);
  border:1px solid var(--line);border-radius:11px;padding:13px 15px;box-shadow:var(--shadow);
  font:13.5px/1.5 ui-sans-serif,system-ui,sans-serif;display:none;pointer-events:none}
#tip .k{font-size:10.5px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
  color:var(--accent);margin-bottom:3px}
#tip .t{font-weight:600;margin-bottom:5px;font-size:14px}
#tip .n{font-size:11.5px;color:var(--faint);margin-bottom:6px}
#tip .g{color:var(--dim)}
#tip .open{margin-top:8px;font-size:11.5px;color:var(--faint)}

/* ── comms ───────────────────────────────────────────────────────────── */
.thread{display:flex;gap:11px;padding:9px 0;border-top:1px solid var(--line);
  font-family:ui-sans-serif,system-ui,sans-serif;font-size:13px;align-items:baseline}
.thread:first-of-type{border-top:0}
.thread .d{flex:0 0 78px;color:var(--faint);font-size:11.5px;font-variant-numeric:tabular-nums}
.thread .dir{flex:0 0 62px;font-size:10.5px;font-weight:700;letter-spacing:.06em;
  text-transform:uppercase}
.thread .dir.out{color:var(--accent)}
.thread .dir.in{color:var(--ok)}
.thread a{text-decoration:none}
.thread a:hover{text-decoration:underline}

/* ── sticky footer ───────────────────────────────────────────────────── */
.dock{position:fixed;left:0;right:0;bottom:0;background:var(--panel);
  border-top:1px solid var(--line);padding:11px 20px;display:flex;gap:12px;
  align-items:center;justify-content:center;flex-wrap:wrap;box-shadow:0 -4px 20px rgba(0,0,0,.06)}
.dock .count{font-family:ui-sans-serif,system-ui,sans-serif;font-size:13px;color:var(--dim)}
.dock button{border-radius:9px;padding:8px 15px;font-size:13.5px;border:1px solid var(--line);
  background:var(--panel);color:var(--ink)}
.dock button.primary{background:var(--accent);border-color:var(--accent);color:#fff;font-weight:600}
.dock button:disabled{opacity:.45;cursor:not-allowed}
.nowbody{font-size:15px}
.nowbody h2,.nowbody h3{font-size:13px;text-transform:uppercase;letter-spacing:.08em;
  color:var(--faint);margin-top:1.3em}
@media (max-width:560px){.wrap{padding:20px 14px 130px}.thread .d{flex-basis:64px}}
"""

JS = """
const KEY='workspace-feed-v1';
const store=JSON.parse(localStorage.getItem(KEY)||'{}');
const save=()=>localStorage.setItem(KEY,JSON.stringify(store));

document.querySelectorAll('.card[data-id]').forEach(card=>{
  const id=card.dataset.id, rec=store[id]||{};
  card.querySelectorAll('.opt').forEach(b=>{
    if(rec.pick===b.dataset.opt) b.classList.add('picked');
    b.addEventListener('click',()=>{
      const was=b.classList.contains('picked');
      card.querySelectorAll('.opt').forEach(x=>x.classList.remove('picked'));
      if(!was){b.classList.add('picked');rec.pick=b.dataset.opt;}else{delete rec.pick;}
      store[id]=rec;save();flash(card);tally();
    });
  });
  const ta=card.querySelector('textarea');
  if(ta){
    ta.value=rec.note||'';
    ta.addEventListener('input',()=>{rec.note=ta.value;store[id]=rec;save();tally();});
    ta.addEventListener('blur',()=>flash(card));
  }
});
function flash(card){
  const s=card.querySelector('.saved'); if(!s) return;
  s.textContent='saved in this browser'; setTimeout(()=>s.textContent='',1600);
}
function answered(){
  return Object.entries(store).filter(([k,v])=>v&&(v.pick||(v.note||'').trim()));
}
function tally(){
  const n=answered().length;
  document.getElementById('count').textContent =
    n? `${n} answered — not sent yet` : 'nothing answered yet';
  document.getElementById('copy').disabled = n===0;
}
document.getElementById('copy').addEventListener('click',async()=>{
  const lines=['Answers from the feed:',''];
  answered().forEach(([id,v])=>{
    const card=document.querySelector(`.card[data-id="${id}"]`);
    lines.push(`**${id} — ${card?card.dataset.title:''}**`);
    if(v.pick) lines.push(`- ${v.pick}`);
    if((v.note||'').trim()) lines.push(`- ${v.note.trim()}`);
    lines.push('');
  });
  const text=lines.join('\\n');
  try{ await navigator.clipboard.writeText(text); }
  catch(e){ const t=document.createElement('textarea');t.value=text;document.body.append(t);
            t.select();document.execCommand('copy');t.remove(); }
  const b=document.getElementById('copy'); const old=b.textContent;
  b.textContent='copied — paste it to me'; setTimeout(()=>b.textContent=old,2200);
});
document.getElementById('clear').addEventListener('click',()=>{
  if(!confirm('Clear every answer stored in this browser?'))return;
  localStorage.removeItem(KEY);location.reload();
});
tally();

/* conditions expand */
document.querySelectorAll('.cond .claim').forEach(c=>{
  c.addEventListener('click',()=>c.closest('.cond').classList.toggle('open'));
});

/* reference tooltips — hover on a pointer, tap on touch */
const tip=document.getElementById('tip');
let pinned=null;
function show(a){
  tip.innerHTML=`<div class="k">${a.dataset.kind}</div>
    <div class="t">${a.dataset.title}</div>
    ${a.dataset.note?`<div class="n">${a.dataset.note}</div>`:''}
    <div class="g">${a.dataset.gloss||'(no summary in the file)'}</div>
    <div class="open">click to open ${a.dataset.path}</div>`;
  tip.style.display='block';
  const r=a.getBoundingClientRect(), t=tip.getBoundingClientRect();
  let left=Math.min(Math.max(8,r.left),innerWidth-t.width-8);
  let top=r.bottom+9; if(top+t.height>innerHeight-8) top=Math.max(8,r.top-t.height-9);
  tip.style.left=left+'px'; tip.style.top=top+'px';
}
function hide(){ if(!pinned) tip.style.display='none'; }
document.querySelectorAll('a.ref').forEach(a=>{
  a.addEventListener('mouseenter',()=>show(a));
  a.addEventListener('mouseleave',hide);
  a.addEventListener('click',e=>{
    if(matchMedia('(hover:hover)').matches) return;   /* pointer devices follow the link */
    e.preventDefault();
    if(pinned===a){pinned=null;tip.style.display='none';}else{pinned=a;show(a);}
  });
});
document.addEventListener('click',e=>{
  if(pinned&&!e.target.closest('a.ref')){pinned=null;tip.style.display='none';}
});
"""


def build() -> str:
    g = glossary()
    items = feed_items()
    stage, conds = bar_conditions()
    thread = comms()
    now_md = (BRAIN / "now.md").read_text()
    now_md = re.sub(r"^# Now\s*\n", "", now_md)
    now_md = re.sub(r"^\*20.*?\*\s*$", "", now_md, count=1, flags=re.M | re.S)

    waiting = [i for i in items if i["status"] == "awaiting-you"]
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    plan_text = (BRAIN / "plan.md").read_text()
    stages = []
    for m in re.finditer(r"^## (Stage (\d+) · [^—\n]+?) — \*?\*?(.+?)\*?\*?\s*$", plan_text, re.M):
        label, num, state = m.group(1), m.group(2), m.group(3)
        cls = "here" if "current" in state else ("done" if "exited" in state else "")
        short = label.split("·", 1)[1].strip() if "·" in label else label
        stages.append(f'<div class="stage {cls}" title="{html.escape(state)}">'
                      f'<b>{num}</b> · {html.escape(short)}</div>')

    out = [f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Feed — {PROJECT_NAME}</title><style>{CSS}</style></head><body>
<div id="tip"></div>
<div class="wrap">
<div class="top">
  <div><div class="kicker">{PROJECT_NAME} · decision feed</div>
       <h1>Where we are, and what is waiting on you</h1></div>
  <div class="meta">generated {stamp}<br>from brain/*.md — regenerate with
    <code>python3 brain/feed.py</code></div>
</div>

<div class="stages">{''.join(stages)}</div>
"""]

    # ── now ──────────────────────────────────────────────────────────────────────────────────
    out.append('<div class="panel"><div class="kicker">now.md · the one-screen state</div>'
               f'<div class="nowbody">{render_md(now_md, g)}</div></div>')

    # ── the bar ──────────────────────────────────────────────────────────────────────────────
    if conds:
        met = sum(1 for c in conds if c["status"] == "met")
        rows = []
        for c in conds:
            cls = c["status"] if c["status"] in ("met", "partly") else ""
            mark = "✓" if c["status"] == "met" else ("~" if c["status"] == "partly" else c["n"])
            rows.append(
                f'<div class="cond {cls}"><div class="dot">{mark}</div><div>'
                f'<div class="claim">{_inline(c["claim"], g)}</div>'
                + (f'<div class="ev">{_inline(c["evidence"], g)}</div>' if c["evidence"] else "")
                + f'<div class="more">{_inline(c["detail"], g)}</div></div></div>')
        out.append(
            '<div class="panel"><div class="kicker">what has to be true to leave '
            f'{html.escape(stage.split("·")[0].strip())} '
            f'<span class="pill {"ok" if met == len(conds) else "warn"}">{met} of {len(conds)}'
            '</span></div>'
            '<p style="font-size:13.5px;color:var(--dim);margin:-2px 0 10px">'
            'Tap a condition for the full wording from the decision that owns it.</p>'
            + "".join(rows) + '</div>')

    # ── the graph ────────────────────────────────────────────────────────────────────────────
    gnodes, gedges = graph_data()
    layout(gnodes, gedges)          # once; graph_svg and write_canvas share the result
    write_canvas(gnodes, gedges)
    out.append('<div class="panel"><div class="kicker">the brain · '
               f'{len(gnodes)} note(s) and tag(s), how they connect</div>'
               '<p style="font-size:13.5px;color:var(--dim);margin:-2px 0 10px">'
               'Solid lines are links between notes; dashed lines are a shared tag. '
               'Hover a node for what it says, click to open the file.</p>'
               + graph_svg(gnodes, gedges, g) + '</div>')

    # ── the feed ─────────────────────────────────────────────────────────────────────────────
    out.append(f'<div class="kicker" style="margin:30px 0 12px">the feed · '
               f'{len(waiting)} waiting on you</div>')
    for item in items:
        k = item["keys"]
        facts = []
        if k.get("blocks"):
            facts.append(f'<span class="fact"><b>blocks</b> {_inline(k["blocks"], g)}</span>')
        if k.get("cost"):
            facts.append(f'<span class="fact"><b>costs you</b> {_inline(k["cost"], g)}</span>')
        facts.append(f'<span class="fact"><b>raised</b> {item["date"]}</span>')
        opts = "".join(
            f'<button class="opt" data-opt="{html.escape(o)}">{html.escape(o)}</button>'
            for o in item["options"])
        answered_pill = ('<span class="pill ok">answered</span>' if item["status"] == "answered"
                         else '<span class="pill warn">awaiting you</span>')
        body = render_md(item["body"], g)
        # The first paragraph is always visible; the rest folds away. Scanning is the whole point —
        # the argument has to be one click from the question, not in front of it.
        first, _, rest = body.partition("</p>")
        lead = first + "</p>" if rest else body
        more = (f'<details class="body-more"><summary>the reasoning</summary>{rest}</details>'
                if rest.strip() else "")
        # A whole settled item folds too, and starts folded. What is waiting on the owner is
        # the only thing the page opens by itself — everything else is history, and history
        # that is open by default pushes the live question below the fold.
        live = item["status"] == "awaiting-you"
        if live:
            fold_label = "the detail"
        else:
            given = k.get("answered", "").strip()
            fold_label = (f"you said: {given}" if given
                          else f"{item['status']} · open it")
        out.append(f"""<div class="card{'' if live else ' answered'}"
  data-id="{item['id']}" data-title="{html.escape(item['title'])}">
  <div class="cardhead"><span class="idtag">{item['id']}</span>{answered_pill}</div>
  <h3>{_inline(item['title'], g)}</h3>
  <details class="fold"{' open' if live else ''}>
  <summary>{_inline(fold_label, g)}</summary>
  <div class="facts">{''.join(facts)}</div>
  <div class="body">{lead}{more}</div>
  <div class="answer">
    <div class="opts">{opts}</div>
    <textarea placeholder="…or say it in your own words"></textarea>
    <div class="saved"></div>
  </div>
  </details>
</div>""")

    # ── the client thread ────────────────────────────────────────────────────────────────────
    if thread:
        rows = []
        today = date.today()
        for c in thread[:9]:
            days = (today - date.fromisoformat(c["date"])).days
            tag = "out" if c["direction"] == "outbound" else "in"
            draft = ' <span class="pill warn">draft, unsent</span>' if c["draft"] else ""
            rows.append(
                f'<div class="thread"><div class="d">{c["date"]}</div>'
                f'<div class="dir {tag}">{tag}</div>'
                f'<div><a href="{html.escape(str(c["path"]))}">{html.escape(c["title"])}</a>'
                f'{draft} <span style="color:var(--faint)">· {days}d ago</span></div></div>')
        out.append('<div class="panel"><div class="kicker">the thread · newest first</div>'
                   + "".join(rows) + '</div>')

    out.append(f"""</div>
<div class="dock">
  <span class="count" id="count"></span>
  <button class="primary" id="copy" disabled>Copy my answers</button>
  <button id="clear">Clear</button>
</div>
<script>{JS}</script></body></html>""")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--open", action="store_true")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if the page is older than the files it projects")
    args = ap.parse_args()

    if args.check:
        fresh, stale = freshness()
        print("feed.html is current" if fresh
              else "feed.html is STALE — regenerate: " + ", ".join(stale))
        return 0 if fresh else 1

    OUT.write_text(build())
    items = feed_items()
    waiting = [i for i in items if i["status"] == "awaiting-you"]
    nodes, _ = graph_data()
    canvas = BRAIN / "brain.canvas"
    print(f"{OUT.relative_to(ROOT)}  ·  {len(items)} item(s), {len(waiting)} awaiting you"
          f"  ·  {len(glossary())} glossary entries  ·  {len(nodes)} graph node(s)"
          + (f"  ·  {canvas.relative_to(ROOT)}" if canvas.exists() else ""))
    if args.open:
        subprocess.run(["open", str(OUT)], check=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
