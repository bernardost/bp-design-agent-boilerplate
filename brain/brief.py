#!/usr/bin/env python3
"""brief.py — render the project brief as one page the owner can read and approve.

    python3 brain/brief.py [--open]

**Why this exists.** Once the first context lands — a kickoff recording, a thread, a folder of
client material — a session can start moving without either party ever agreeing on what the
project *is*. The work then advances on the assistant's private reading of it, which is the
expensive kind of wrong: it surfaces weeks later as a deliverable aimed at the wrong thing.
So the brief is a gate, not a document. It says *this is what I understood, here is what I
still do not know, here is the shape of the work, here is what I would do next* — and it waits.

**What it renders, and from where.** Nothing here is authored. Every section is read out of
the file that owns it, so the page cannot disagree with the brain:

    the brief        brain/project-brief.md
    the unknowns     brain/open-questions.md   (## Open, with each question's owner)
    the plan         brain/plan.md + the decision that holds the current stage's exit bar
    next steps       brain/tasks.md            (doing and todo, by priority)
    the sources      every `^[…]` citation on the page, collected as it renders

**Citations are the quiet part.** `AGENTS.md` requires a claim about what a client said to
carry who said it and when. Printed inline that requirement destroys the document — the owner
reads provenance instead of the argument. So `feed.py` renders a `^[who · where · when](url)`
tag as a faint superscript numeral: invisible while reading, one hover from the transcript,
and listed in full at the foot of the page. An unsourced guess is written `^[inferred]` and
renders as its own word in ochre, because a guess that reads like a quote is the failure this
whole apparatus exists to prevent.

**Unwritten sections render as gaps, not as absence.** A missing section prints "not written
yet" in its place. Seeing the hole is how the owner notices it; hiding it would make the page
flatter the brief.

The markdown files stay the truth. This writes a projection and is never read back — same
contract as `feed.py` and `spread.py`. Delete the HTML and nothing is lost.
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

sys.path.insert(0, str(BRAIN))
from config import PROJECT_NAME, OWNER, TRACKER_PREFIX  # noqa: E402
from feed import (  # noqa: E402
    CSS, FONT_LINK, TIP_JS, bar_conditions, cite_list_html, cite_reset, glossary, render_md,
)

OUT = BRAIN / "brief.html"
_KEY = rf"{TRACKER_PREFIX}-\d+|" if TRACKER_PREFIX else ""


# ---------------------------------------------------------------------------------------------
# Reading the brain
# ---------------------------------------------------------------------------------------------

def status() -> tuple[str, str]:
    """`(state, detail)` from the `Status:` line under the brief's title.

    Approval has to live somewhere a script can read and a human can see, and it cannot live
    in a second file — so it is one line in the brief itself:

        Status: draft
        Status: approved 2026-09-04 · [[the-brief-is-approved]]

    An approved brief that names no decision is a verbal yes, which the record does not keep.
    `doctor.py` reports that; this page shows it.
    """
    text = (BRAIN / "project-brief.md").read_text(encoding="utf-8")
    m = re.search(r"^Status:\s*(.+)$", text, re.M)
    if not m:
        return "unset", ""
    detail = m.group(1).strip()
    state = "approved" if detail.lower().startswith("approved") else "draft"
    return state, detail


def brief_body() -> tuple[str, list[str]]:
    """The brief's prose, minus its own title, caption and status line — and the list of
    sections still holding nothing but the template's parenthetical prompt."""
    text = (BRAIN / "project-brief.md").read_text(encoding="utf-8")
    text = re.sub(r"^#\s+.*$", "", text, count=1, flags=re.M)
    text = re.sub(r"^Status:.*$", "", text, count=1, flags=re.M)
    text = re.sub(r"^\*Stable facts.*?\*\s*$", "", text, count=1, flags=re.M | re.S)

    empty = []
    for m in re.finditer(r"^##\s+(.+?)\s*\n(.*?)(?=^##\s|\Z)", text, re.M | re.S):
        body = m.group(2).strip()
        if not body or re.fullmatch(r"\*\(.*?\)\*", body, re.S):
            empty.append(m.group(1).strip())
    return text.strip(), empty


