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

    the brief        brain/project-brief.md    (prose sections, and the design-brief
                                               questions with their answers)
    the unknowns     brain/open-questions.md   (## Open, with each question's owner)
    the plan         brain/plan.md + the decision that holds the current stage's exit bar
    next steps       brain/tasks.md            (doing and todo, by priority)
    the sources      every `^[…]` citation on the page, collected as it renders

**Citations are the quiet part.** `AGENTS.md` requires a claim about what a client said to
carry who said it and when. Printed inline that requirement destroys the document — the owner
reads provenance instead of the argument. So `feed.py` renders a `^[who · where · when](url)`
tag as a faint superscript numeral: invisible while reading, one hover from the transcript,
and listed in full at the foot of the page. An unsourced guess is written `^[inferred]` and
renders as a small dashed tag, because a guess that reads like a quote is the failure this
whole apparatus exists to prevent.

**Every design question shows its state at a glance.** A question answered from a source, an
answer that is only inferred, a question nobody has answered, and one that does not apply each
get their own mark, and the side navigation counts what is missing per section. Key questions
left unanswered raise a call for a kickoff workshop, with the agenda ready to copy.

**The owner can answer on the page.** A missing question has a field under it, and an inferred
answer can be confirmed or corrected. Replies stay in the browser (`localStorage`) until he
copies them as one block and pastes it into the session, which routes each into the brief;
the same contract as `review.py`. A reply whose question is no longer open is dropped. The
question list itself lives in `.claude/skills/brief/questions.md`.

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


QUESTION = re.compile(r"^-\s+(★\s*)?\*\*(.+?)\*\*[ \t]*(.*)$")
OWNER_TAG = re.compile(r"\*\*\[([^\]]+)\]\*\*")
PLACEHOLDER = re.compile(r"\*\(.*?\)\*", re.S)


def slug(title: str) -> str:
    return "s-" + re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def q_state(answer: str) -> str:
    """answered · inferred · missing · na, read from how the answer is written
    (`.claude/skills/brief/questions.md` has the convention)."""
    a = answer.strip()
    if re.match(r"^n/?a\b", a, re.I):
        return "na"
    if not a or a.startswith("?"):
        return "missing"
    if "^[inferred]" in a:
        return "inferred"
    return "answered"


def sections() -> list[dict]:
    """The brief, section by section: its prose, its unwritten sub-sections, and its questions.

    A `##` section can hold prose with `###` sub-sections (Overview, Working arrangements),
    design questions written as bullets, or the single line `n/a — why`."""
    text = (BRAIN / "project-brief.md").read_text(encoding="utf-8")
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"^#\s+.*$", "", text, count=1, flags=re.M)
    text = re.sub(r"^Status:.*$", "", text, count=1, flags=re.M)
    text = re.sub(r"^\*Stable facts.*?\*\s*$", "", text, count=1, flags=re.M | re.S)

    out = []
    for m in re.finditer(r"^##\s+(.+?)\s*\n(.*?)(?=^##\s|\Z)", text, re.M | re.S):
        title, body = m.group(1).strip(), m.group(2).strip()
        sec = {"title": title, "id": slug(title), "na": "", "questions": [], "prose": "",
               "gaps": []}
        na = re.match(r"^n/?a\b\s*[—:-]*\s*(.*)$", body, re.I | re.S)
        if na and not body.startswith("-"):
            sec["na"] = na.group(1).strip() or "not applicable"
            out.append(sec)
            continue

        prose, cur = [], None
        for line in body.splitlines():
            q = QUESTION.match(line)
            if q:
                cur = {"key": bool(q.group(1)), "q": q.group(2).strip(),
                       "a": q.group(3).strip()}
                sec["questions"].append(cur)
            elif cur and line.startswith((" ", "\t")) and line.strip():
                cur["a"] = (cur["a"] + " " + line.strip()).strip()
            else:
                cur = None
                prose.append(line)
        for qd in sec["questions"]:
            qd["state"] = q_state(qd["a"])
            own = OWNER_TAG.search(qd["a"])
            qd["owner"] = own.group(1) if own else ""
            qd["a"] = OWNER_TAG.sub("", qd["a"]).strip()
            if qd["state"] == "missing":
                qd["a"] = qd["a"].lstrip("?").strip()
            elif qd["state"] == "na":
                qd["a"] = re.sub(r"^n/?a\b\s*[—:-]*\s*", "", qd["a"], flags=re.I)

        prose_text = "\n".join(prose).strip()
        subs = list(re.finditer(r"^###\s+(.+?)\s*\n(.*?)(?=^###\s|\Z)", prose_text,
                                re.M | re.S))
        for sm in subs:
            sb = sm.group(2).strip()
            if not sb or PLACEHOLDER.fullmatch(sb):
                sec["gaps"].append(sm.group(1).strip())
        if not subs and not sec["questions"] and (not prose_text
                                                   or PLACEHOLDER.fullmatch(prose_text)):
            sec["gaps"].append(title)
        # Drop the template's parenthetical prompts from what renders; the gap says it instead.
        prose_text = re.sub(r"^###\s+(.+?)\s*\n\s*\*\(.*?\)\*\s*(?=^###|\Z)", "",
                            prose_text, flags=re.M | re.S)
        sec["prose"] = PLACEHOLDER.sub("", prose_text).strip() if PLACEHOLDER.fullmatch(
            prose_text.strip() or "x") else prose_text
        out.append(sec)
    return out


def tally(secs: list[dict]) -> dict:
    t = {"answered": 0, "inferred": 0, "missing": 0, "na": 0, "key_missing": []}
    for sec in secs:
        for q in sec["questions"]:
            t[q["state"]] += 1
            if q["state"] == "missing" and q["key"]:
                t["key_missing"].append((sec["title"], q))
    return t


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

