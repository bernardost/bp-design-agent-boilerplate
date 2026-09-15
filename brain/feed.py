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
workspace is dense with references — `[[a-decision-slug]]`, `Q9`, `PROJ-7`, `[[an-insight-slug]]` — and each one
is a file the reader has to go and find. The compression is right for the record and wrong for a
person scanning it. So the glossary is built from the files themselves and every reference on the
page carries its own definition on hover and its own link on click. **Nothing here is a summary
someone maintains**; if a decision's title changes, the tooltip changes with it.

Dependency-free, matching the rest of the tree: no packages, no build step. The one network
request is the webfont stylesheet — Inter and IBM Plex Mono, which fall back to the system
stack offline; set `FONT_LINK = ""` to remove even that. The page is a local file rather than
anything hosted: it may carry confidential project facts, and `file://` links into the repo only
resolve from a local page anyway.
"""

import argparse
import hashlib
import html
import math
import json
import os
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
from config import (  # noqa: E402
    PROJECT_NAME, TRACKER_PREFIX, MULTI_PROJECT, PROJECT_KEYS, PROJECT_LABEL,
)

_KEY = rf"{TRACKER_PREFIX}-\d+" if TRACKER_PREFIX else r"(?!x)x"   # never-matching if None

FONT_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link rel="stylesheet" referrerpolicy="no-referrer" '
    'href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&'
    'family=IBM+Plex+Mono:wght@400;500&display=swap">'
)

SOURCES = ("now.md", "plan.md", "tasks.md", "feed-items.md", "open-questions.md",
           "tags.md", "glossary.md")


# ---------------------------------------------------------------------------------------------
# Citations — where a claim came from, one hover away and never in the sentence's way
# ---------------------------------------------------------------------------------------------
#
# The brain's source tag, written inline in any markdown file:
#
#     The client wants SSO before launch. ^[Dana · kickoff call · 2026-08-11 14:20](https://meetings…)
#     The roster is stale. ^[Ravi · #client-portal · 2026-08-28]
#     Two more workstreams are coming. ^[inferred]
#
# It renders as a superscript numeral, which is the entire point: `AGENTS.md` requires every
# claim about what a client said to carry who said it and when, and a brief that prints that
# provenance inline becomes unreadable — the owner ends up reading the citations instead of
# the argument. So the claim stays clean, the marker is 0.62em at 62% opacity, and the source
# is on hover, on click, and in the list at the foot of the page.
#
# `^[inferred]` is not numbered. It is the charter's anti-laundering mark, and it renders as
# its own word in ochre so an unsourced claim cannot pass as a sourced one.

CITES: list[dict] = []
_CITE_IX: dict[str, int] = {}


def cite_reset() -> None:
    """Numbering is per page. Every builder calls this before it renders anything."""
    CITES.clear()
    _CITE_IX.clear()


def cite_n(label: str, url: str) -> int:
    """The number for one source, reusing it when the same source is cited twice."""
    key = f"{label}\x1f{url}"
    if key not in _CITE_IX:
        CITES.append({"n": len(CITES) + 1, "label": label, "url": url})
        _CITE_IX[key] = len(CITES)
    return _CITE_IX[key]


def cite_list_html() -> str:
    """The reference list. Empty string when nothing on the page was cited, so a page with no
    claims does not grow an empty apparatus."""
    if not CITES:
        return ""
    rows = []
    for c in CITES:
        label = html.escape(c["label"])
        # `url` was escaped once, on the way into `_inline`, so it is already attribute-safe.
        # Escaping it again here turns a `&` in a timestamped link into `&amp;amp;` and
        # silently changes the query string — which is how the link stops working.
        body = (f'<a href="{safe_url(c["url"])}" target="_blank" '
                f'rel="noreferrer">{label}</a>'
                if c["url"] else f'{label} <span class="nolink">no link recorded</span>')
        rows.append(f'<li id="src-{c["n"]}"><span class="n">{c["n"]}</span>{body}</li>')
    return f'<ol class="srclist">{"".join(rows)}</ol>'


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
        if path.stem.startswith("0000"):
            continue
        # A dated decision is keyed by its slug — the identity the charter tells prose to cite —
        # and by its full stem. It is NEVER keyed by its leading four digits: those are the
        # year, and keying on them would turn every mention of "2026" into a link to whichever
        # decision sorted last that year. A legacy `NNNN-` file keeps its bare-number key,
        # because a tree mid-migration still cites it that way.
        dated = re.match(r"^(\d{4}-\d{2}-\d{2})-(.+)$", path.stem)
        legacy = re.match(r"^(\d{4})-(?!\d{2}-\d{2})(.+)$", path.stem)
        if not (dated or legacy):
            continue
        text = path.read_text()
        head = re.search(r"^#\s*(?:\d{4}\s*[—-]\s*)?(.+)$", text, re.M)
        title = head.group(1).strip() if head else path.stem
        status = re.search(r"^Date:.*·\s*Status:\s*(.+)$", text, re.M)
        entry = {
            "kind": "decision",
            "title": title,
            "gloss": _first_para(text, after="## Decision"),
            "note": (status.group(1).strip() if status else ""),
            "path": path,
        }
        if dated:
            g[dated.group(2)] = entry         # [[the-slug]] — the form prose uses
        else:
            entry["kind"] = "decision " + legacy.group(1)
            g[legacy.group(1)] = entry        # [[0017]] — legacy, mid-migration only
        g[path.stem] = entry                  # the full [[YYYY-MM-DD-slug]] form too

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

SAFE_SCHEME = re.compile(r"^(?:https?:|mailto:)", re.I)


def safe_url(url: str) -> str:
    """An external URL, or `#` if its scheme is not one we are willing to make clickable.

    Source tags are not all written by the owner: `/briefing` routes text in from Slack,
    mail and meeting recordings, and `feed.html` is opened on a phone. A `javascript:` or
    `data:` href reaching that page would run as the page. Anything relative is left alone —
    those are links to files in this repo."""
    u = url.strip()
    if not u or u.startswith(("#", "/", ".")):
        return u
    if ":" not in u.split("/", 1)[0]:
        return u                      # no scheme at all: a relative path
    return u if SAFE_SCHEME.match(u) else "#"


def here(path) -> str:
    """A path written relative to the generated page, never absolute.

    `/Users/<name>/…` in an href breaks the moment the page is opened on any other device —
    which is the whole reason the workspace has a remote — and prints the owner's directory
    layout into a file that gets shared."""
    return os.path.relpath(str(path), str(OUT.parent))


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
        return lift(f'<a class="ref" href="{html.escape(here(e["path"]))}" '
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
            return lift(f'<a class="path" href="{html.escape(here(target))}" '
                        f'title="open {html.escape(inner)}"><code>{inner}</code></a>')
        return lift(f"<code>{inner}</code>")
    out = re.sub(r"`([^`]+)`", code, out)

    # `^[who · where · when](url)` — a source tag. Must run before the plain-link rule below,
    # which would otherwise eat the bracket pair and leave a stray caret in the prose.
    def src(m):
        label, url = m.group(1), (m.group(2) or "")
        if label.strip().lower() == "inferred":
            return lift('<span class="cite inferred" title="inferred — no source recorded, '
                        'and not to be cited as one">inferred</span>')
        n = cite_n(label, url)
        # `text` was escaped on entry, so `url` and `label` already are: escaping again here
        # would turn a `&` in a timestamped link into `&amp;amp;`.
        href = safe_url(url) if url else f"#src-{n}"
        return lift(f'<a class="ref cite" href="{href}" '
                    + ('target="_blank" rel="noreferrer" ' if url else "")
                    + f'data-kind="source" data-title="{label}" data-note="" '
                    + 'data-gloss="' + ("Opens the source at the moment quoted."
                                          if url else
                                          "No link recorded — this attribution is all the "
                                          "record has for the claim.") + '" '
                    + f'data-path="{url or "the source list at the foot of the page"}">'
                    ) + str(n) + lift("</a>")
    out = re.sub(r"\^\[([^\]]+)\](?:\(([^)\s]+)\))?", src, out)

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
        if all(re.match(r"^\s*\d+[.)]\s+", ln) or ln.startswith("  ") for ln in lines) \
                and re.match(r"^\s*\d+[.)]\s+", lines[0]):
            items, cur = [], ""
            for ln in lines:
                if re.match(r"^\s*\d+[.)]\s+", ln):
                    if cur:
                        items.append(cur)
                    cur = re.sub(r"^\s*\d+[.)]\s+", "", ln)
                else:
                    cur += " " + ln.strip()
            if cur:
                items.append(cur)
            parts.append("<ol>" + "".join(f"<li>{_inline(i, g)}</li>" for i in items) + "</ol>")
            continue
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
            kv = re.match(r"^(project|owner|blocks|cost|options|answered):\s*(.*)$", s)
            if kv:
                item["keys"][kv.group(1)] = kv.group(2).strip()
                body_start = i + 1
                continue
            if title is not None and item["keys"]:
                break
        item["title"] = title.group(1) if title else item["id"]
        item["body"] = "\n".join(lines[body_start:]).strip()
        item["options"] = [o.strip() for o in item["keys"].get("options", "").split("|") if o.strip()]
        item["project"] = item["keys"].get("project", "").strip() or "all"
        items.append(item)
    return sorted(items, key=lambda i: -i["n"])


def decision_path(ref: str):
    """A `[[link]]` from plan.md to the decision file it names.

    Links are written as `[[slug]]` — the date orders the log, the slug identifies the file —
    so the slug has to be resolved against what is on disk. The full stem and a legacy
    `NNNN-slug` still resolve, because a half-migrated tree has to keep working."""
    d = BRAIN / "decisions"
    direct = d / f"{ref}.md"
    if direct.exists():
        return direct
    for path in sorted(d.glob("*.md")):
        stem = path.stem
        if re.sub(r"^\d{4}-\d{2}-\d{2}-", "", stem) == ref or re.sub(r"^\d{4}-", "", stem) == ref:
            return path
    return None


def bar_status() -> dict:
    """`(project, n) -> (status, evidence)` from `feed-items.md`'s `## BAR` block.

    The condition **text** is read from the decision that owns it and never retyped. Whether
    each is met is a judgment no file can derive, and this block is the one place the tool
    asks to be told rather than deriving. Lines are `n: status · evidence`, prefixed
    `project/n:` once the engagement runs more than one strand, because each exits its own bar."""
    out = {}
    block = re.search(r"^## BAR\s*\n(.*?)(?=^## |\Z)", (BRAIN / "feed-items.md").read_text(),
                      re.M | re.S)
    if not block:
        return out
    for ln in block.group(1).splitlines():
        sm = re.match(r"^\s*(?:([a-z0-9-]+)/)?(\d)\s*:\s*(met|not-met|partly)\s*·\s*(.*)$",
                      ln.strip())
        if sm:
            out[(sm.group(1), sm.group(2))] = (sm.group(3), sm.group(4))
    return out


def chip(key: str) -> str:
    """The project a card is about, as a small uppercase label.

    Monochrome on purpose: the house style spends colour on intent — committing, discarding,
    a reference — and a strand of work is metadata, not intent. Nothing renders below two
    strands, where the chip would say the same word on every card."""
    if not MULTI_PROJECT or not key or key == "all":
        return ""
    return f'<span class="chip">{html.escape(PROJECT_LABEL.get(key, key))}</span>'


def project_filter() -> str:
    """One button per strand, plus everything.

    The whole compartmentalization story ends here: records are stored in one place under one
    owner each, and the separation the owner actually needs is a filter at the point he reads.
    Splitting `decisions/` per project would have traded the one-owner rule for this."""
    if not MULTI_PROJECT:
        return ""
    buttons = ['<button class="pf on" data-pf="*">everything</button>']
    buttons += [f'<button class="pf" data-pf="{html.escape(k)}">'
                f'{html.escape(PROJECT_LABEL[k])}</button>' for k in PROJECT_KEYS]
    return ('<div class="filter"><span class="flabel">project</span>'
            + "".join(buttons) + '</div>')


def bar_conditions() -> list[dict]:
    """One entry per project that is inside a stage: its label, the stage, and that stage's
    exit conditions, read from the decision that owns them so they cannot drift from it.

    Two strands of one engagement are rarely at the same stage, so plan.md carries a `## `
    section per project with `### Stage n` inside it. A single-project plan written the old
    way — `## Stage n` at the top level — still parses, and reports one unnamed bar."""
    plan = (BRAIN / "plan.md").read_text()
    status = bar_status()
    sections = []
    if re.search(r"^### Stage \d", plan, re.M):
        for m in re.finditer(r"^## (?!What this plan)(.+?)\s*$(.*?)(?=^## |\Z)", plan,
                             re.M | re.S):
            sections.append((m.group(1).strip(), m.group(2)))
    else:
        sections.append((None, plan))

    label_to_key = {v.lower(): k for k, v in PROJECT_LABEL.items()}
    label_to_key.update({k.lower(): k for k in PROJECT_KEYS})
    out = []
    for label, body in sections:
        sm = re.search(r"^#{2,3} (Stage \d+ · [^\n]*?) — \*\*current\*\*", body, re.M)
        if not sm:
            continue
        key = label_to_key.get((label or "").lower())
        ref = re.search(r"\*\*Bar: \[\[([^\]]+)\]\]", body)
        conds = []
        path = decision_path(ref.group(1)) if ref else None
        if path:
            dec = path.read_text().split("## Decision", 1)[-1].split("\n## ", 1)[0]
            for cm in re.finditer(r"^(\d)\.\s+\*\*(.+?)\*\*(.*?)(?=^\d\.\s+\*\*|\Z)",
                                  dec, re.M | re.S):
                n = cm.group(1)
                st, ev = status.get((key, n)) or status.get((None, n)) or ("unknown", "")
                conds.append({"n": n, "claim": " ".join(cm.group(2).split()),
                              "detail": " ".join(cm.group(3).split())[:400],
                              "status": st, "evidence": ev})
        if conds:
            out.append({"project": key, "label": label, "stage": sm.group(1), "conds": conds})
    return out


def drafts() -> list[dict]:
    """Messages written for the owner to send, newest first, from `brain/drafts/`.

    This replaced a `comms/` folder that `feed.py` rendered, nothing documented, and no clone
    ever created — which is exactly how a drafted email ends up in a scratch directory the
    owner has no reason to know the path of. One documented home, inside the brain, listed on
    the page they already read.

    The **body is what gets sent**, verbatim, so the copy button can hand it over unedited.
    """
    folder = BRAIN / "drafts"
    if not folder.exists():
        return []
    out = []
    for path in sorted(folder.glob("*.md")):
        if path.name == "README.md":
            continue
        m = re.match(r"^(\d{4}-\d{2}-\d{2})-(.+)\.md$", path.name)
        if not m:
            continue
        text = path.read_text(encoding="utf-8")
        fm = re.match(r"^---\n(.*?)\n---\n?", text, re.S)
        meta, body = {}, text
        if fm:
            body = text[fm.end():]
            for ln in fm.group(1).splitlines():
                k, _, v = ln.partition(":")
                if _:
                    meta[k.strip()] = v.strip()
        out.append({
            "date": m.group(1), "path": path, "body": body.strip(),
            "to": meta.get("to", ""), "channel": (meta.get("channel") or "other").lower(),
            "subject": meta.get("subject") or m.group(2).replace("-", " "),
            "status": (meta.get("status") or "draft").lower(),
            "sent": meta.get("sent", ""),
        })
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
    # Bare-number aliases, for a tree still holding legacy `NNNN-` names. The negative
    # lookahead keeps a dated `2026-09-15-slug` out: its first four digits are the year.
    numbered = {n["id"][:4]: n["id"] for n in nodes
                if re.match(r"^\d{4}-(?!\d{2}-\d{2})", n["id"])}
    # A dated record is aliased by its slug, which is what `[[links]]` in the brain name.
    slugged = {m.group(1): n["id"] for n in nodes
               if (m := re.match(r"^\d{4}-\d{2}-\d{2}-(.+)$", n["id"]))}
    numbered.update(slugged)

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
        return ('<p style="font-size:13.5px;color:var(--ink-3);margin:0">Nothing to draw yet — '
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

/* One deliberate look: white paper, black ink. There is no dark-mode block, and that is a
   decision rather than an omission — a page that flips to a dark dashboard at the whim of an
   OS setting is the thing this design exists to not be. */
:root{
  --paper:#ffffff;
  --ink:#0d0d0e;
  --ink-2:#3a3a3e;      /* secondary prose */
  --ink-3:#6e6e75;      /* metadata */
  --ink-4:#9a9aa1;      /* faintest legible */
  --rule:rgba(13,13,14,.13);
  --rule-soft:rgba(13,13,14,.07);
  --wash:#f6f5f2;       /* warm paper tint for insets */
  --blue:#12408f;       /* references, links: the one habitual colour */
  --blue-wash:#eaf0fb;
  --ochre:#8a5a12;      /* awaiting, unsent, draft */
  --ochre-wash:#fbf3e4;
  --green:#1f6640;      /* met, answered, inbound */
  --green-wash:#eaf3ed;
  --red:#a52218;        /* destructive only */
  --sans:"Inter","Inter var",-apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,sans-serif;
  --mono:"IBM Plex Mono","JetBrains Mono",ui-monospace,SFMono-Regular,"SF Mono",Menlo,monospace;
}

html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);
  font-family:var(--sans);font-size:17px;line-height:1.72;
  font-feature-settings:"kern" 1,"liga" 1,"calt" 1;
  -webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}
.wrap{max-width:812px;margin:0 auto;padding:72px 28px 160px}

h1,h2,h3,h4,h5{font-family:var(--sans);margin:0 0 .45em;font-weight:600}
h1{font-size:clamp(32px,4.4vw,45px);line-height:1.08;letter-spacing:-.033em;
  text-wrap:balance;margin-bottom:.3em}
h3{font-size:23px;line-height:1.26;letter-spacing:-.021em;text-wrap:balance}
h4{font-size:18px;letter-spacing:-.012em}
h5{font-size:15px;color:var(--ink-3)}
p{margin:0 0 1.05em;max-width:68ch}
ul,ol{margin:0 0 1.05em;padding-left:1.35em}
li{margin:.34em 0;max-width:66ch}
strong,b{font-weight:600}
em,i{font-style:italic}
a{color:inherit}
code{font-family:var(--mono);font-size:.855em;background:var(--wash);
  padding:.1em .36em;border-radius:3px;word-break:break-word;
  font-feature-settings:"kern" 1}
hr{border:0;border-top:1px solid var(--rule);margin:2.4em 0}
button{font:inherit;font-family:var(--sans);cursor:pointer}

/* Small letterspaced label. The structural device of the whole page: it names a section
   without needing a box drawn around it. */
.kicker{font-size:11px;font-weight:600;letter-spacing:.15em;text-transform:uppercase;
  color:var(--ink-3);margin:0 0 18px}

/* Sections are separated by air and a hairline, never by a rounded card with a shadow. */
.panel{padding:0;margin:0 0 58px;border-top:1px solid var(--rule);padding-top:30px}
.panel.tight{margin-bottom:38px}

/* ── masthead ────────────────────────────────────────────────────────── */
.top{margin:0 0 46px}
.top .kicker{margin-bottom:22px}
.top .meta{margin-top:20px;font-size:13px;line-height:1.6;color:var(--ink-4);
  font-variant-numeric:tabular-nums}
.top .meta code{background:none;padding:0;color:var(--ink-3)}

.pill{display:inline-block;font-size:10.5px;font-weight:600;letter-spacing:.11em;
  text-transform:uppercase;padding:0;color:var(--ink-3);background:none}
.pill.warn{color:var(--ochre)}
.pill.ok{color:var(--green)}
.pill.warn::before,.pill.ok::before{content:"";display:inline-block;width:5px;height:5px;
  border-radius:50%;margin-right:6px;vertical-align:.14em}
.pill.warn::before{background:var(--ochre)}
.pill.ok::before{background:var(--green)}

/* ── projects: one rail per strand, one chip per card, one filter ─────
   Monochrome by design. Colour on this page carries intent — committing, discarding, a
   reference — and which strand of work a card belongs to is metadata, not intent. */
.rail{margin:0 0 4px}
.rail .stages{margin-bottom:22px}
.raillabel{font-size:10.5px;font-weight:600;letter-spacing:.15em;text-transform:uppercase;
  color:var(--ink-3);margin:0 0 8px}
.filter{display:flex;align-items:baseline;gap:9px;flex-wrap:wrap;margin:10px 0 44px;
  padding:0 0 15px;border-bottom:1px solid var(--rule)}
.flabel{font-size:10.5px;font-weight:600;letter-spacing:.15em;text-transform:uppercase;
  color:var(--ink-4);margin-right:3px}
.pf{font-family:var(--sans);font-size:12.5px;font-weight:500;color:var(--ink-3);
  background:none;border:1px solid var(--rule);border-radius:2px;padding:5px 11px;
  cursor:pointer}
.pf:hover{color:var(--ink);border-color:var(--ink-4)}
.pf.on{color:var(--paper);background:var(--ink);border-color:var(--ink)}
.chip{font-size:10px;font-weight:600;letter-spacing:.13em;text-transform:uppercase;
  color:var(--ink-3);border:1px solid var(--rule);border-radius:2px;padding:3px 7px}
[hidden]{display:none!important}

/* ── stage strip ─────────────────────────────────────────────────────── */
.stages{display:flex;gap:0;margin:0 0 52px;flex-wrap:wrap;
  border-top:1px solid var(--ink);border-bottom:1px solid var(--rule)}
.stage{flex:1 1 130px;min-width:130px;padding:13px 4px 12px;font-size:12.5px;
  color:var(--ink-4);border-right:1px solid var(--rule-soft)}
.stage:last-child{border-right:0}
.stage b{display:block;font-family:var(--mono);font-size:11px;font-weight:500;
  letter-spacing:.04em;margin-bottom:2px}
.stage.done{color:var(--ink-3)}
.stage.here{color:var(--ink);font-weight:600}
.stage.here b{color:var(--blue)}

/* ── exit conditions ─────────────────────────────────────────────────── */
.cond{display:flex;gap:20px;padding:17px 0;border-top:1px solid var(--rule-soft);
  align-items:baseline}
.cond:first-of-type{border-top:0;padding-top:4px}
.cond .dot{flex:0 0 auto;width:auto;min-width:22px;font-family:var(--mono);font-size:15px;
  font-weight:400;color:var(--ink-4);text-align:left}
.cond.met .dot{color:var(--green)}
.cond.partly .dot{color:var(--ochre)}
.cond .claim{font-size:17px;cursor:pointer;max-width:62ch}
.cond .claim:hover{color:var(--blue)}
.cond .ev{font-size:14px;color:var(--ink-3);margin-top:5px;max-width:64ch}
.cond .status{font-size:10px;font-weight:600;letter-spacing:.13em;text-transform:uppercase;
  color:var(--ink-4);margin-right:9px}
.cond.met .status{color:var(--green)}
.cond.partly .status{color:var(--ochre)}
.cond:not(.met):not(.partly) .status{color:var(--red)}
.cond .more{font-size:15.5px;color:var(--ink-2);margin-top:11px;display:none;max-width:64ch;
  padding-left:14px;border-left:2px solid var(--rule)}
.cond.open .more{display:block}

/* ── the graph ───────────────────────────────────────────────────────── */
svg.graph{display:block;width:100%;height:auto;overflow:visible;touch-action:pan-y;
  margin:6px 0 2px}
svg.graph line.e-link{stroke:var(--ink-4);stroke-width:1.1;opacity:.62}
svg.graph line.e-tag{stroke:var(--blue);stroke-width:1;stroke-dasharray:1.5 4;opacity:.4}
svg.graph .n-decision{fill:var(--blue)}
svg.graph .n-insight{fill:var(--green)}
svg.graph .n-braindump{fill:var(--ochre)}
svg.graph .n-briefing{fill:var(--ink-4)}
svg.graph .n-tag{fill:var(--paper);stroke:var(--ink-3);stroke-width:1.3}
svg.graph text{font-family:var(--sans);font-size:9.5px;font-weight:450;
  text-anchor:middle;fill:var(--ink-2);pointer-events:none}
svg.graph text.l-tag{fill:var(--ink-4);font-size:8.5px;font-weight:600;letter-spacing:.09em;
  text-transform:uppercase}
svg.graph a.gnode{cursor:pointer}
svg.graph a.gnode:hover circle,svg.graph a.gnode:hover rect{stroke:var(--ink);stroke-width:2}
svg.graph a.gnode:hover text{fill:var(--ink);font-weight:600}
.legend{display:flex;flex-wrap:wrap;gap:16px;margin:0 0 4px;font-size:12px;color:var(--ink-3)}
.legend .lg{display:inline-flex;align-items:center;gap:6px}
.legend .lg::before{content:"";width:7px;height:7px;border-radius:50%;background:var(--ink-4)}
.legend .lg.decision::before{background:var(--blue)}
.legend .lg.insight::before{background:var(--green)}
.legend .lg.braindump::before{background:var(--ochre)}
.legend .lg.briefing::before{background:var(--ink-4)}
.legend .lg.tag::before{background:var(--paper);border:1.3px solid var(--ink-3);
  border-radius:1px;transform:rotate(45deg);width:6px;height:6px}

/* ── the feed ────────────────────────────────────────────────────────── */
.card{padding:34px 0 4px;margin:0;border-top:1px solid var(--rule);position:relative}
.card.answered{opacity:.55;transition:opacity .18s}
.card.answered:hover{opacity:1}
.card .cardhead{display:flex;gap:14px;align-items:baseline;flex-wrap:wrap;margin-bottom:10px}
.card .idtag{font-family:var(--mono);font-size:11.5px;letter-spacing:.05em;color:var(--ink-4)}
.card h3{margin:0 0 16px}

.facts{display:flex;flex-wrap:wrap;gap:0 26px;margin:0 0 20px;padding:12px 0;
  border-top:1px solid var(--rule-soft);border-bottom:1px solid var(--rule-soft)}
.fact{font-size:13px;color:var(--ink-3);background:none;border:0;padding:0}
.fact b{display:block;font-size:10px;font-weight:600;letter-spacing:.12em;
  text-transform:uppercase;color:var(--ink-4);margin-bottom:1px}
.body{font-size:17px;color:var(--ink-2)}
.body p:last-child{margin-bottom:0}
.body strong{color:var(--ink)}

/* Disclosure: a quiet line of type, not a widget. */
details.fold>summary,details.body-more>summary{font-size:13px;color:var(--ink-3);
  cursor:pointer;list-style:none;padding:4px 0;font-weight:500;letter-spacing:.005em}
details.fold>summary::-webkit-details-marker,
details.body-more>summary::-webkit-details-marker{display:none}
details.fold>summary::before,details.body-more>summary::before{content:"+";
  font-family:var(--mono);color:var(--blue);margin-right:9px;font-size:12px}
details.fold[open]>summary::before,details.body-more[open]>summary::before{content:"–"}
details.fold>summary:hover,details.body-more>summary:hover{color:var(--ink)}
details.fold[open]>summary{color:var(--ink-4)}
details.body-more{margin-top:6px}

/* ── answering ───────────────────────────────────────────────────────── */
.answer{margin-top:26px;padding-top:20px;border-top:1px solid var(--rule)}
.opts{display:flex;flex-wrap:wrap;gap:9px;margin-bottom:13px}
/* An option is a considered choice, so it reads as type in a hairline frame until picked,
   then commits to ink. */
.opt{border:1px solid var(--rule);background:var(--paper);color:var(--ink);
  border-radius:2px;padding:9px 15px;font-size:14.5px;transition:.14s ease}
.opt:hover{border-color:var(--ink);}
.opt.picked{background:var(--ink);border-color:var(--ink);color:var(--paper);font-weight:500}
textarea{width:100%;min-height:64px;resize:vertical;
  font:16px/1.6 var(--sans);color:var(--ink);background:var(--wash);
  border:1px solid transparent;border-radius:2px;padding:13px 15px}
textarea::placeholder{color:var(--ink-4)}
textarea:focus{outline:none;background:var(--paper);border-color:var(--ink)}
.saved{font-size:12px;color:var(--green);margin-top:8px;height:16px;letter-spacing:.02em}

/* ── references and their tooltips ───────────────────────────────────── */
a.ref{color:var(--blue);text-decoration:none;
  border-bottom:1px solid rgba(18,64,143,.32);cursor:help}
a.ref:hover{background:var(--blue-wash);border-bottom-color:var(--blue)}
span.ref.dead{color:var(--ink-4);border-bottom:1px dotted var(--ink-4)}

/* Citations. Small, faint, blue: present for anyone who wants to check a claim, invisible to
   anyone reading the argument. The rule this implements is in `brain/sources.md` — a claim
   about what a client said carries who said it, and a brief that carries it inline is a brief
   nobody finishes. Deliberately no background and no underline, unlike a.ref, because a
   marker that highlights on hover next to every second sentence turns the page into a rash. */
a.ref.cite{font-family:var(--mono);font-size:.6em;font-weight:500;vertical-align:.45em;
  color:var(--blue);opacity:.6;border:0;background:none;padding:0 .06em;margin-left:.1em;
  text-decoration:none;transition:opacity .14s}
a.ref.cite:hover{opacity:1;background:none;border:0}
.cite.inferred{font-family:var(--mono);font-size:.64em;letter-spacing:.06em;
  text-transform:uppercase;color:var(--ochre);vertical-align:.35em;margin-left:.28em;
  cursor:help;border-bottom:1px dotted var(--ochre)}

ol.srclist{list-style:none;padding:0;margin:0;counter-reset:none}
ol.srclist li{display:flex;gap:14px;padding:9px 0;border-top:1px solid var(--rule-soft);
  font-size:13.5px;line-height:1.55;color:var(--ink-2)}
ol.srclist li:first-child{border-top:0}
ol.srclist .n{flex:0 0 22px;font-family:var(--mono);font-size:11.5px;color:var(--ink-4);
  padding-top:2px}
ol.srclist .nolink{color:var(--ink-4);font-size:12px;margin-left:6px}
a.path{color:var(--blue);text-decoration:none}
a.path:hover code{background:var(--blue-wash)}
#tip{position:fixed;z-index:99;max-width:392px;background:var(--paper);color:var(--ink);
  border:1px solid var(--rule);border-radius:3px;padding:16px 18px;
  box-shadow:0 1px 2px rgba(13,13,14,.05),0 14px 40px rgba(13,13,14,.13);
  font-size:14px;line-height:1.6;display:none;pointer-events:none}
#tip .k{font-family:var(--mono);font-size:10.5px;font-weight:500;letter-spacing:.09em;
  text-transform:uppercase;color:var(--blue);margin-bottom:5px}
#tip .t{font-weight:600;margin-bottom:7px;font-size:16px;letter-spacing:-.012em;
  line-height:1.32}
#tip .n{font-size:12px;color:var(--ink-4);margin-bottom:8px}
#tip .g{color:var(--ink-2)}
#tip .open{margin-top:11px;padding-top:9px;border-top:1px solid var(--rule-soft);
  font-size:11.5px;color:var(--ink-4)}

/* ── drafts waiting to be sent ───────────────────────────────────────── */
.draft{padding:19px 0 21px;border-top:1px solid var(--rule)}
.draft:first-of-type{border-top:0}
.draft .dmeta{font-family:var(--mono);font-size:11px;letter-spacing:.09em;
  text-transform:uppercase;color:var(--ink-3);margin-bottom:8px}
.draft .dmeta .noone{color:var(--red);text-transform:none;letter-spacing:0}
.draft .dsubject{font-size:18px;font-weight:500;letter-spacing:-.012em;margin-bottom:7px}
.draft .dpeek{font-size:14.5px;line-height:1.6;color:var(--ink-3);max-width:66ch;
  margin-bottom:13px}
.draft .dact{display:flex;align-items:center;gap:16px;flex-wrap:wrap}
.draft .dact button{font-family:var(--sans);font-size:13px;padding:7px 13px;
  border:1px solid var(--ink);background:var(--paper);color:var(--ink);cursor:pointer}
.draft .dact button:hover{background:var(--ink);color:var(--paper)}
.draft .dact button.done{border-color:var(--blue);color:var(--blue);background:var(--paper)}
.draft .dact .path{font-size:12.5px;color:var(--ink-3)}

/* ── the thread ──────────────────────────────────────────────────────── */
.thread{display:flex;gap:18px;padding:13px 0;border-top:1px solid var(--rule-soft);
  font-size:15px;align-items:baseline}
.thread:first-of-type{border-top:0}
.thread .d{flex:0 0 84px;color:var(--ink-4);font-family:var(--mono);font-size:12px;
  font-variant-numeric:tabular-nums}
.thread .dir{flex:0 0 44px;font-size:10px;font-weight:600;letter-spacing:.13em;
  text-transform:uppercase}
.thread .dir.out{color:var(--blue)}
.thread .dir.in{color:var(--green)}
.thread a{text-decoration:none;border-bottom:1px solid var(--rule)}
.thread a:hover{border-bottom-color:var(--ink)}

/* ── the dock ────────────────────────────────────────────────────────── */
.dock{position:fixed;left:0;right:0;bottom:0;background:rgba(255,255,255,.94);
  backdrop-filter:saturate(1.4) blur(8px);
  border-top:1px solid var(--rule);padding:14px 22px;display:flex;gap:16px;
  align-items:center;justify-content:center;flex-wrap:wrap}
.dock .count{font-size:13.5px;color:var(--ink-3)}
/* Intent, in the colour: committing is ink, discarding is the only red on the page. */
.dock button{border-radius:2px;padding:10px 18px;font-size:14px;
  border:1px solid var(--rule);background:var(--paper);color:var(--ink-2);transition:.14s}
.dock button:hover{border-color:var(--ink);color:var(--ink)}
.dock button.primary{background:var(--ink);border-color:var(--ink);color:var(--paper);
  font-weight:500}
.dock button.primary:hover{background:#000}
.dock #clear{border-color:transparent;color:var(--ink-4)}
.dock #clear:hover{color:var(--red);border-color:rgba(165,34,24,.4)}
.dock button:disabled{opacity:.36;cursor:not-allowed}
.dock button.primary:disabled:hover{background:var(--ink)}

/* ── now.md ──────────────────────────────────────────────────────────── */
.nowbody{font-size:18px;line-height:1.7}
.nowbody p{max-width:64ch}
.nowbody h2,.nowbody h3{font-size:11px;font-weight:600;text-transform:uppercase;
  letter-spacing:.15em;color:var(--ink-4);margin:1.9em 0 .55em;letter-spacing:.15em}
.nowbody>*:first-child{margin-top:0}
.nowbody em{color:var(--ink-3)}

@media (max-width:640px){
  .wrap{padding:44px 20px 150px}
  body{font-size:16.5px}
  .nowbody{font-size:17px}
  .thread .d{flex-basis:72px}
  .stage{flex-basis:50%;min-width:50%}
  .facts{gap:0 18px}
}
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

/* a draft's whole body onto the clipboard — the body IS the message, so it pastes unedited */
document.querySelectorAll('.draft').forEach(d=>{
  const b=d.querySelector('.copy-draft'), src=d.querySelector('.draft-src');
  if(!b||!src) return;
  b.addEventListener('click',async()=>{
    const text=src.textContent;
    try{ await navigator.clipboard.writeText(text); }
    catch(e){ const t=document.createElement('textarea');t.value=text;document.body.append(t);
              t.select();document.execCommand('copy');t.remove(); }
    const old=b.textContent; b.textContent='copied — paste it and send';
    b.classList.add('done');
    setTimeout(()=>{b.textContent=old;b.classList.remove('done');},2400);
  });
});

/* conditions expand */
document.querySelectorAll('.cond .claim').forEach(c=>{
  c.addEventListener('click',()=>c.closest('.cond').classList.toggle('open'));
});

"""

