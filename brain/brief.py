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
renders as its own word in ochre, because a guess that reads like a quote is the failure this
whole apparatus exists to prevent.

**Every design question shows its state at a glance.** A question answered from a source, an
answer that is only inferred, a question nobody has answered, and one that does not apply each
get their own mark, and the side navigation counts what is missing per section. Key questions
left unanswered raise a call for a kickoff workshop, with the agenda ready to copy. The
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


BRIEF_CSS = """
/* Two columns on a wide screen: the navigation stays put while the brief scrolls, so the owner
   can see at any point which sections still have holes. On a phone it becomes a strip. */
.wrap{max-width:1160px}
.layout{display:grid;grid-template-columns:208px minmax(0,1fr);gap:0 64px;align-items:start}
.main{max-width:780px;min-width:0}
.nav{position:sticky;top:28px;padding-top:6px;font-size:13.5px}
.nav .navh{font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--ink-4);margin:0 0 10px}
.nav ol{list-style:none;margin:0 0 26px;padding:0}
.nav li{margin:0}
.nav a{display:flex;justify-content:space-between;gap:10px;padding:6px 0;color:var(--ink-2);
  text-decoration:none;border-bottom:1px solid var(--rule-soft)}
.nav a:hover{color:var(--ink)}
.nav a.on{color:var(--ink);font-weight:600}
.nav .n{font-family:var(--mono);font-size:11px;color:var(--ink-4);white-space:nowrap}
.nav .n.miss{color:var(--ink-2)}
.nav .n.key{color:var(--red)}
.nav .n.done{color:var(--green)}
.nav .n.na{color:var(--ink-4)}
@media (max-width:900px){
  .layout{display:block}
  .nav{position:sticky;top:0;z-index:5;background:var(--paper);margin:0 -28px;
    padding:10px 28px;border-bottom:1px solid var(--rule);overflow-x:auto;white-space:nowrap}
  .nav .navh{display:none}
  .nav ol{display:inline-flex;gap:18px;margin:0 18px 0 0}
  .nav a{border:0;padding:4px 0;gap:6px}
}

/* Coverage: one bar for the whole brief, and a legend that doubles as the filter. */
.cov{margin:30px 0 0}
.covbar{display:flex;height:8px;gap:2px}
.covbar span{display:block;min-width:2px}
.covbar .answered{background:var(--green)}
.covbar .inferred{background:var(--ochre)}
.covbar .missing{background:transparent;box-shadow:inset 0 0 0 1px var(--ink-4)}
.covbar .na{background:var(--rule)}
.legend{display:flex;flex-wrap:wrap;gap:6px 18px;margin-top:12px}
.legend button{font:inherit;font-size:13px;color:var(--ink-3);background:none;border:0;
  border-bottom:1px solid transparent;padding:3px 0;cursor:pointer;display:inline-flex;
  align-items:center;gap:7px}
.legend button:hover{color:var(--ink)}
.legend button[aria-pressed=true]{color:var(--ink);border-bottom-color:var(--ink)}
.legend b{font-weight:600;color:var(--ink)}

/* The four marks. Shape carries the state as well as colour, so it survives a grey print. */
.mk{flex:0 0 auto;width:10px;height:10px;border-radius:50%;display:inline-block}
.mk.answered{background:var(--green)}
.mk.inferred{background:linear-gradient(90deg,var(--ochre) 50%,transparent 50%);
  box-shadow:inset 0 0 0 1.5px var(--ochre)}
.mk.missing{box-shadow:inset 0 0 0 1.5px var(--ink-3)}
.mk.missing.key{box-shadow:inset 0 0 0 2px var(--red)}
.mk.na{width:10px;height:1.5px;border-radius:0;background:var(--ink-4)}

/* Kickoff call: a hairline frame in red, because key questions are blocking the work. */
.kickoff{margin:34px 0 0;padding:20px 0 22px 20px;border-left:2px solid var(--red)}
.kickoff .ov{font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;
  text-transform:uppercase;color:var(--red);margin:0 0 8px}
.kickoff h3{font-size:21px;margin:0 0 10px}
.kickoff p{font-size:15px;line-height:1.6;color:var(--ink-2);margin:0 0 12px;max-width:62ch}
.kickoff blockquote{margin:0 0 14px;padding:0 0 0 14px;border-left:1px solid var(--rule);
  font-size:15px;line-height:1.6;color:var(--ink)}
.kickoff ul{margin:0 0 14px;padding:0 0 0 18px;font-size:14.5px;line-height:1.6;
  color:var(--ink-2)}
.kickoff ul .sect{list-style:none;margin:10px 0 2px -18px;font-family:var(--mono);
  font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-4)}
.kickoff .who{color:var(--blue);font-size:13px}
.kickoff .actions{display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;font-size:13.5px;
  color:var(--ink-3)}
.kickoff button{font:inherit;font-size:13.5px;font-weight:600;color:var(--paper);
  background:var(--ink);border:0;border-radius:2px;padding:8px 14px;cursor:pointer}
.kickoff button.done{background:var(--green)}

/* A design section and its questions. */
.sechead{display:flex;justify-content:space-between;align-items:baseline;gap:16px;
  border-bottom:1px solid var(--ink);padding-bottom:11px;margin:0 0 6px}
.sec > .sechead h2{font-size:13px;font-family:var(--mono);font-weight:500;letter-spacing:.14em;
  text-transform:uppercase;color:var(--ink-3);margin:0;padding:0;border:0}
.sechead .tally{font-size:12.5px;color:var(--ink-4);white-space:nowrap}
.sechead .tally .key{color:var(--red)}
.sec{scroll-margin-top:24px}
.qa{display:flex;gap:14px;padding:15px 0;border-top:1px solid var(--rule-soft)}
.qa:first-of-type{border-top:0}
.qa .mk{margin-top:6px}
.qa .qbody{min-width:0;flex:1}
.qa .qq{font-size:14px;line-height:1.5;color:var(--ink-3)}
.qa .keytag{font-family:var(--mono);font-size:10px;letter-spacing:.12em;text-transform:uppercase;
  color:var(--ink-4);margin-left:6px;white-space:nowrap}
.qa .qans{font-size:16px;line-height:1.62;color:var(--ink);margin-top:4px}
.qa .qans p{margin:0}
.qa.missing .qq{color:var(--ink)}
.qa.missing .qans{color:var(--ink-4);font-style:italic;font-size:14.5px}
.qa.missing.key .keytag{color:var(--red)}
.qa.missing.key .qans{color:var(--red)}
.qa.inferred .qans{color:var(--ink-2)}
.qa.na{opacity:.55}
.qa.na .qans{font-size:14px;color:var(--ink-4)}
.qa .qowner{font-family:var(--mono);font-size:11px;letter-spacing:.09em;text-transform:uppercase;
  color:var(--blue);margin-top:5px}
.secna{font-size:14.5px;color:var(--ink-4);padding:14px 0}
.hidden{display:none !important}
"""