GEIST_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link rel="stylesheet" referrerpolicy="no-referrer" '
    'href="https://fonts.googleapis.com/css2?family=Geist:wght@100..900&display=swap">'
)

# The brief is a page that is *used*: brain/lenses/house.md, section 2. The feed's stylesheet is
# loaded first for the parts this page shares with it (citations, the tooltip, the stage strip
# and the exit-bar conditions); its tokens are then remapped onto the document palette, and
# everything below is this page's own.
PAGE_CSS = """
:root{
  /* the feed's tokens, remapped: one typeface, ink and grey, red only for "needed" */
  --sans:"Geist","Helvetica Neue",Arial,sans-serif; --mono:var(--sans);
  --ink:#0a0a0a; --ink-2:#0a0a0a; --ink-3:#737373; --ink-4:#9b9b9b;
  --rule:#dedede; --rule-soft:#dedede; --wash:rgb(241,241,239);
  --blue:#0a0a0a; --blue-wash:rgb(241,241,239); --ochre:#737373; --ochre-wash:#dedede;
  --green:#0a0a0a; --green-wash:rgb(241,241,239); --red:#c8102e;

  /* the document style */
  --muted:#737373; --hair:#dedede; --paper:#ffffff;
  --fill:rgb(241,241,239); --fill-hover:rgb(235,235,232);
  --field-line:#8a8a8a; --guess-line:#9a9a9a; --need:#c8102e;
  --track:-0.012em; --track-big:-0.035em;
  --cols:180px 1fr 170px; --gap:48px; --side:56px; --max:1200px;
  --body:16px; --q:20px; --small:13px; --lede:30px; --band-t:30px;
  --row-pad:80px; --field-pad:18px; --tap:52px; --measure:600px; --sec-gap:160px;
  --bar-h:81px;
}
*{box-sizing:border-box}
html,body{background:var(--paper)}
body{margin:0;font-family:var(--sans);color:var(--ink);font-size:var(--body);line-height:1.5;
  letter-spacing:var(--track);-webkit-font-smoothing:antialiased}
h1,h2,h3,p{margin:0;font-weight:inherit;letter-spacing:inherit}
.muted{color:var(--muted)}
.num{font-variant-numeric:tabular-nums}
button{font:inherit;letter-spacing:inherit;color:inherit;background:none;border:0;cursor:pointer;
  padding:0}
code{font-family:var(--sans);font-size:.94em;background:var(--fill);padding:1px 5px;
  border-radius:0}
a{color:inherit;text-decoration:underline;text-decoration-color:var(--hair);
  text-underline-offset:3px}
.row{display:grid;grid-template-columns:var(--cols);column-gap:var(--gap)}
.span{grid-column:2 / 4}

/* buttons: black for the main action, an ink outline for the alternative */
.btn{display:inline-flex;align-items:center;justify-content:center;min-height:44px;
  padding:0 20px;border:1px solid var(--ink);font-size:var(--small);font-weight:500}
.btn.primary{background:var(--ink);color:#fff}
.btn[disabled]{opacity:.35;cursor:default}
.btn:focus-visible,.field:focus-visible{outline:2px solid var(--ink);outline-offset:2px}

/* top bar: what this is, how much is left, the one action */
.bar{position:sticky;top:0;z-index:20;background:var(--paper);border-bottom:1px solid var(--hair)}
.bar-in{max-width:var(--max);margin:0 auto;padding:18px var(--side);display:grid;
  grid-template-columns:180px 1fr auto;column-gap:var(--gap);align-items:center;
  font-size:var(--small)}
.bar .where{font-weight:560}
.bar .prog{display:flex;align-items:center;gap:12px}
.bar .track{flex:1;height:2px;background:var(--hair);position:relative;max-width:360px}
.bar .track i{position:absolute;inset:0 auto 0 0;background:var(--ink);transition:width .3s}
.bar .r{display:flex;justify-content:flex-end;gap:8px;white-space:nowrap}

.wrap{max-width:var(--max);margin:0 auto;padding:72px var(--side) 200px}

/* page head: same pattern as the printed documents */
.head{border-top:1.5px solid var(--ink);padding-top:12px;font-size:var(--small)}
.head b{font-weight:560}
.head .r{text-align:right}
.head .state.draft{color:var(--ink)}
.head .state.unset{color:var(--need)}
.lede{font-size:var(--lede);line-height:1.22;letter-spacing:-0.03em;margin-top:96px;
  max-width:760px}
.how{margin-top:28px;font-size:17px;line-height:1.6;color:#333;max-width:640px}
.key{display:flex;flex-wrap:wrap;gap:14px 36px;margin-top:36px;font-size:var(--small);
  color:var(--muted)}
.key span{display:inline-flex;align-items:center;gap:8px}
.sw{width:34px;height:18px;display:inline-block}
.sw.f{background:var(--fill);border-bottom:1.5px solid var(--field-line)}
.sw.g{border:1.5px dashed var(--guess-line)}
.sw.d{background:var(--paper);border-bottom:1.5px solid var(--ink)}

/* contents: every section with what is left in it */
.toc{margin-top:96px}
.toc .h{border-top:1.5px solid var(--ink);padding:12px 0 14px;font-size:var(--small)}
.toc .h b{font-weight:560}
.toc a.row{padding:13px 0;border-top:1px solid var(--hair);text-decoration:none;
  align-items:baseline}
.toc a.row:hover .t{text-decoration:underline;text-underline-offset:3px}
.toc .n{font-size:var(--small);color:var(--muted)}
.toc .r{text-align:right;font-size:var(--small);color:var(--muted)}
.toc .r .need{color:var(--need)}
.toc .filter{margin-top:20px;display:flex;gap:10px;flex-wrap:wrap}

/* sections: a band that sticks, a rule that closes */
.sec{margin-top:var(--sec-gap);scroll-margin-top:var(--bar-h)}
.band{position:sticky;top:var(--bar-h);z-index:10;background:var(--paper);
  border-top:1.5px solid var(--ink);border-bottom:1px solid var(--hair);padding:18px 0 28px}
.band .n{font-weight:560;font-size:var(--small)}
.band .t{font-size:var(--band-t);letter-spacing:-0.03em;line-height:1.2;font-weight:500}
.band .s{color:var(--muted);font-size:var(--small);margin-top:2px}
.band .r{text-align:right;font-size:var(--small)}
.mini{display:block;height:2px;background:var(--hair);margin-top:8px;position:relative}
.mini i{position:absolute;inset:0 auto 0 0;background:var(--ink)}
.end{border-top:1.5px solid var(--ink);margin-top:24px;padding-top:14px;font-size:var(--small);
  color:var(--muted)}

/* a question */
.q{padding:var(--row-pad) 0;border-top:1px solid var(--hair)}
.q:first-of-type{border-top:0}
.q .qn{font-size:var(--small);color:var(--muted);padding-top:3px}
.q h3{font-size:var(--q);font-weight:520;line-height:1.35;letter-spacing:-0.015em;
  max-width:var(--measure)}
.q .help{color:var(--muted);font-size:15.5px;margin-top:8px;max-width:var(--measure)}
.q .ctl{margin-top:28px;max-width:var(--measure)}
.q .ans{font-size:17px;line-height:1.55}
.q .st{text-align:right;font-size:var(--small);padding-top:3px}
.q.na h3,.q.na .ans{color:var(--muted)}
/* Status is a tag: a tint, a darker word and an icon, so what needs the owner scans at a
   glance. The one place colour is allowed besides red: brain/lenses/house.md, section 2.6.
   brain/workshop/form.html carries the same tags. */
.tag{display:inline-flex;align-items:center;gap:6px;padding:4px 9px 4px 7px;font-size:var(--small);
  font-weight:500;line-height:1.25;letter-spacing:0;white-space:nowrap;background:var(--fill);color:#5c5c5c}
.tag::before{content:"";width:14px;height:14px;flex:none;background:currentColor;
  -webkit-mask:var(--icon) center/contain no-repeat;mask:var(--icon) center/contain no-repeat}
.tag.t-open{--icon:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Ccircle cx='8' cy='8' r='6' fill='none' stroke='black' stroke-width='1.6'/%3E%3C/svg%3E")}
.tag.t-need{background:#fbe7ea;color:#b00d28;
  --icon:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Ccircle cx='8' cy='8' r='6.2' fill='none' stroke='black' stroke-width='1.6'/%3E%3Cpath d='M8 4.7v4' stroke='black' stroke-width='1.8' stroke-linecap='round'/%3E%3Ccircle cx='8' cy='11.1' r='1.05'/%3E%3C/svg%3E")}
.tag.t-guess{background:#f8eedb;color:#80520e;
  --icon:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Ccircle cx='8' cy='8' r='6' fill='none' stroke='black' stroke-width='1.6' stroke-dasharray='2.4 2.1'/%3E%3C/svg%3E")}
.tag.t-done{background:#e4f1e8;color:#17663a;
  --icon:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Ccircle cx='8' cy='8' r='6.2' fill='none' stroke='black' stroke-width='1.6'/%3E%3Cpath d='M5.2 8.3l1.9 1.9 3.7-3.9' fill='none' stroke='black' stroke-width='1.7' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E")}
.tag.t-na{background:none;color:var(--muted);padding-left:0;
  --icon:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M4 8h8' stroke='black' stroke-width='1.6' stroke-linecap='round'/%3E%3C/svg%3E")}
.who{display:block;color:var(--muted);margin-top:4px}

/* a field: the fill means "write here" */
.field{display:block;width:100%;background:var(--fill);border:0;
  border-bottom:1.5px solid var(--field-line);padding:var(--field-pad) 14px;font:inherit;
  font-size:var(--body);letter-spacing:var(--track);color:var(--ink);resize:vertical;
  min-height:120px;border-radius:0}
.field::placeholder{color:#9b9b9b}
.field:hover{background:var(--fill-hover)}
.field:focus{outline:none;background:var(--paper);border-bottom:2px solid var(--ink);
  box-shadow:inset 0 0 0 1px var(--ink)}
.field.filled{background:var(--paper);border-bottom-color:var(--ink)}
.saved{font-size:var(--small);color:var(--muted);margin-top:6px;min-height:18px}

/* my guess: dashed, with two real buttons */
.guess{border:1.5px dashed var(--guess-line);padding:22px 24px}
.guess .lbl{font-size:var(--small);color:var(--muted)}
.guess .txt{font-size:17px;margin-top:4px}
.guess .acts{display:flex;gap:12px;margin-top:22px;flex-wrap:wrap}
.guess.kept{border-style:solid;border-color:var(--ink)}
.guess.kept .lbl::after{content:" · kept";color:var(--ink)}
.guess.changing .acts,.guess.changing .txt{display:none}
.guess.changing{border:0;padding:0}
.guess.changing .lbl{margin-bottom:8px}

/* kickoff: the needed questions, and the agenda to copy */
.kick .lede2{font-size:22px;line-height:1.35;letter-spacing:-0.02em;max-width:var(--measure)}
.kick blockquote{margin:28px 0 0;padding:0 0 0 18px;border-left:1.5px solid var(--ink);
  font-size:17px;line-height:1.55;max-width:var(--measure)}
.kick .list{margin-top:44px}
.kick .li{padding:13px 0;border-top:1px solid var(--hair);align-items:baseline}
.kick .li .n{font-size:var(--small);color:var(--muted)}
.kick .li .r{text-align:right;font-size:var(--small);color:var(--muted)}
.kick .acts{margin-top:28px;display:flex;gap:12px;flex-wrap:wrap;align-items:center}
.kick .acts .muted{font-size:var(--small);max-width:420px}

/* read-only rows: prose, other questions, next steps */
.rrow{padding:22px 0;border-top:1px solid var(--hair)}
.rrow:first-of-type{border-top:0}
.rrow .l{font-size:var(--small);color:var(--muted);padding-top:3px}
.rrow .body{max-width:680px;font-size:var(--body);line-height:1.6}
.rrow .body p+p{margin-top:10px}
.rrow .r{text-align:right;font-size:var(--small);color:var(--muted)}
.rrow .r.need{color:var(--need)}
.rrow .sub{color:var(--muted);font-size:var(--small);margin-top:4px}
.gapline{color:var(--muted)}

/* the parts shared with the feed, brought into this register */
.stages{margin:28px 0 36px}
.stage b,.cond .dot{font-family:var(--sans)}
.cond .status,.stage b{letter-spacing:0;text-transform:none;font-size:var(--small);
  font-weight:500}
.cite.inferred{font-family:var(--sans);text-transform:none;letter-spacing:0;color:var(--muted);
  border:1px dashed var(--guess-line);padding:0 4px;font-size:.7em}
a.ref.cite{color:var(--muted);text-decoration:none}
.srclist{font-size:var(--small)}
#tip .k{font-family:var(--sans);text-transform:none;letter-spacing:0}

.hidden{display:none !important}
body.only-mine .q.done,body.only-mine .q.na,body.only-mine .readonly{display:none}

@media (max-width:760px){
  :root{--side:20px;--gap:0px;--lede:24px;--row-pad:40px;--sec-gap:110px;--band-t:24px;
    --bar-h:99px}
  .row{grid-template-columns:1fr}
  .span{grid-column:1}
  .bar-in{grid-template-columns:1fr auto;row-gap:8px}
  .bar .prog{grid-column:1 / 3;grid-row:2}
  .head .r{text-align:left;margin-top:8px}
  .band .r{text-align:left;margin-top:6px}
  .q .qn{padding-top:0;margin-bottom:4px}
  .q .ctl{margin-top:20px}
  .q .st{text-align:left;margin-top:12px}
  .toc .r,.rrow .r,.kick .li .r{text-align:left}
  .lede{margin-top:56px}
}
"""