def unknowns() -> list[dict]:
    """The open questions, each with the owner who can answer it. The owner is the whole
    point of that file — a question with no owner is a worry, not a question."""
    text = (BRAIN / "open-questions.md").read_text(encoding="utf-8")
    block = re.search(r"^## Open\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not block:
        return []
    out = []
    for chunk in re.split(r"\n(?=\s*[-*]\s)", block.group(1)):
        line = " ".join(chunk.split())
        if not re.match(r"^[-*]\s", line):
            continue
        line = re.sub(r"^[-*]\s+", "", line)
        q = re.search(r"\bQ(\d{1,3})\b", line)
        owner = re.search(r"\*\*\[([^\]]+)\]\*\*", line)
        body = re.sub(r"\*\*\[[^\]]+\]\*\*", "", line)
        body = re.sub(r"^\s*Q\d{1,3}\s*[·:—-]*\s*", "", body).strip(" ·—-")
        out.append({"id": f"Q{q.group(1)}" if q else "", "owner": owner.group(1) if owner else "",
                    "text": body})
    return out


def next_steps() -> tuple[list[dict], dict]:
    """`doing` and `todo` from `tasks.md`, in the order to do them, plus a count of the rest.

    No cap. A brief that silently shows the top three reads as "this is all of it", and the
    charter's rule is that a bounded view says what it bounded.
    """
    text = (BRAIN / "tasks.md").read_text(encoding="utf-8")
    lines = text.splitlines()
    rows, counts = [], {}
    for i, line in enumerate(lines):
        m = re.match(rf"^-\s+`(\w+)`\s*·\s*(P\d)\s*·\s*(.*?)·\s*({_KEY}skip|—)\s*—\s*"
                     r"\*\*(.+?)\*\*\s*$", line)
        if not m:
            continue
        st, prio, labels, _ptr, title = m.groups()
        counts[st] = counts.get(st, 0) + 1
        if st not in ("doing", "todo"):
            continue
        note = ""
        for nxt in lines[i + 1:]:
            if not nxt.startswith("      "):
                break
            if nxt.strip():
                note = " ".join(nxt.split())
                break
        labs = [x for x in re.split(r"[`·,]\s*", labels) if x.strip() and x.strip() != "—"]
        rows.append({"status": st, "prio": prio, "labels": [x.strip() for x in labs],
                     "title": title, "note": note})
    rows.sort(key=lambda r: (0 if r["status"] == "doing" else 1, r["prio"]))
    return rows, counts


def stage_strip(plan_text: str) -> tuple[str, str]:
    """The stage arc as a strip, and the name of the stage we are in.

    `##` or `###`: a plan carrying several projects nests its stages one level under a project
    heading, and a single-project plan written flat still reads."""
    here = ""
    cells = []
    for m in re.finditer(r"^#{2,3} (Stage (\d+) · [^—\n]+?) — \*?\*?(.+?)\*?\*?\s*$",
                         plan_text, re.M):
        label, num, state = m.group(1), m.group(2), m.group(3)
        cls = "here" if "current" in state else ("done" if "exited" in state else "")
        short = label.split("·", 1)[1].strip() if "·" in label else label
        if cls == "here":
            here = short
        cells.append(f'<div class="stage {cls}" title="{html.escape(state)}">'
                     f'<b>{num}</b>{html.escape(short)}</div>')
    return "".join(cells), here


# ---------------------------------------------------------------------------------------------
# The page
# ---------------------------------------------------------------------------------------------

PAGE_CSS = """
/* One column, one measure. This page is read start to finish, unlike the feed, which is
   scanned — so it gets a book's width rather than a dashboard's. */
.wrap{max-width:820px}

.approval{display:flex;flex-wrap:wrap;align-items:baseline;gap:10px 18px;
  margin:26px 0 0;padding:15px 0;border-top:1px solid var(--ink);
  border-bottom:1px solid var(--rule)}
.approval .state{font-family:var(--mono);font-size:11px;font-weight:500;letter-spacing:.13em;
  text-transform:uppercase}
.approval.draft .state{color:var(--ochre)}
.approval.approved .state{color:var(--ink)}
.approval.unset .state{color:var(--red)}
.approval .what{font-size:14px;color:var(--ink-3);max-width:62ch}

.sec{margin:58px 0 0}
.sec > h2{font-size:13px;font-family:var(--mono);font-weight:500;letter-spacing:.14em;
  text-transform:uppercase;color:var(--ink-3);margin:0 0 22px;padding-bottom:11px;
  border-bottom:1px solid var(--ink)}
.sec .body h3{font-size:21px;margin:34px 0 10px;letter-spacing:-.015em}
.sec .body h3:first-child{margin-top:0}
.sec .body p,.sec .body li{font-size:16.5px;line-height:1.68;color:var(--ink-2)}
.sec .body em{color:var(--ink-4)}

.gap{font-family:var(--mono);font-size:12px;letter-spacing:.06em;color:var(--ochre);
  padding:11px 0 11px 14px;border-left:2px solid var(--ochre-wash);margin:0 0 8px}

.q{display:flex;gap:16px;padding:15px 0;border-top:1px solid var(--rule-soft)}
.q:first-child{border-top:0}
.q .qid{flex:0 0 42px;font-family:var(--mono);font-size:12.5px;color:var(--ink-3);
  padding-top:3px}
.q .qbody{min-width:0}
.q .qtext{font-size:16px;line-height:1.6;color:var(--ink)}
.q .qowner{font-family:var(--mono);font-size:11px;letter-spacing:.09em;text-transform:uppercase;
  color:var(--blue);margin-top:5px}
.q .qowner.none{color:var(--red)}

.step{display:flex;gap:16px;padding:16px 0;border-top:1px solid var(--rule-soft)}
.step:first-child{border-top:0}
.step .num{flex:0 0 26px;font-family:var(--mono);font-size:15px;color:var(--ink-4);
  padding-top:1px}
.step .stitle{font-size:16.5px;line-height:1.5;color:var(--ink);font-weight:500}
.step .snote{font-size:14px;line-height:1.6;color:var(--ink-3);margin-top:5px;max-width:62ch}
.step .stags{font-family:var(--mono);font-size:10.5px;letter-spacing:.09em;
  text-transform:uppercase;color:var(--ink-4);margin-top:7px}
.step .stags .bar{color:var(--blue)}
.step .stags .doing{color:var(--ink)}
.rest{font-size:13.5px;color:var(--ink-4);margin-top:18px}

.footnote{margin:62px 0 0;padding-top:22px;border-top:1px solid var(--rule);
  font-size:14px;line-height:1.65;color:var(--ink-3)}
.footnote b{color:var(--ink)}
"""


def build() -> str:
    cite_reset()                      # numbering is per page, and this page is built once
    g = glossary()
    state, detail = status()
    body, empty = brief_body()
    qs = unknowns()
    steps, counts = next_steps()
    plan_text = (BRAIN / "plan.md").read_text(encoding="utf-8")
    strip, here = stage_strip(plan_text)
    # The brief is the engagement's one approved understanding, so it shows the bars of every
    # project that is inside a stage rather than picking one.
    bars = bar_conditions()
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # The approval strip. Three states, and "unset" is loud on purpose: a brief with no status
    # line has never been put in front of anyone, which is the exact failure this page fixes.
    words = {
        "draft": ("draft — awaiting your approval",
                  "Read it, then say what is wrong or say it is approved. Approving it writes "
                  "a numbered decision and this line changes to name it."),
        "approved": (detail.lower(),
                     "Approved. Re-approval is only needed when the engagement itself changes "
                     "— volatile state lives in now.md, not here."),
        "unset": ("no status line",
                  "brain/project-brief.md carries no `Status:` line, so nothing records "
                  "whether this was ever agreed. Add one under the title."),
    }[state]

    secs = []

    # ── the brief itself ─────────────────────────────────────────────────────────────────────
    gaps = "".join(f'<div class="gap">{html.escape(e)} — not written yet</div>' for e in empty)
    secs.append(f"""<div class="sec"><h2>What this project is</h2>
      <div class="body">{render_md(body, g) if body.strip() else ""}</div>{gaps}</div>""")

    # ── unknowns ─────────────────────────────────────────────────────────────────────────────
    if qs:
        rows = []
        for q in qs:
            own = (f'<div class="qowner">{html.escape(q["owner"])} can answer</div>'
                   if q["owner"] else
                   '<div class="qowner none">no owner named — nobody can answer it</div>')
            rows.append(f'<div class="q"><div class="qid">{html.escape(q["id"])}</div>'
                        f'<div class="qbody"><div class="qtext">'
                        f'{render_md(q["text"], g)}</div>{own}</div></div>')
        inner = "".join(rows)
    else:
        inner = ('<div class="gap">no open questions recorded — a brief this early with '
                 'nothing unknown is a brief that has not been checked</div>')
    secs.append(f'<div class="sec"><h2>What I still do not know</h2>{inner}</div>')

    # ── the plan ─────────────────────────────────────────────────────────────────────────────
    blocks = []
    for bar_entry in bars:
        cells = []
        for c in bar_entry["conds"]:
            st = c["status"]
            mark = {"met": "met", "partly": "partly", "not-met": "not met"}.get(st, "unknown")
            ev = (f'<div class="ev">{render_md(c["evidence"], g)}</div>' if c.get("evidence")
                  else "")
            cells.append(f'<div class="cond {st}"><div class="dot">{c["n"]}</div>'
                         f'<div><div class="claim"><span class="status">{mark}</span>'
                         f'{render_md(c["claim"], g)}</div>{ev}'
                         f'<div class="more">{render_md(c["detail"], g)}</div></div></div>')
        head = (f'{html.escape(bar_entry["label"])} · ' if bar_entry["label"] and len(bars) > 1
                else "")
        blocks.append(f'<h3 style="margin-top:30px">{head}'
                      f'{html.escape(bar_entry["stage"])} — what ends it</h3>'
                      + "".join(cells))
    if blocks:
        bar = ("".join(blocks)
               + '<div class="rest">Every condition above is read from the decision that owns '
                 'it. Status is a judgment and comes from the BAR block in feed-items.md.</div>')
    else:
        bar = ('<h3 style="margin-top:30px">What ends the current stage</h3>'
               '<div class="gap">this stage has no exit bar — write it as a decision before '
               'the work goes further, or the stage cannot end</div>')
    secs.append(f"""<div class="sec"><h2>The plan</h2>
      <div class="stages">{strip}</div>
      {bar}</div>""")

    # ── next steps ───────────────────────────────────────────────────────────────────────────
    if steps:
        rows = []
        for i, s in enumerate(steps, 1):
            tags = [f'<span class="doing">{s["status"]}</span>'] if s["status"] == "doing" else []
            tags += [f'<span class="bar">{l}</span>' if l == "bar" else f"<span>{l}</span>"
                     for l in s["labels"]]
            note = f'<div class="snote">{render_md(s["note"], g)}</div>' if s["note"] else ""
            rows.append(f'<div class="step"><div class="num">{i}</div><div>'
                        f'<div class="stitle">{html.escape(s["title"])}</div>{note}'
                        f'<div class="stags">{s["prio"]} · '
                        f'{" · ".join(tags) if tags else "no label"}</div></div></div>')
        rest = ", ".join(f"{n} {st}" for st, n in sorted(counts.items())
                         if st not in ("doing", "todo"))
        inner = "".join(rows) + (
            f'<div class="rest">Also on the board and deliberately not shown here: {rest}. '
            f'Full list in tasks.md.</div>' if rest else "")
    else:
        inner = ('<div class="gap">no task is `doing` or `todo` — either the work has not '
                 'been broken down yet, or everything is waiting on someone else</div>')
    secs.append(f'<div class="sec"><h2>What I would do next</h2>{inner}</div>')

    # ── sources ──────────────────────────────────────────────────────────────────────────────
    srcs = cite_list_html()
    if srcs:
        secs.append(f'<div class="sec"><h2>Sources</h2>{srcs}</div>')
    else:
        secs.append('<div class="sec"><h2>Sources</h2><div class="gap">nothing on this page '
                    'is attributed — every claim about what someone said needs a '
                    '<code>^[who · where · when]</code> tag, or the mark '
                    '<code>^[inferred]</code></div></div>')

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Project brief — {html.escape(PROJECT_NAME)}</title>
{FONT_LINK}<style>{CSS}{PAGE_CSS}</style></head><body>
<div class="wrap">
<div class="top">
  <div class="kicker">{html.escape(PROJECT_NAME)} · preliminary brief</div>
  <h1>What I understand, and what I do not</h1>
  <div class="approval {state}">
    <span class="state">{html.escape(words[0])}</span>
    <span class="what">{words[1]}</span>
  </div>
  <div class="meta">for {html.escape(OWNER)} · generated {stamp} from
    <code>brain/project-brief.md</code>, <code>brain/open-questions.md</code>,
    <code>brain/plan.md</code> and <code>brain/tasks.md</code> — regenerate with
    <code>python3 brain/brief.py</code>. The files are the truth; this page is a projection.</div>
</div>

{"".join(secs)}

<div class="footnote"><b>How to read the small blue numbers.</b> Every claim that came from
outside this repo carries one. Hover it for who said it and when; click it for the recording,
the thread or the message. A claim marked <span class="cite inferred">inferred</span> is mine,
not theirs — those are the ones to check first.</div>
</div>
<div id="tip"></div>
<script>{TIP_JS}</script></body></html>"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--open", action="store_true")
    args = ap.parse_args()

    OUT.write_text(build(), encoding="utf-8")
    state, detail = status()
    _, empty = brief_body()
    qs, (steps, _) = unknowns(), next_steps()
    print(f"brain/brief.html  ·  {state}{' · ' + detail if state == 'approved' else ''}")
    print(f"  {len(qs)} open question(s) · {len(steps)} next step(s) · "
          f"{len(empty)} unwritten section(s)")
    if empty:
        print("  unwritten: " + ", ".join(empty))
    if args.open:
        subprocess.run(["open", str(OUT)], check=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