FILTER_JS = r"""
(function(){
  var btns = document.querySelectorAll('.legend button');
  function apply(f){
    btns.forEach(function(b){ b.setAttribute('aria-pressed', String(b.dataset.f === f)); });
    document.querySelectorAll('.qa').forEach(function(r){
      r.classList.toggle('hidden', f !== 'all' && !r.classList.contains(f));
    });
    // While filtering, a section with nothing to show steps out of the way, and so does
    // everything that is not a design question.
    document.querySelectorAll('.main > .sec').forEach(function(s){
      if (f === 'all') { s.classList.remove('hidden'); return; }
      var any = s.querySelector('.qa:not(.hidden)');
      s.classList.toggle('hidden', !any);
    });
  }
  btns.forEach(function(b){ b.addEventListener('click', function(){
    apply(b.getAttribute('aria-pressed') === 'true' ? 'all' : b.dataset.f); }); });

  var copy = document.getElementById('copy-agenda');
  if (copy) copy.addEventListener('click', function(){
    var t = document.getElementById('agenda').value;
    var done = function(){ copy.textContent = 'Copied'; copy.classList.add('done');
      setTimeout(function(){ copy.textContent = 'Copy the agenda'; copy.classList.remove('done'); }, 1800); };
    if (navigator.clipboard) navigator.clipboard.writeText(t).then(done, function(){});
    else { var a = document.getElementById('agenda'); a.classList.remove('hidden'); a.select();
      document.execCommand('copy'); a.classList.add('hidden'); done(); }
  });

  // The navigation marks the section in view.
  var links = {};
  document.querySelectorAll('.nav a').forEach(function(a){ links[a.getAttribute('href').slice(1)] = a; });
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function(es){
      es.forEach(function(e){
        if (e.isIntersecting && links[e.target.id]) {
          Object.values(links).forEach(function(l){ l.classList.remove('on'); });
          links[e.target.id].classList.add('on');
        }
      });
    }, {rootMargin: '-20% 0px -70% 0px'});
    document.querySelectorAll('.main > .sec[id]').forEach(function(s){ io.observe(s); });
  }
})();
"""