PAGE_JS = r"""
(function(){
  // The section bands stick under the top bar, whose height changes with the screen.
  var barEl = document.querySelector('.bar');
  function barH(){ document.documentElement.style.setProperty('--bar-h', barEl.offsetHeight + 'px'); }
  barH(); window.addEventListener('resize', barH);

  var KEY = 'brief-replies:' + document.title, store = {};
  try { store = JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) { store = {}; }
  var qs = document.querySelectorAll('.q[data-qid]');
  var live = {};
  qs.forEach(function(q){ live[q.dataset.qid] = q; });
  // A reply whose question is no longer open here (answered since, or removed) is dropped.
  Object.keys(store).forEach(function(k){ if (!live[k]) delete store[k]; });
  function save(){ try { localStorage.setItem(KEY, JSON.stringify(store)); } catch (e) {} }

  var copyBtn = document.getElementById('copy'), clearBtn = document.getElementById('clear');
  var base = +document.body.dataset.answered, total = +document.body.dataset.total;

  function status(q){
    var st = q.querySelector('.st .tag'), v = store[q.dataset.qid];
    if (!st) return;
    if (v) { st.className = 'tag t-done'; st.textContent = v.ok ? 'Kept' : 'Answered'; }
    else { st.className = 'tag ' + st.dataset.c; st.textContent = st.dataset.t; }
  }
  function refresh(){
    var n = Object.keys(store).length, done = base + n;
    document.getElementById('prog-n').textContent = done + ' of ' + total + ' answered';
    document.getElementById('prog-i').style.width = (total ? 100 * done / total : 0) + '%';
    copyBtn.textContent = n ? 'Copy ' + n + (n === 1 ? ' reply' : ' replies') : 'Copy replies';
    copyBtn.disabled = n === 0;
    clearBtn.classList.toggle('hidden', n === 0);
    document.querySelectorAll('.sec[data-total]').forEach(function(s){
      var t = +s.dataset.total, d = +s.dataset.done;
      s.querySelectorAll('.q[data-qid]').forEach(function(q){ if (store[q.dataset.qid]) d++; });
      var c = s.querySelector('.band .cnt'); if (c) c.textContent = d + ' of ' + t;
      var m = s.querySelector('.band .mini i'); if (m) m.style.width = (t ? 100 * d / t : 0) + '%';
    });
  }
  function grow(t){ t.style.height = 'auto'; t.style.height = Math.max(120, t.scrollHeight + 4) + 'px'; }
  var timers = {};
  function said(q){
    var s = q.querySelector('.saved'); if (!s) return;
    s.textContent = 'Saving…'; clearTimeout(timers[q.dataset.qid]);
    timers[q.dataset.qid] = setTimeout(function(){ s.textContent = store[q.dataset.qid] ? 'Saved' : ''; }, 500);
  }

  qs.forEach(function(q){
    var id = q.dataset.qid, f = q.querySelector('textarea.field'), g = q.querySelector('.guess');
    function set(v){
      if (v && (v.ok || (v.text && v.text.trim()))) store[id] = v; else delete store[id];
      save(); status(q); refresh(); said(q);
    }
    var v = store[id];
    if (v) {
      if (g && v.ok) g.classList.add('kept');
      if (v.text) { if (g) g.classList.add('changing'); f.classList.remove('hidden'); f.value = v.text;
        f.classList.add('filled'); setTimeout(function(){ grow(f); }, 0); }
      status(q); q.querySelector('.saved').textContent = 'Saved';
    }
    if (f) f.addEventListener('input', function(){
      grow(f); f.classList.toggle('filled', !!f.value.trim());
      set(f.value.trim() ? {text: f.value} : (g ? null : null));
    });
    if (g) {
      g.querySelector('[data-act=keep]').addEventListener('click', function(){
        var on = !g.classList.contains('kept');
        g.classList.toggle('kept', on); set(on ? {ok: true} : null);
      });
      g.querySelector('[data-act=change]').addEventListener('click', function(){
        g.classList.remove('kept'); g.classList.add('changing');
        f.classList.remove('hidden'); f.value = g.dataset.was; grow(f); f.focus();
        set(null);
      });
    }
  });

  function block(){
    var d = new Date().toISOString().slice(0, 10), lines = [], i = 0;
    lines.push('Brief replies — ' + document.body.dataset.project + ' · ' + d);
    lines.push('Route each into brain/project-brief.md, cited ^[' + document.body.dataset.owner +
               ' · brief page · ' + d + '].');
    qs.forEach(function(q){
      var v = store[q.dataset.qid]; if (!v) return;
      i++; lines.push('');
      if (q.dataset.state === 'inferred') {
        lines.push(i + '. ' + q.dataset.sec + ' — ' + q.dataset.q + ' (inferred: "' + q.dataset.was + '")');
        lines.push(v.ok ? '   Confirmed.' : '   Correction: ' + v.text.trim().replace(/\n+/g, ' '));
      } else {
        lines.push(i + '. ' + q.dataset.sec + ' — ' + q.dataset.q);
        lines.push('   Answer: ' + v.text.trim().replace(/\n+/g, ' '));
      }
    });
    return lines.join('\n');
  }
  function flash(btn, txt, back){
    btn.textContent = txt; setTimeout(function(){ btn.textContent = back(); }, 2200);
  }
  copyBtn.addEventListener('click', function(){
    var t = block();
    if (navigator.clipboard) navigator.clipboard.writeText(t).then(function(){
      flash(copyBtn, 'Copied. Paste it into the session', function(){
        var n = Object.keys(store).length; return 'Copy ' + n + (n === 1 ? ' reply' : ' replies'); });
    }, function(){});
  });
  clearBtn.addEventListener('click', function(){
    store = {}; save();
    qs.forEach(function(q){
      var f = q.querySelector('textarea.field'), g = q.querySelector('.guess');
      if (g) { g.classList.remove('kept', 'changing'); if (f) f.classList.add('hidden'); }
      if (f) { f.value = ''; f.classList.remove('filled'); }
      var s = q.querySelector('.saved'); if (s) s.textContent = '';
      status(q);
    });
    refresh();
  });

  var only = document.getElementById('only');
  if (only) only.addEventListener('click', function(){
    var on = document.body.classList.toggle('only-mine');
    only.textContent = on ? 'Show everything' : 'Show only what needs you';
  });

  var ag = document.getElementById('copy-agenda');
  if (ag) ag.addEventListener('click', function(){
    if (navigator.clipboard) navigator.clipboard.writeText(document.getElementById('agenda').value)
      .then(function(){ flash(ag, 'Copied', function(){ return 'Copy the agenda'; }); }, function(){});
  });

  refresh();
})();
"""