# The tooltip is the only interactive part a second page needs, so it is its own constant —
# `brief.py` imports it rather than keeping a copy that can drift.
TIP_JS = """
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

FILTER_JS = """
// One strand at a time, or everything. A card or panel marked `all` belongs to the
// engagement rather than to one project, so it survives every filter.
document.querySelectorAll('.pf').forEach(function (b) {
  b.addEventListener('click', function () {
    var want = b.dataset.pf;
    document.querySelectorAll('.pf').forEach(function (o) { o.classList.toggle('on', o === b); });
    document.querySelectorAll('[data-project]').forEach(function (el) {
      var p = el.dataset.project;
      el.hidden = !(want === '*' || p === want || p === 'all');
    });
  });
});
"""

JS = JS + TIP_JS + FILTER_JS


def build() -> str:
    g = glossary()
    items = feed_items()
    bars = bar_conditions()
    thread = drafts()
    now_md = (BRAIN / "now.md").read_text()
    now_md = re.sub(r"^# Now\s*\n", "", now_md)
    now_md = re.sub(r"^\*20.*?\*\s*$", "", now_md, count=1, flags=re.M | re.S)

    waiting = [i for i in items if i["status"] == "awaiting-you"]
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # The stage rail. Each project runs its own arc, so each gets its own row — an engagement
    # with one strand renders exactly one and looks unchanged.
    plan_text = (BRAIN / "plan.md").read_text()
    rails = []
    if re.search(r"^### Stage \d", plan_text, re.M):
        chunks = [(m.group(1).strip(), m.group(2)) for m in
                  re.finditer(r"^## (?!What this plan)(.+?)\s*$(.*?)(?=^## |\Z)", plan_text,
                              re.M | re.S)]
    else:
        chunks = [(None, plan_text)]
    rail_key = {v.lower(): k for k, v in PROJECT_LABEL.items()}
    rail_key.update({k.lower(): k for k in PROJECT_KEYS})
    for label, body in chunks:
        steps = []
        for m in re.finditer(r"^#{2,3} (Stage (\d+) · [^—\n]+?) — \*?\*?(.+?)\*?\*?\s*$",
                             body, re.M):
            name, num, state = m.group(1), m.group(2), m.group(3)
            cls = "here" if "current" in state else ("done" if "exited" in state else "")
            short = name.split("·", 1)[1].strip() if "·" in name else name
            steps.append(f'<div class="stage {cls}" title="{html.escape(state)}">'
                         f'<b>{num}</b>{html.escape(short)}</div>')
        if not steps:
            continue
        head = (f'<div class="raillabel">{html.escape(label)}</div>'
                if label and len(chunks) > 1 else "")
        key = rail_key.get((label or "").lower(), "all")
        rails.append(f'<div class="rail" data-project="{html.escape(key)}">{head}'
                     f'<div class="stages">{"".join(steps)}</div></div>')

    out = [f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Feed — {PROJECT_NAME}</title>
{FONT_LINK}<style>{CSS}</style></head><body>
<div id="tip"></div>
<div class="wrap">
<div class="top">
  <div><div class="kicker">{PROJECT_NAME} · decision feed</div>
       <h1>Where we are, and what is waiting on you</h1></div>
  <div class="meta">generated {stamp}<br>from brain/*.md — regenerate with
    <code>python3 brain/feed.py</code></div>
</div>

{''.join(rails)}
{project_filter()}
"""]

    # ── now ──────────────────────────────────────────────────────────────────────────────────
    out.append('<div class="panel"><div class="kicker">now.md · the one-screen state</div>'
               f'<div class="nowbody">{render_md(now_md, g)}</div></div>')

    # ── the bar ──────────────────────────────────────────────────────────────────────────────
    for bar in bars:
        conds, stage = bar["conds"], bar["stage"]
        met = sum(1 for c in conds if c["status"] == "met")
        rows = []
        words = {"met": "met", "partly": "partly", "unknown": "not met"}
        for c in conds:
            cls = c["status"] if c["status"] in ("met", "partly") else ""
            word = words.get(c["status"], "not met")
            ev = (f'<span class="status">{word}</span>'
                  + (_inline(c["evidence"], g) if c["evidence"] else ""))
            rows.append(
                f'<div class="cond {cls}"><div class="dot">{c["n"]}</div><div>'
                f'<div class="claim">{_inline(c["claim"], g)}</div>'
                f'<div class="ev">{ev}</div>'
                f'<div class="more">{_inline(c["detail"], g)}</div></div></div>')
        out.append(
            f'<div class="panel" data-project="{html.escape(bar["project"] or "all")}">'
            '<div class="kicker">'
            + (f'{html.escape(bar["label"])} · ' if bar["label"] and len(bars) > 1 else "")
            + 'what has to be true to leave '
            f'{html.escape(stage.split("·")[0].strip())} '
            f'<span class="pill {"ok" if met == len(conds) else "warn"}">{met} of {len(conds)}'
            '</span></div>'
            '<p style="font-size:13.5px;color:var(--ink-3);margin:-2px 0 10px">'
            'Tap a condition for the full wording from the decision that owns it.</p>'
            + "".join(rows) + '</div>')

    # ── the graph ────────────────────────────────────────────────────────────────────────────
    gnodes, gedges = graph_data()
    layout(gnodes, gedges)          # once; graph_svg and write_canvas share the result
    write_canvas(gnodes, gedges)
    out.append('<div class="panel"><div class="kicker">the brain · '
               f'{len(gnodes)} note(s) and tag(s), how they connect</div>'
               '<p style="font-size:13.5px;color:var(--ink-3);margin:-2px 0 10px">'
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
            fold_label = "hide"
        else:
            given = k.get("answered", "").strip()
            fold_label = (f"you said: {given}" if given
                          else f"{item['status']} · open it")
        out.append(f"""<div class="card{'' if live else ' answered'}"
  data-id="{item['id']}" data-project="{html.escape(item['project'])}"
  data-title="{html.escape(item['title'])}">
  <div class="cardhead"><span class="idtag">{item['id']}</span>{chip(item['project'])}{answered_pill}</div>
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

    # ── messages waiting to be sent ──────────────────────────────────────────────────────────
    # Unsent first and in full, because an unsent draft is an action the owner owes someone.
    # Sent ones stay as a quiet list: what we actually told a client is part of the record.
    if thread:
        today = date.today()
        unsent = [c for c in thread if c["status"] != "sent"]
        sent = [c for c in thread if c["status"] == "sent"]
        rows = []
        for i, c in enumerate(unsent):
            days = (today - date.fromisoformat(c["date"])).days
            age = ("today" if days == 0 else f"{days}d old")
            stale = ' <span class="pill warn">still unsent</span>' if days >= 7 else ""
            to = (html.escape(c["to"]) if c["to"]
                  else '<span class="noone">addressed to nobody</span>')
            rows.append(
                f'<div class="draft" data-id="d{i}">'
                f'<div class="dmeta">{html.escape(c["channel"])} · to {to} · '
                f'{c["date"]} · {age}{stale}</div>'
                f'<div class="dsubject">{html.escape(c["subject"])}</div>'
                f'<div class="dpeek">{html.escape(" ".join(c["body"].split())[:230])}…</div>'
                f'<div class="dact"><button class="copy-draft">Copy the message</button>'
                f'<a class="path" href="{html.escape(str(c["path"]))}">'
                f'open {html.escape(c["path"].name)}</a></div>'
                f'<pre class="draft-src" hidden>{html.escape(c["body"])}</pre>'
                f'</div>')
        for c in sent[:6]:
            rows.append(
                f'<div class="thread"><div class="d">{c["sent"] or c["date"]}</div>'
                f'<div class="dir out">sent</div>'
                f'<div><a href="{html.escape(str(c["path"]))}">'
                f'{html.escape(c["subject"])}</a>'
                f' <span style="color:var(--ink-4)">· {html.escape(c["channel"])}'
                f'{" · to " + html.escape(c["to"]) if c["to"] else ""}</span></div></div>')
        kicker = (f"waiting for you to send · {len(unsent)}" if unsent
                  else "messages · all sent")
        out.append(f'<div class="panel"><div class="kicker">{kicker}</div>'
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