OPENING = ("Describe the experience you want a customer to have, from first seeing the brand to "
           "completing their most important task. What should they feel, understand and be "
           "able to do?")


def inline(md: str, g: dict) -> str:
    """`render_md` without its paragraph wrapper, for text that sits inside a line."""
    out = render_md(md, g).strip()
    m = re.fullmatch(r"<p>(.*)</p>", out, re.S)
    return m.group(1) if m and "<p>" not in m.group(1) else out


def plain(md: str) -> str:
    """Markdown down to plain text, for the copyable agenda."""
    t = re.sub(r"\^\[[^\]]*\](\([^)]*\))?", "", md)
    t = re.sub(r"\*\*|__|`", "", t)
    return " ".join(t.split())


def build() -> str:
    cite_reset()                      # numbering is per page, and this page is built once
    g = glossary()
    state, detail = status()
    brief_secs = sections()
    t = tally(brief_secs)
    qs = unknowns()
    steps, counts = next_steps()
    plan_text = (BRAIN / "plan.md").read_text(encoding="utf-8")
    strip, here = stage_strip(plan_text)
    # The brief is the engagement's one approved understanding, so it shows the bars of every
    # project that is inside a stage rather than picking one.
    bars = bar_conditions()
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    total_q = t["answered"] + t["inferred"] + t["missing"] + t["na"]

    # The approval strip. Three states, and "unset" is loud on purpose: a brief with no status
    # line has never been put in front of anyone, which is the exact failure this page fixes.
    words = {
        "draft": ("draft — awaiting your approval",
                  "Read it, then say what is wrong or say it is approved. Approving it writes "
                  "a decision and this line changes to name it."),
        "approved": (detail.lower(),
                     "Approved. Re-approval is only needed when the engagement itself changes "
                     "— volatile state lives in now.md, not here."),
        "unset": ("no status line",
                  "brain/project-brief.md carries no `Status:` line, so nothing records "
                  "whether this was ever agreed. Add one under the title."),
    }[state]

    secs, nav = [], []

    # ── coverage and the filter ──────────────────────────────────────────────────────────────
    if total_q:
        bar = "".join(f'<span class="{k}" style="flex:{t[k]}" title="{t[k]} {k}"></span>'
                      for k in ("answered", "inferred", "missing", "na") if t[k])
        km = len(t["key_missing"])
        legend = [
            ("answered", f'<b>{t["answered"]}</b> answered'),
            ("inferred", f'<b>{t["inferred"]}</b> inferred — check these'),
            ("missing", f'<b>{t["missing"]}</b> missing' + (f', {km} key' if km else "")),
            ("na", f'<b>{t["na"]}</b> not applicable'),
        ]
        cov = (f'<div class="cov"><div class="covbar">{bar}</div><div class="legend">'
               + "".join(f'<button type="button" data-f="{k}" aria-pressed="false">'
                         f'<span class="mk {k}{" key" if k == "missing" and km else ""}">'
                         f'</span>{label}</button>' for k, label in legend if t[k] or k != "na")
               + '</div></div>')
    else:
        cov = ('<div class="gap" style="margin-top:28px">this brief has no design questions yet '
               '— /brief adds the ones that fit the project from '
               '.claude/skills/brief/questions.md</div>')

    # ── the kickoff call ─────────────────────────────────────────────────────────────────────
    kick = ""
    if t["key_missing"]:
        km = t["key_missing"]
        items, agenda, last = [], [f"Kickoff — {PROJECT_NAME}", "", "Opening question:",
                                    OPENING, ""], None
        missing_all = [(sec["title"], q) for sec in brief_secs for q in sec["questions"]
                       if q["state"] == "missing"]
        # Key questions first, each group in the brief's own section order.
        ordered = ([x for x in missing_all if x[1]["key"]]
                   + [x for x in missing_all if not x[1]["key"]])
        for title, q in [x for x in ordered if x[1]["key"]]:
            if title != last:
                items.append(f'<li class="sect">{html.escape(title)}</li>')
                last = title
            who = f' <span class="who">— {html.escape(q["owner"])}</span>' if q["owner"] else ""
            items.append(f'<li>{inline(q["q"], g)}{who}</li>')
        last = None
        for i, (title, q) in enumerate(ordered):
            if i == len(km):
                agenda += ["", "If there is time:"]
                last = None
            if title != last:
                agenda += ["", title.upper()]
                last = title
            agenda.append(f"- {plain(q['q'])}" + (f" ({q['owner']})" if q["owner"] else ""))
        n = len(km)
        kick = f"""<div class="kickoff">
  <div class="ov">Kickoff workshop</div>
  <h3>{n} key question{"s are" if n != 1 else " is"} still unanswered, so I suggest a kickoff
  workshop to ask {"them" if n != 1 else "it"}.</h3>
  <p>Open with one question that ties brand, product, audience and business together, before
  anyone talks about colours or layout:</p>
  <blockquote>{html.escape(OPENING)}</blockquote>
  <p>Then the key questions:</p>
  <ul>{"".join(items)}</ul>
  <div class="actions"><button type="button" id="copy-agenda">Copy the agenda</button>
  <span>It holds every missing question, key ones first. If a meeting is hard to get,
  <code>/workshop</code> sends them as questions to answer on a phone.</span></div>
  <textarea id="agenda" class="hidden" aria-hidden="true">{html.escape(chr(10).join(agenda))}</textarea>
</div>"""

    # ── the brief, section by section ────────────────────────────────────────────────────────
    for sec in brief_secs:
        qrows, n_ans = [], 0
        for q in sec["questions"]:
            st = q["state"]
            key = " key" if q["key"] else ""
            keytag = '<span class="keytag">key</span>' if q["key"] else ""
            if st == "missing":
                ans = "Not answered yet" + (f" — {inline(q['a'], g)}" if q["a"] else "")
            elif st == "na":
                ans = "Not applicable" + (f" — {inline(q['a'], g)}" if q["a"] else "")
            else:
                ans = render_md(q["a"], g)
                n_ans += 1
            own = (f'<div class="qowner">{html.escape(q["owner"])} can answer</div>'
                   if q["owner"] and st == "missing" else "")
            qrows.append(f'<div class="qa {st}{key}"><span class="mk {st}{key}"></span>'
                         f'<div class="qbody"><div class="qq">{inline(q["q"], g)}{keytag}'
                         f'</div><div class="qans">{ans}</div>{own}</div></div>')
        miss = [q for q in sec["questions"] if q["state"] == "missing"]
        kmiss = [q for q in miss if q["key"]]
        applic = [q for q in sec["questions"] if q["state"] != "na"]

        if sec["na"]:
            tally_txt, navn = "not applicable", ('na', "n/a")
        elif sec["questions"]:
            tally_txt = f"{n_ans} of {len(applic)} answered"
            if miss:
                tally_txt += (f' · <span class="key">{len(miss)} missing</span>' if kmiss
                              else f" · {len(miss)} missing")
            navn = (("key", f"{len(miss)} missing") if kmiss else
                    ("miss", f"{len(miss)} missing") if miss else ("done", "✓"))
        else:
            tally_txt = (f"{len(sec['gaps'])} not written" if sec["gaps"] else "")
            navn = ("miss", f"{len(sec['gaps'])} to write") if sec["gaps"] else ("done", "✓")

        prose = render_md(sec["prose"], g) if sec["prose"].strip() else ""
        gaps = "".join(f'<div class="gap">{html.escape(e)} — not written yet</div>'
                       for e in sec["gaps"])
        na = (f'<div class="secna">Not applicable — {inline(sec["na"], g)}</div>'
              if sec["na"] else "")
        secs.append(f'<div class="sec" id="{sec["id"]}"><div class="sechead">'
                    f'<h2>{html.escape(sec["title"])}</h2><span class="tally">{tally_txt}</span>'
                    f'</div>{na}<div class="body">{prose}</div>{gaps}{"".join(qrows)}</div>')
        nav.append((sec["id"], sec["title"], navn))

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
    secs.append(f'<div class="sec" id="s-open"><h2>Other open questions</h2>{inner}</div>')
    nav.append(("s-open", "Other open questions",
                ("miss", str(len(qs))) if qs else ("na", "—")))

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
        barhtml = ("".join(blocks)
                   + '<div class="rest">Every condition above is read from the decision that '
                     'owns it. Status is a judgment and comes from the BAR block in '
                     'feed-items.md.</div>')
    else:
        barhtml = ('<h3 style="margin-top:30px">What ends the current stage</h3>'
                   '<div class="gap">this stage has no exit bar — write it as a decision '
                   'before the work goes further, or the stage cannot end</div>')
    secs.append(f"""<div class="sec" id="s-plan"><h2>The plan</h2>
      <div class="stages">{strip}</div>
      {barhtml}</div>""")
    nav.append(("s-plan", "The plan", ("done", "") if blocks else ("miss", "no bar")))

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
    secs.append(f'<div class="sec" id="s-next"><h2>What I would do next</h2>{inner}</div>')
    nav.append(("s-next", "Next steps", ("na", str(len(steps))) if steps else ("miss", "none")))

    # ── sources ──────────────────────────────────────────────────────────────────────────────
    srcs = cite_list_html()
    if srcs:
        secs.append(f'<div class="sec" id="s-sources"><h2>Sources</h2>{srcs}</div>')
    else:
        secs.append('<div class="sec" id="s-sources"><h2>Sources</h2><div class="gap">nothing '
                    'on this page is attributed — every claim about what someone said needs a '
                    '<code>^[who · where · when]</code> tag, or the mark '
                    '<code>^[inferred]</code></div></div>')
    nav.append(("s-sources", "Sources", ("na", "")))

    navhtml = ('<nav class="nav" aria-label="Sections"><div class="navh">The brief</div><ol>'
               + "".join(f'<li><a href="#{i}"><span>{html.escape(lbl)}</span>'
                         f'<span class="n {c}">{html.escape(n)}</span></a></li>'
                         for i, lbl, (c, n) in nav[:len(brief_secs)])
               + '</ol><div class="navh">The work</div><ol>'
               + "".join(f'<li><a href="#{i}"><span>{html.escape(lbl)}</span>'
                         f'<span class="n {c}">{html.escape(n)}</span></a></li>'
                         for i, lbl, (c, n) in nav[len(brief_secs):])
               + '</ol></nav>')

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Project brief — {html.escape(PROJECT_NAME)}</title>
{FONT_LINK}<style>{CSS}{PAGE_CSS}{BRIEF_CSS}</style></head><body>
<div class="wrap">
<div class="layout">
{navhtml}
<div class="main">
<div class="top">
  <div class="kicker">{html.escape(PROJECT_NAME)} · preliminary brief</div>
  <h1>What I understand, and what I do not</h1>
  <div class="approval {state}">
    <span class="state">{html.escape(words[0])}</span>
    <span class="what">{words[1]}</span>
  </div>
  {cov}
  {kick}
  <div class="meta">for {html.escape(OWNER)} · generated {stamp} from
    <code>brain/project-brief.md</code>, <code>brain/open-questions.md</code>,
    <code>brain/plan.md</code> and <code>brain/tasks.md</code> — regenerate with
    <code>python3 brain/brief.py</code>. The files are the truth; this page is a projection.</div>
</div>

{"".join(secs)}

<div class="footnote"><b>How to read the marks.</b>
<span class="mk answered"></span> answered from a source ·
<span class="mk inferred"></span> inferred by me, not said by anyone: check these first ·
<span class="mk missing"></span> not answered yet ·
<span class="mk missing key"></span> not answered, and the work should not move far without it ·
<span class="mk na"></span> does not apply. The small blue numbers are sources: hover one for
who said it and when, click it for the recording, the thread or the message.</div>
</div>
</div>
</div>
<div id="tip"></div>
<script>{TIP_JS}</script><script>{FILTER_JS}</script></body></html>"""



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