OPENING = ("Describe the experience you want a customer to have, from first seeing the brand to "
           "completing their most important task. What should they feel, understand and be "
           "able to do?")

STATUS = {  # state -> (tag class, words)
    "answered": ("t-done", "Answered"),
    "inferred": ("t-guess", "My guess"),
    "missing": ("t-open", "Open"),
    "need": ("t-need", "Needed to start"),
    "na": ("t-na", "Not applicable"),
}


def inline(md: str, g: dict) -> str:
    """`render_md` without its paragraph wrapper, for text that sits inside a line."""
    out = render_md(md, g).strip()
    m = re.fullmatch(r"<p>(.*)</p>", out, re.S)
    return m.group(1) if m and "<p>" not in m.group(1) else out


def plain(md: str) -> str:
    """Markdown down to plain text, for the copyable agenda and the replies."""
    t = re.sub(r"\^\[[^\]]*\](\([^)]*\))?", "", md)
    t = re.sub(r"\*\*|__|`", "", t)
    return " ".join(t.split())


def long_date(d: datetime) -> str:
    return f"{d.day} {d.strftime('%B %Y')}"


def build() -> str:
    cite_reset()                      # numbering is per page, and this page is built once
    g = glossary()
    state, detail = status()
    brief_secs = sections()
    t = tally(brief_secs)
    qs = unknowns()
    steps, counts = next_steps()
    plan_text = (BRAIN / "plan.md").read_text(encoding="utf-8")
    strip, _here = stage_strip(plan_text)
    bars = bar_conditions()
    now = datetime.now()
    total = t["answered"] + t["inferred"] + t["missing"]      # n/a is not asked of anyone
    answered = t["answered"]
    esc = html.escape

    head_state = {
        "draft": ("draft", "Draft · awaiting your approval"),
        "approved": ("approved", detail[:1].upper() + detail[1:]),
        "unset": ("unset", "No status line: never agreed"),
    }[state]

    # ── contents ─────────────────────────────────────────────────────────────────────────────
    toc, out_secs = [], []
    n_sec = 0
    design = [s for s in brief_secs if s["questions"] or s["na"]]
    for sec in brief_secs:
        n_sec += 1
        sec["n"] = n_sec
        qn = [q for q in sec["questions"] if q["state"] != "na"]
        done = sum(1 for q in qn if q["state"] == "answered")
        need = sum(1 for q in qn if q["state"] == "missing" and q["key"])
        sec["done"], sec["total"], sec["need"] = done, len(qn), need
        if sec["na"]:
            right = "Not applicable"
        elif sec["questions"]:
            right = f"{done} of {len(qn)} answered" + (
                f' · <span class="need">{need} needed</span>' if need else "")
        else:
            right = (f'{len(sec["gaps"])} not written' if sec["gaps"] else "Written")
        toc.append(f'<a class="row" href="#{sec["id"]}"><span class="n">{n_sec}</span>'
                   f'<span class="t">{esc(sec["title"])}</span><span class="r">{right}</span></a>')
    work = [("s-open", "Other open questions", f"{len(qs)} open" if qs else "None recorded"),
            ("s-plan", "The plan", "Exit bar set" if bars else
             '<span class="need">No exit bar</span>'),
            ("s-next", "What I would do next", f"{len(steps)} steps" if steps else "None"),
            ("s-sources", "Sources", "")]
    for i, (sid, title, right) in enumerate(work):
        toc.append(f'<a class="row" href="#{sid}"><span class="n">{n_sec + i + 1}</span>'
                   f'<span class="t">{esc(title)}</span><span class="r">{right}</span></a>')

    # ── the kickoff call ─────────────────────────────────────────────────────────────────────
    kick = ""
    if t["key_missing"]:
        km = t["key_missing"]
        missing_all = [(sec, q) for sec in brief_secs for q in sec["questions"]
                       if q["state"] == "missing"]
        ordered = ([x for x in missing_all if x[1]["key"]]
                   + [x for x in missing_all if not x[1]["key"]])
        agenda = [f"Kickoff — {PROJECT_NAME}", "", "Opening question:", OPENING]
        last = None
        for i, (sec, q) in enumerate(ordered):
            if i == len(km):
                agenda += ["", "If there is time:"]
                last = None
            if sec["title"] != last:
                agenda += ["", sec["title"].upper()]
                last = sec["title"]
            agenda.append(f"- {plain(q['q'])}" + (f" ({q['owner']})" if q["owner"] else ""))
        kick = "pending"  # the rows need the question numbers, which the loop below assigns
    # ── the brief, section by section ────────────────────────────────────────────────────────
    for sec in brief_secs:
        qrows = []
        for j, q in enumerate(sec["questions"], 1):
            q["num"] = f'{sec["n"]}.{j}'
            st = q["state"]
            need = st == "missing" and q["key"]
            cls, words = STATUS["need" if need else st]
            who = (f'<span class="who">{esc(q["owner"])} can answer</span>'
                   if q["owner"] and st == "missing" else "")
            attrs = ""
            if st in ("missing", "inferred"):
                qid = re.sub(r"[^a-z0-9]+", "-", f'{sec["title"]} {plain(q["q"])}'.lower())[:90]
                attrs = (f' data-qid="{qid}" data-sec="{esc(sec["title"])}" '
                         f'data-q="{esc(plain(q["q"]))}" data-state="{st}" '
                         f'data-was="{esc(plain(q["a"]))}"')
            if st == "answered":
                ctl = f'<div class="ans">{inline(q["a"], g)}</div>'
                help_ = ""
            elif st == "inferred":
                was = esc(plain(q["a"]))
                ctl = (f'<div class="guess" data-was="{was}"><div class="lbl">My guess</div>'
                       f'<div class="txt">{inline(q["a"].replace("^[inferred]", ""), g)}</div>'
                       f'<div class="acts"><button type="button" class="btn primary" '
                       f'data-act="keep">Keep it</button><button type="button" class="btn" '
                       f'data-act="change">Change it</button></div></div>'
                       f'<textarea class="field hidden" aria-label="Your answer"></textarea>'
                       f'<div class="saved"></div>')
                help_ = ""
            elif st == "missing":
                ctl = ('<textarea class="field" placeholder="Type the answer, if you know it" '
                       'aria-label="Your answer"></textarea><div class="saved"></div>')
                help_ = (f'<p class="help">{inline(q["a"], g)}</p>' if q["a"] else "")
            else:
                ctl = (f'<div class="ans">Not applicable'
                       + (f' — {inline(q["a"], g)}' if q["a"] else "") + '</div>')
                help_ = ""
            done_cls = " done" if st == "answered" else ""
            qrows.append(
                f'<div class="row q {st}{done_cls}"{attrs}><span class="qn">{q["num"]}</span>'
                f'<div><h3>{inline(q["q"], g)}</h3>{help_}<div class="ctl">{ctl}</div></div>'
                f'<div class="st"><span class="tag {cls}" data-c="{cls}" data-t="{words}">'
                f'{words}</span>{who}</div></div>')

        nxt = (brief_secs[sec["n"]].get("title") if sec["n"] < len(brief_secs)
               else "Other open questions")
        if sec["na"]:
            body = (f'<div class="row rrow"><span class="l"></span><div class="body muted">'
                    f'Not applicable — {inline(sec["na"], g)}</div><span></span></div>')
            sub, right, data = "Considered, and left out", "", ""
        elif sec["questions"]:
            body = "".join(qrows)
            sub = (f'{sec["total"]} question{"s" if sec["total"] != 1 else ""}'
                   + (f' · <span style="color:var(--need)">{sec["need"]} needed to start</span>'
                      if sec["need"] else ""))
            pct = 100 * sec["done"] / sec["total"] if sec["total"] else 100
            right = (f'<span class="cnt num">{sec["done"]} of {sec["total"]}</span>'
                     f'<span class="mini"><i style="width:{pct:.0f}%"></i></span>')
            data = f' data-total="{sec["total"]}" data-done="{sec["done"]}"'
        else:
            rows = []
            subs = list(re.finditer(r"^###\s+(.+?)\s*\n(.*?)(?=^###\s|\Z)", sec["prose"],
                                    re.M | re.S))
            if subs:
                for sm in subs:
                    rows.append(f'<div class="row rrow"><span class="l">{esc(sm.group(1))}</span>'
                                f'<div class="body">{render_md(sm.group(2).strip(), g)}</div>'
                                f'<span class="r">Written</span></div>')
            elif sec["prose"].strip():
                rows.append(f'<div class="row rrow"><span class="l"></span><div class="body">'
                            f'{render_md(sec["prose"], g)}</div><span></span></div>')
            for gap in sec["gaps"]:
                rows.append(f'<div class="row rrow"><span class="l">{esc(gap)}</span>'
                            f'<div class="body gapline">Not written yet</div>'
                            f'<span class="r">Open</span></div>')
            body = "".join(rows)
            sub = (f'{len(sec["gaps"])} part{"s" if len(sec["gaps"]) != 1 else ""} not written'
                   if sec["gaps"] else "Written")
            right, data = "", ""
        ro = " readonly" if not sec["questions"] else ""
        out_secs.append(
            f'<section class="sec{ro}" id="{sec["id"]}"{data}><div class="band row">'
            f'<span class="n">{sec["n"]}</span><div><div class="t">{esc(sec["title"])}</div>'
            f'<div class="s">{sub}</div></div><div class="r">{right}</div></div>{body}'
            f'<div class="end">End of {sec["n"]} · Next, {esc(nxt.lower() if nxt else "")}</div>'
            f'</section>')

    if kick:
        km = [q for sec in brief_secs for q in sec["questions"]
              if q["state"] == "missing" and q["key"]]
        rows = "".join(
            f'<div class="row li"><span class="n">{q["num"]}</span><span>{inline(q["q"], g)}'
            f'</span><span class="r">{esc(q["owner"]) + " can answer" if q["owner"] else ""}'
            f'</span></div>' for q in km)
        n = len(km)
        kick = f"""<section class="sec kick readonly" id="s-kickoff">
  <div class="band row"><span class="n">—</span><div><div class="t">Kickoff workshop</div>
  <div class="s" style="color:var(--need)">{n} question{"s" if n != 1 else ""} needed to start</div></div>
  <div class="r"></div></div>
  <div class="row rrow"><span class="l">Why</span><div class="span">
  <p class="lede2">{n} key question{"s are" if n != 1 else " is"} still unanswered, so I suggest a
  kickoff workshop to ask {"them" if n != 1 else "it"}.</p>
  <blockquote>{esc(OPENING)}</blockquote>
  <p class="muted" style="margin-top:12px;font-size:var(--small)">Open with this question. It ties
  brand, product, audience and business together before anyone talks about colours or layout.</p>
  </div></div>
  <div class="list">{rows}</div>
  <div class="row"><span></span><div class="span acts"><button type="button" class="btn primary"
  id="copy-agenda">Copy the agenda</button>
  <span class="muted">The agenda holds every open question, needed ones first. If a meeting
  is hard to get, <code>/workshop</code> sends them as questions to answer on a phone.</span></div></div>
  <textarea id="agenda" class="hidden" aria-hidden="true">{esc(chr(10).join(agenda))}</textarea>
</section>"""

    # ── the work: other questions, plan, next steps, sources ─────────────────────────────────
    base_n = len(brief_secs)

    def band(sid, n, title, sub):
        return (f'<section class="sec readonly" id="{sid}"><div class="band row">'
                f'<span class="n">{n}</span><div><div class="t">{esc(title)}</div>'
                f'<div class="s">{sub}</div></div><div class="r"></div></div>')

    if qs:
        rows = "".join(
            f'<div class="row rrow"><span class="l">{esc(q["id"])}</span>'
            f'<div class="body">{render_md(q["text"], g)}</div>'
            f'<span class="r{"" if q["owner"] else " need"}">'
            f'{esc(q["owner"]) + " can answer" if q["owner"] else "Nobody named"}</span></div>'
            for q in qs)
    else:
        rows = ('<div class="row rrow"><span class="l"></span><div class="body gapline">None '
                'recorded. A brief this early with nothing unknown has not been checked.</div>'
                '<span></span></div>')
    out_secs.append(band("s-open", base_n + 1, "Other open questions",
                         "Unknowns that are not design questions, with who can answer")
                    + rows + '<div class="end">From brain/open-questions.md</div></section>')

    blocks = []
    for bar_entry in bars:
        cells = []
        for c in bar_entry["conds"]:
            stc = c["status"]
            mark = {"met": "Met", "partly": "Partly", "not-met": "Not met"}.get(stc, "Unknown")
            ev = (f'<div class="ev">{render_md(c["evidence"], g)}</div>' if c.get("evidence")
                  else "")
            cells.append(f'<div class="cond {stc}"><div class="dot">{c["n"]}</div>'
                         f'<div><div class="claim"><span class="status">{mark}</span> '
                         f'{render_md(c["claim"], g)}</div>{ev}'
                         f'<div class="more">{render_md(c["detail"], g)}</div></div></div>')
        head = (f'{esc(bar_entry["label"])} · ' if bar_entry["label"] and len(bars) > 1 else "")
        blocks.append(f'<p style="font-weight:560;margin:24px 0 8px">{head}'
                      f'{esc(bar_entry["stage"])}: what ends it</p>' + "".join(cells))
    planbody = ("".join(blocks) if blocks else
                '<p class="gapline" style="color:var(--need)">This stage has no exit bar. Write it '
                'as a decision before the work goes further, or the stage cannot end.</p>')
    out_secs.append(band("s-plan", base_n + 2, "The plan", "The stages, and what ends this one")
                    + f'<div class="row rrow"><span class="l"></span><div class="span">'
                      f'<div class="stages">{strip}</div>{planbody}</div></div>'
                    + '<div class="end">From brain/plan.md and its decisions</div></section>')

    if steps:
        rows = []
        for i, s in enumerate(steps, 1):
            labels = " · ".join(s["labels"]) or ""
            note = f'<div class="sub">{render_md(s["note"], g)}</div>' if s["note"] else ""
            rows.append(f'<div class="row rrow"><span class="l">{i}</span><div class="body">'
                        f'<b style="font-weight:560">{esc(s["title"])}</b>{note}</div>'
                        f'<span class="r">{s["status"].capitalize()} · {s["prio"]}'
                        f'{" · " + esc(labels) if labels else ""}</span></div>')
        rest = ", ".join(f"{n} {st}" for st, n in sorted(counts.items())
                         if st not in ("doing", "todo"))
        stepbody = "".join(rows)
        endline = (f"Also on the board, not shown: {rest}. Full list in brain/tasks.md."
                   if rest else "From brain/tasks.md")
    else:
        stepbody = ('<div class="row rrow"><span class="l"></span><div class="body gapline">No '
                    'task is doing or todo. Either the work has not been broken down, or it is '
                    'all waiting on someone else.</div><span></span></div>')
        endline = "From brain/tasks.md"
    out_secs.append(band("s-next", base_n + 3, "What I would do next", "In the order to do them")
                    + stepbody + f'<div class="end">{esc(endline)}</div></section>')

    srcs = cite_list_html()
    out_secs.append(band("s-sources", base_n + 4, "Sources",
                         "Every claim from outside this repo")
                    + f'<div class="row rrow"><span class="l"></span><div class="span">'
                      + (srcs or '<p class="gapline">Nothing on this page is attributed. Every '
                                 'claim about what someone said needs a source tag, or the mark '
                                 'inferred.</p>')
                    + '</div></div></section>')

    n_open = t["missing"] + t["inferred"]
    pct = 100 * answered / total if total else 0
    no_q = ("" if total else
            '<p class="how" style="color:var(--need)">This brief has no design questions yet. '
            '<code>/brief</code> adds the ones that fit the project.</p>')

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Project brief — {esc(PROJECT_NAME)}</title>
{GEIST_LINK}<style>{CSS}{PAGE_CSS}</style></head>
<body data-project="{esc(PROJECT_NAME)}" data-owner="{esc(OWNER)}" data-answered="{answered}"
  data-total="{total}">
<header class="bar"><div class="bar-in">
  <span class="where">Brief · {esc(PROJECT_NAME)}</span>
  <span class="prog"><span class="track"><i id="prog-i" style="width:{pct:.0f}%"></i></span>
    <span class="num" id="prog-n">{answered} of {total} answered</span></span>
  <span class="r"><button type="button" class="btn hidden" id="clear">Clear</button>
    <button type="button" class="btn primary" id="copy" disabled>Copy replies</button></span>
</div></header>
<main class="wrap">
  <div class="row head">
    <span><b>Brief</b></span>
    <span><b>Engagement brief</b><br><span class="muted">{esc(PROJECT_NAME)}</span></span>
    <span class="r"><span class="state {head_state[0]}">{esc(head_state[1])}</span><br>
      <span class="muted">Generated {long_date(now)}</span></span>
  </div>
  <div class="row"><span></span><p class="lede span">What I understand about
    {esc(PROJECT_NAME)}, and what I still need from you.</p></div>
  <div class="row"><span></span><div class="span">
    <p class="how">Grey boxes are yours to fill. Dashed boxes are my guesses: keep them or change
    them. Everything saves in this browser as you type. When you are done, press
    <b style="font-weight:560">Copy replies</b> and paste them into the session; I file each one
    in the brief. Approve the brief, or tell me what is wrong, in the session.</p>{no_q}
    <div class="key"><span><i class="sw f"></i>Yours to fill</span>
      <span><i class="sw g"></i>My guess, keep or change</span>
      <span><i class="sw d"></i>Answered</span></div>
  </div></div>

  <div class="toc"><div class="row h"><b>Contents</b><span class="muted">{n_open} waiting on
    you{f" · {len(t['key_missing'])} needed to start" if t["key_missing"] else ""}</span><span></span></div>
    {"".join(toc)}
    <div class="row"><span></span><div class="filter"><button type="button" class="btn"
      id="only">Show only what needs you</button></div><span></span></div>
  </div>

  {kick}
  {"".join(out_secs)}

  <div class="row" style="margin-top:96px"><span></span><p class="muted span"
    style="font-size:var(--small)">Generated from brain/project-brief.md, brain/open-questions.md,
    brain/plan.md and brain/tasks.md. The files are the truth; this page is a projection.
    Regenerate with python3 brain/brief.py.</p></div>
</main>
<div id="tip"></div>
<script>{TIP_JS}</script><script>{PAGE_JS}</script></body></html>"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--open", action="store_true")
    args = ap.parse_args()

    OUT.write_text(build(), encoding="utf-8")
    state, detail = status()
    secs = sections()
    t = tally(secs)
    empty = [g for s in secs for g in s["gaps"]]
    qs, (steps, _) = unknowns(), next_steps()
    print(f"brain/brief.html  ·  {state}{' · ' + detail if state == 'approved' else ''}")
    print(f"  design questions: {t['answered']} answered · {t['inferred']} inferred · "
          f"{t['missing']} missing ({len(t['key_missing'])} key) · {t['na']} n/a")
    print(f"  {len(qs)} other open question(s) · {len(steps)} next step(s) · "
          f"{len(empty)} unwritten section(s)")
    if empty:
        print("  unwritten: " + ", ".join(empty))
    for title, q in t["key_missing"]:
        print(f"  key, missing: {title} — {plain(q['q'])}")
    if args.open:
        subprocess.run([sys.executable, str(BRAIN / "show.py"), str(OUT)], check=False,
                       stdout=subprocess.DEVNULL)
    return 0


if __name__ == "__main__":
    sys.exit(main())
