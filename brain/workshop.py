#!/usr/bin/env python3
"""workshop.py — run a workshop deck from this repo, with every answer saved as you type.

    python3 brain/workshop.py serve --open              # the home page: new workshop, past ones
    python3 brain/workshop.py new "Brand kickoff" --client Acme --open
    python3 brain/workshop.py new --spec brain/workshops/acme-spec.json   # an agent-written deck
    python3 brain/workshop.py list
    python3 brain/workshop.py notes <id>                # rewrite notes.md from deck.json

    python3 brain/workshop.py preview <id>              # the deck's questions as the client's form
    python3 brain/workshop.py send <id> --to "Dana"     # a file to email (or --via vercel: a link)
    python3 brain/workshop.py receive ~/Downloads/<file>-answers-dana.html
    python3 brain/workshop.py pull                      # the answers to every hosted form
    python3 brain/workshop.py host                      # once per workspace, for --via vercel

A workshop is one folder, `brain/workshops/YYYY-MM-DD-<slug>/`:

    deck.json    the whole deck: which boards, their questions, every answer. The truth.
    notes.md     the answers as readable markdown, rewritten on every save. Route from this.
    history/     a copy of deck.json every ten minutes and before any conflicting write.
                 Gitignored; it is the undo for a bad afternoon, not the record.
    send/        the form files sent by email, one per person.
    responses/   one file per form sent: the questions as sent, and the answers that came back.

The page keeps a copy of the deck in the browser on every keystroke and sends it here a
moment later. A dropped connection, a stopped server or a refreshed tab loses nothing: the
browser copy waits and is sent when the server answers again. Close the laptop and come back
next week; the deck opens on the board you left.

Only standard library. The server listens on 127.0.0.1 and nowhere else: the answers are
client material, and a port open to the café wifi is how they leave.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from datetime import date, datetime, timedelta
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BRAIN = Path(__file__).resolve().parent
ROOT = BRAIN.parent
APP = BRAIN / "workshop"            # the page, its styles and script, the board library
STORE = BRAIN / "workshops"         # one folder per workshop
LIBRARY = APP / "library.json"
DEFAULT_PORT = 8765
HISTORY_EVERY = 600                 # seconds between history copies
HISTORY_KEEP = 60

sys.path.insert(0, str(BRAIN))
try:
    from config import CONFIG  # noqa: E402
except Exception:  # a broken workspace.toml must not stop a workshop mid-call
    CONFIG = {}

ID = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]*$")
RESERVED = {"v", "id", "rev", "project", "created", "updated", "cover", "boards", "off", "mins",
            "call", "pace", "at", "week2", "cadence"}
LOCK = threading.Lock()


# ── the library and new decks ──────────────────────────────────────────────

def library() -> list[dict]:
    return json.loads(LIBRARY.read_text(encoding="utf-8"))["boards"]


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:48].strip("-") or "workshop"


def long_date(d: date) -> str:
    return f"{d.strftime('%A')}, {d.day} {d.strftime('%B %Y')}"


MONTHS = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}


def parse_date(text: str) -> date | None:
    """The cover's date is free text. Read the common shapes; anything else is None."""
    t = (text or "").strip()
    m = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", t)
    if m:
        return date(int(m[1]), int(m[2]), int(m[3]))
    m = re.search(r"(\d{1,2})\s+([A-Za-z]{3})[a-z]*\.?,?\s+(\d{4})", t)
    if m and m[2].lower() in MONTHS:
        return date(int(m[3]), MONTHS[m[2].lower()], int(m[1]))
    m = re.search(r"([A-Za-z]{3})[a-z]*\.?\s+(\d{1,2}),?\s+(\d{4})", t)
    if m and m[1].lower() in MONTHS:
        return date(int(m[3]), MONTHS[m[1].lower()], int(m[2]))
    return None


def board_content(b: dict):
    """The empty content a board starts with, in the shape deck.js reads."""
    k = b["kind"]
    if k == "team":
        return []
    if k == "rows":
        cols = b.get("cols") or ["{client}"]
        return {"cols": cols, "rows": [{"label": r["label"], "def": r.get("def", ""), "v": [""] * len(cols)}
                                       for r in b.get("rows", [])]}
    if k == "goals":
        return [{"q": x["q"], "d": x.get("d", ""), "add": x.get("add", "Add"), "a": []} for x in b.get("buckets", [])]
    if k == "timeline":
        return {"n": b.get("weeks", 8),
                "phases": [{"name": n, "s": s, "n": w} for n, s, w in b.get("phases", [])],
                "ms": [{"name": n, "w": round(w * 7) / 7} for n, w in b.get("milestones", [])]}
    if k == "questions":
        return [{"q": q, "d": "", "a": []} if isinstance(q, str)
                else {"q": q["q"], "d": q.get("d", ""), "a": [], **({"pick": q["pick"]} if q.get("pick") else {})}
                for q in b.get("questions", [])]
    if k == "personas":
        return [{"name": "", "qs": [{"a": []} for _ in b.get("questions", [])]}]
    if k == "raci":
        return [{"role": r, "R": "", "A": "", "C": "", "I": ""} for r in b.get("roles", [])]
    if k == "traits":
        return [{"a": a, "b": z, "pos": 0} for a, z in b.get("pairs", [])]
    if k == "steps":
        return [{"who": "", "what": w} for w in b.get("items", [])]
    return None


DEF_KEYS = ("key", "kind", "name", "eyebrow", "title", "tone", "fixed", "questions", "groups")


def new_deck(title: str, client: str = "", when: str = "", us: str = "", on=None, spec_boards=None,
             project: str = "") -> dict:
    """Every library board goes into the deck; `on` (keys) or the library's own `on` says which
    start switched on, so the Deck panel can still switch the others in during the call."""
    lib = library()
    by_key = {b["key"]: b for b in lib}
    boards = [dict(b) for b in lib]
    if spec_boards is not None:
        on = []
        for entry in spec_boards:
            e = {"key": entry} if isinstance(entry, str) else dict(entry)
            key = e.get("key", "")
            if key in by_key:
                i = next(i for i, b in enumerate(boards) if b["key"] == key)
                boards[i] = {**boards[i], **e}
            else:
                if e.get("kind") not in ("questions", "rows", "goals"):
                    raise SystemExit(f"spec board {key!r}: a new board must be kind questions, rows or goals")
                if not re.match(r"^[a-z][a-z0-9-]*$", key) or key in RESERVED:
                    raise SystemExit(f"spec board key {key!r} is not usable")
                e.setdefault("name", key.replace("-", " ").capitalize())
                e.setdefault("eyebrow", e["name"])
                e.setdefault("title", "")
                e.setdefault("min", 4)
                at = next((i for i, b in enumerate(boards) if b["key"] == "end"), len(boards))
                at = next((i for i, b in enumerate(boards) if b["key"] in ("raci", "pre", "steps")), at)
                boards.insert(at, e)
            on.append(key)
    when_d = parse_date(when) or date.today()
    deck = {
        "v": 1, "rev": 0, "project": project,
        "created": datetime.now().isoformat(timespec="seconds"),
        "cover": {"title": title, "client": client, "date": long_date(when_d) if (not when or parse_date(when)) else when, "us": us,
                  "line": "", "eyebrow": by_key.get("cover", {}).get("eyebrow", "Workshop")},
        "boards": [], "off": {}, "mins": {},
        "call": {"tk": False, "len": 60, "start": 600, "tod": True, "tz": "", "theme": "light"},
        "pace": {}, "at": "cover",
    }
    for b in boards:
        key = b["key"]
        deck["boards"].append({k: b[k] for k in DEF_KEYS if k in b})
        deck["mins"][key] = b.get("min", 3)
        fixed = b.get("fixed")
        is_on = fixed or (key in on if on is not None else b.get("on", False))
        if not is_on:
            deck["off"][key] = True
        content = board_content(b)
        if b["kind"] == "week":
            days = b.get("days", [[]] * 5)
            deck["week"] = [[{"name": n, "dur": d} for n, d in day] for day in days]
            deck["week2"] = [[] for _ in range(5)]
            deck["cadence"] = 1
        elif content is not None:
            deck[key] = content
    return deck


def create(deck: dict) -> str:
    STORE.mkdir(exist_ok=True)
    base = f"{date.today().isoformat()}-{slugify(' '.join(filter(None, [deck['cover'].get('client'), deck['cover'].get('title')])))}"
    wid, n = base, 2
    while (STORE / wid).exists():
        wid, n = f"{base}-{n}", n + 1
    deck["id"] = wid
    (STORE / wid).mkdir()
    write_deck(wid, deck)
    return wid


# ── reading and writing a workshop ─────────────────────────────────────────

def folder(wid: str) -> Path:
    if not ID.match(wid or ""):
        raise KeyError(wid)
    p = STORE / wid
    if not (p / "deck.json").exists():
        raise KeyError(wid)
    return p


def read_deck(wid: str) -> dict:
    return json.loads((folder(wid) / "deck.json").read_text(encoding="utf-8"))


def atomic_write(path: Path, text: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".tmp-", suffix=path.suffix)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def snapshot(wid: str, reason: str = "") -> None:
    """Copy the current deck.json into history/, at most every ten minutes unless a reason is
    given. A reason is a conflict: two copies of the deck disagreed, and the one about to be
    overwritten is kept whole."""
    p = STORE / wid
    src = p / "deck.json"
    if not src.exists():
        return
    hist = p / "history"
    hist.mkdir(exist_ok=True)
    olds = sorted(hist.glob("*.json"))
    if not reason and olds and time.time() - olds[-1].stat().st_mtime < HISTORY_EVERY:
        return
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    shutil.copy2(src, hist / f"{stamp}{'-' + reason if reason else ''}.json")
    for old in olds[:-HISTORY_KEEP]:
        old.unlink(missing_ok=True)


def write_deck(wid: str, deck: dict) -> None:
    p = STORE / wid
    deck["id"] = wid
    deck["updated"] = datetime.now().isoformat(timespec="seconds")
    atomic_write(p / "deck.json", json.dumps(deck, ensure_ascii=False, indent=1) + "\n")
    try:
        atomic_write(p / "notes.md", notes(deck))
    except Exception as e:  # notes are a projection; a bug there must never lose a save
        print(f"notes.md not written for {wid}: {e}", file=sys.stderr)


def save(wid: str, base, deck: dict) -> dict:
    """The page sends the whole deck with the rev it started from. A mismatch means another
    tab or device wrote in between: the newest write wins, and the one it replaces goes to
    history/ whole, so nothing is lost and nothing has to be merged during a call."""
    with LOCK:
        cur = read_deck(wid)
        rev = int(cur.get("rev", 0))
        conflict = base is not None and int(base) != rev
        snapshot(wid, "conflict" if conflict else "")
        deck["rev"] = rev + 1
        for k in ("created", "project"):
            if k in cur and k not in deck:
                deck[k] = cur[k]
        write_deck(wid, deck)
        return {"rev": deck["rev"], "updated": deck["updated"], "conflict": conflict}


def answered_count(deck: dict) -> tuple[int, int]:
    """How many answers the deck holds, and how many boards are switched on."""
    n = 0
    for b in deck.get("boards", []):
        if deck.get("off", {}).get(b["key"]):
            continue
        c = deck.get(b["key"])
        if b["kind"] in ("questions", "goals"):
            n += sum(len([a for a in q.get("a", []) if a.strip()]) for q in c or [])
        elif b["kind"] == "rows":
            n += sum(1 for r in (c or {}).get("rows", []) for v in r.get("v", []) if v.strip())
        elif b["kind"] == "personas":
            n += sum(1 for p in c or [] for q in p.get("qs", []) for a in q.get("a", []) if a.strip())
        elif b["kind"] == "traits":
            n += sum(1 for t in c or [] if t.get("pos"))
    on = sum(1 for b in deck.get("boards", []) if not deck.get("off", {}).get(b["key"]))
    return n, on


def listing() -> list[dict]:
    out = []
    if not STORE.exists():
        return out
    for p in sorted(STORE.iterdir(), reverse=True):
        f = p / "deck.json"
        if not f.exists():
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        n, on = answered_count(d)
        c = d.get("cover", {})
        sent = [{"to": r.get("to", ""), "via": r.get("via", ""), "done": bool(r.get("done")),
                 "answered": progress(r)[0], "of": progress(r)[1]} for r in responses(p.name)]
        out.append({"id": p.name, "title": c.get("title", ""), "client": c.get("client", ""),
                    "date": c.get("date", ""), "updated": d.get("updated", ""), "answers": n, "boards": on,
                    "at": d.get("at", ""), "sent": sent})
    return out


# ── notes.md: the deck as markdown ─────────────────────────────────────────

def _t(s) -> str:
    return (s or "").strip()


def notes(d: dict) -> str:
    c = d.get("cover", {})
    client = _t(c.get("client")) or "the client"
    kick = parse_date(c.get("date", ""))
    mon = kick - timedelta(days=kick.weekday()) if kick else None
    fm = ["---", "tags: [research]"]
    if d.get("project"):
        fm.append(f"project: {d['project']}")
    fm.append("---")
    out = fm + [f"# Workshop notes — {_t(c.get('title')) or 'Untitled'}",
                f"{client} · {_t(c.get('date'))} · `{d.get('id', '')}`", "",
                "*Written by `brain/workshop.py` from `deck.json` on every save. Edits here are "
                "overwritten; route from it, never into it. An empty answer is marked _open_.*", ""]
    who_name = lambda s: _t(s) or "_no owner_"  # noqa: E731
    for b in d.get("boards", []):
        k, kind = b["key"], b["kind"]
        if d.get("off", {}).get(k) or kind in ("cover", "agenda", "end"):
            continue
        x = d.get(k)
        title = _t(b.get("title"))
        out.append(f"## {b.get('name', k)}" + (f" — {title}" if title else ""))
        out.append("")
        if kind == "team":
            people = [m for m in x or [] if _t(m.get("name"))]
            out += [f"- {_t(m['name'])}" + (f" — {_t(m.get('role'))}" if _t(m.get("role")) else "") for m in people] or ["_open_"]
        elif kind == "rows":
            cols = [col.replace("{client}", client) for col in x.get("cols", [])]
            for r in x.get("rows", []):
                vals = r.get("v", [])
                if len(cols) == 1:
                    out.append(f"- **{r['label']}:** {_t(vals[0] if vals else '') or '_open_'}")
                else:
                    out.append(f"- **{r['label']}**")
                    out += [f"  - {col}: {_t(v) or '_open_'}" for col, v in zip(cols, vals)]
        elif kind in ("questions", "goals"):
            for q in x or []:
                if not _t(q.get("q")) and not any(_t(a) for a in q.get("a", [])):
                    continue
                out.append(f"### {_t(q.get('q')) or 'Untitled'}")
                ans = [_t(a) for a in q.get("a", []) if _t(a)]
                out += [f"- {a}" for a in ans] or ["_open_"]
                out.append("")
        elif kind == "timeline":
            def wk(s, n):
                lab = f"W{s + 1}" if n == 1 else f"W{s + 1}–W{s + n}"
                if mon:
                    a, z = mon + timedelta(weeks=s), mon + timedelta(weeks=s + n - 1, days=4)
                    lab += f" ({a.day} {a.strftime('%b')} – {z.day} {z.strftime('%b')})"
                return lab
            out.append(f"{x.get('n')} weeks from the kickoff.")
            out.append("")
            out += [f"- {_t(p.get('name')) or 'Unnamed phase'}: {wk(p['s'], p['n'])}" for p in x.get("phases", [])]
            for m in sorted(x.get("ms", []), key=lambda m: m["w"]):
                when = mon + timedelta(days=round(m["w"] * 7)) if mon else None
                out.append(f"- ◆ {_t(m.get('name')) or 'Unnamed milestone'}: "
                           + (f"{when.strftime('%a')} {when.day} {when.strftime('%b')}" if when else f"week {int(m['w']) + 1}"))
        elif kind == "personas":
            qs = b.get("questions", [])
            for p in x or []:
                role = _t((p["qs"][0]["a"] or [""])[0]) if p.get("qs") else ""
                out.append(f"### {_t(p.get('name')) or 'Unnamed audience'}" + (f" — {role}" if role else ""))
                for i, q in enumerate(qs[1:], 1):
                    ans = [_t(a) for a in (p["qs"][i]["a"] if i < len(p.get("qs", [])) else []) if _t(a)]
                    out.append(f"- **{q['q']}** " + ("; ".join(ans) if ans else "_open_"))
                out.append("")
        elif kind == "raci":
            out += ["| Role | Responsible | Accountable | Consulted | Informed |", "|---|---|---|---|---|"]
            out += [f"| {_t(r.get('role'))} | " + " | ".join(_t(r.get(k2)) or "—" for k2 in "RACI") + " |" for r in x or []]
        elif kind == "traits":
            out += [f"- {t['a']} ↔ {t['b']}: {lean(t.get('pos', 0), t['a'], t['b'])}" for t in x or []]
        elif kind == "week":
            names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            weeks = [d.get("week", [])] + ([d.get("week2", [])] if d.get("cadence") == 2 else [])
            for wi, week in enumerate(weeks):
                if len(weeks) > 1:
                    out.append(f"**Week {wi + 1}**")
                for di, evs in enumerate(week):
                    evs = [e for e in evs if _t(e.get("name"))]
                    if evs:
                        out.append(f"- {names[di]}: " + "; ".join(
                            _t(e["name"]) + (f" ({_t(e.get('dur'))})" if _t(e.get("dur")) else "") for e in evs))
        elif kind == "steps":
            out += [f"- [ ] {who_name(s.get('who'))} — {_t(s.get('what'))}" for s in x or [] if _t(s.get("what"))]
        out.append("")
    for rec in responses(d.get("id", "")):
        out += response_notes(rec)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).rstrip() + "\n"


def lean(p, a: str, b: str) -> str:
    words = {1: "strongly", 2: "clearly", 3: "a little", 5: "a little", 6: "clearly", 7: "strongly"}
    p = int(p or 0)
    return "_not placed_" if p not in range(1, 8) else "balanced" if p == 4 else f"{words[p]} {a if p < 4 else b}"


# ── async: the deck's questions as a form a client fills in alone ──────────
#
# `send` turns the switched-on question boards into a plain form, one per person, and records
# it in `responses/<who>-<token>.json` next to deck.json. The answers come back into that same
# file, never into deck.json, so a deck open in a tab can never overwrite them. Two ways out:
#
#   file     one HTML file to email. The client's answers stay in their browser as they type;
#            the page downloads a copy of itself with the answers inside, they email it back,
#            and `receive` reads it. Needs nothing set up.
#   vercel   a link per person to a small deploy of `workshop/hosted/`; every answer is saved
#            as it is typed, and `pull` fetches them. `host` sets it up once per workspace.

FORM = APP / "form.html"
HOSTED = APP / "hosted"
FORM_KINDS = ("questions", "rows", "goals", "personas", "traits")
SPEC_TAG = '<script id="spec" type="application/json">null</script>'
VIAS = ("file", "vercel")
SECTION_NOTE = {
    "traits": "Pick a point on each line. The middle means balanced; a second tap clears it.",
    "personas": "One for each group this is for. Add the people it is not for, too.",
}


def library_picks() -> dict:
    """Question text → its pick in the library, so a deck made before a question had options,
    or one whose question was left as written, still gets them."""
    out = {}
    for b in library():
        for q in b.get("questions") or []:
            if isinstance(q, dict) and q.get("pick"):
                out[q["q"]] = q["pick"]
    return out


def ask(qid: str, q: dict) -> dict:
    """One question as the form asks it. A question with a `pick` in the library (or the spec)
    is answered with a tap: `one` is a list of options, `many` is chips, `scale` is two words on
    seven steps. `other` adds a field for an answer not listed; `note` adds a field for a line
    of explanation. Without a pick it is a text field."""
    pk = q.get("pick") or library_picks().get(_t(q.get("q"))) or {}
    it = {"id": qid, "kind": pk.get("type") or "text", "q": _t(q.get("q")),
          "d": _t(pk["d"] if "d" in pk else q.get("d"))}   # a pick's own `d` replaces examples its options now show
    if it["kind"] in ("one", "many"):
        it.update(options=list(pk.get("options") or []), other=bool(pk.get("other")), note=bool(pk.get("note")))
        if pk.get("max"):
            it["max"] = int(pk["max"])
    elif it["kind"] == "scale":
        it.update(a=pk.get("a", ""), b=pk.get("b", ""))
    else:
        it["kind"] = "text"
    return it


def form_spec(d: dict, to: str = "", token: str = "", note: str = "", due: str = "", keys=None,
              preview: bool = False, reply_to: str = "") -> dict:
    """The questions a form asks, read from the deck as it stands: its question text as edited
    in prep, and only the boards switched on (or the ones named in `keys`). Team, timeline, RACI,
    week and next steps belong to the call and stay out."""
    c = d.get("cover", {})
    client, title = _t(c.get("client")), _t(c.get("title")) or "Workshop"
    sections = []
    for b in d.get("boards", []):
        k, kind = b["key"], b["kind"]
        if kind not in FORM_KINDS or (k not in keys if keys is not None else d.get("off", {}).get(k)):
            continue
        x, items = d.get(k), []
        if kind == "questions":
            items = [ask(f"{k}.{i}", q) for i, q in enumerate(x or []) if _t(q.get("q"))]
        elif kind == "goals":
            items = [{"id": f"{k}.{i}", "kind": "list", "q": _t(q.get("q")), "d": _t(q.get("d"))}
                     for i, q in enumerate(x or []) if _t(q.get("q"))]
        elif kind == "rows":
            cols = [col.replace("{client}", client or "you") for col in (x or {}).get("cols", [])]
            items = [{"id": f"{k}.{i}.{j}", "kind": "text", "q": r["label"] if len(cols) == 1 else f"{r['label']} — {col}",
                      "d": _t(r.get("def"))}
                     for i, r in enumerate((x or {}).get("rows", [])) for j, col in enumerate(cols)]
        elif kind == "traits":
            items = [{"id": f"{k}.{i}", "kind": "scale", "a": t["a"], "b": t["b"]} for i, t in enumerate(x or [])]
        elif kind == "personas":
            items = [{"id": k, "kind": "people", "one": "Audience", "add": "Add another audience",
                      "name_hint": "Name this audience, e.g. first-time buyers",
                      "names": [_t(p.get("name")) for p in x or [] if _t(p.get("name"))],
                      "qs": [ask(f"{k}.q{j}", {"q": q["q"], "d": q.get("prompt"), "pick": q.get("pick")})
                             for j, q in enumerate(b.get("questions", []))]}]
        if items:
            sections.append({"key": k, "name": b.get("name", k), "title": _t(b.get("title")),
                             "d": SECTION_NOTE.get(kind, ""), "items": items})
    who = slugify(to) if to else ""
    return {"v": 1, "id": d.get("id", ""), "token": token, "to": to, "title": title, "client": client,
            "us": _t(c.get("us")), "note": note, "due": due, "sent": date.today().isoformat(), "preview": preview,
            "reply_to": reply_to or _t(ws_conf().get("reply_to")),
            "save_as": f"{slugify(' '.join(filter(None, [client, title])))}-answers{'-' + who if who else ''}.html",
            "sections": sections}


def form_html(spec: dict) -> str:
    page = FORM.read_text(encoding="utf-8")
    if SPEC_TAG not in page:
        raise RuntimeError("form.html has lost its spec placeholder")
    data = json.dumps(spec, ensure_ascii=False).replace("<", "\\u003c")
    return page.replace(SPEC_TAG, f'<script id="spec" type="application/json">{data}</script>')


def responses(wid: str) -> list[dict]:
    if not ID.match(wid or ""):
        return []
    out = []
    for f in sorted((STORE / wid / "responses").glob("*.json")):
        try:
            rec = json.loads(f.read_text(encoding="utf-8"))
            rec["_path"] = f
            out.append(rec)
        except Exception:
            continue
    return sorted(out, key=lambda r: r.get("sent", ""))


def write_response(wid: str, rec: dict) -> None:
    path = rec.pop("_path", None) or STORE / wid / "responses" / f"{slugify(rec.get('to') or 'client')}-{rec['token'][:6]}.json"
    path.parent.mkdir(exist_ok=True)
    atomic_write(path, json.dumps(rec, ensure_ascii=False, indent=1) + "\n")
    rec["_path"] = path
    atomic_write(STORE / wid / "notes.md", notes(read_deck(wid)))


def filled(it: dict, v) -> bool:
    if it["kind"] == "people":
        for p in v if isinstance(v, list) else []:
            a = p.get("a") or [] if isinstance(p, dict) else []
            if isinstance(p, dict) and (_t(p.get("name")) or any(filled(q, a[j]) for j, q in enumerate(it["qs"]) if j < len(a))):
                return True
        return False
    if it["kind"] == "scale":
        return isinstance(v, (int, float)) and 1 <= v <= 7
    if it["kind"] in ("one", "many"):
        return isinstance(v, dict) and bool(v.get("v") or (v.get("o") and _t(v.get("other"))) or _t(v.get("note")))
    return bool(_t(v if isinstance(v, str) else ""))


def said(it: dict, v) -> str:
    """One answer as a line of markdown, or `_open_`."""
    if not filled(it, v):
        return "_open_"
    if it["kind"] == "scale":
        return lean(v, it["a"], it["b"])
    if it["kind"] in ("one", "many"):
        picked = v.get("v") or []
        picked = [picked] if isinstance(picked, str) else list(picked)
        if v.get("o") and _t(v.get("other")):
            picked.append(_t(v["other"]))
        out = ", ".join(picked)
        if _t(v.get("note")):
            out += (" — " if out else "") + _t(v["note"])
        return out
    return _t(v)


def progress(rec: dict) -> tuple[int, int]:
    """Answered and asked, counted as the page counts them: each audience's questions apiece."""
    A, n, t = rec.get("answers") or {}, 0, 0
    for it in (it for s in rec["spec"]["sections"] for it in s["items"]):
        if it["kind"] == "people":
            people = [p for p in A.get(it["id"]) or [] if isinstance(p, dict)] or [{"a": []}] * max(1, len(it.get("names") or []))
            for p in people:
                a = p.get("a") or []
                t += len(it["qs"])
                n += sum(1 for j, q in enumerate(it["qs"]) if j < len(a) and filled(q, a[j]))
        else:
            t += 1
            n += filled(it, A.get(it["id"]))
    return n, t


def response_notes(rec: dict) -> list[str]:
    s, A = rec["spec"], rec.get("answers") or {}
    n, t = progress(rec)
    state = "marked finished" if rec.get("done") else "not started" if not n else "in progress"
    last = f", last saved {datetime.fromtimestamp(rec['at'] / 1000):%Y-%m-%d %H:%M}" if rec.get("at") else ""
    how = "a link" if rec.get("via") == "vercel" else "a file"
    out = [f"## Answers from {rec.get('to') or 'the client'}", "",
           f"Sent {rec.get('sent', '')[:10]} as {how}. {n} of {t} answered, {state}{last}. "
           "Answered alone, in their own words and picks; nothing was filled in for them.", ""]
    for sec in s["sections"]:
        out += [f"### {sec['name']}" + (f" — {sec['title']}" if sec.get("title") else ""), ""]
        for it in sec["items"]:
            v = A.get(it["id"])
            if it["kind"] == "scale":
                out.append(f"- {it['a']} ↔ {it['b']}: {lean(v, it['a'], it['b'])}")
            elif it["kind"] == "people":
                people = [p for p in (v or []) if isinstance(p, dict)] if filled(it, v) else []
                for i, p in enumerate(people):
                    out.append(f"**{_t(p.get('name')) or f'Audience {i + 1}'}**")
                    a = p.get("a") or []
                    out += [f"- **{q['q']}** {said(q, a[j] if j < len(a) else None)}" for j, q in enumerate(it["qs"])]
                    out.append("")
                if not people:
                    out += ["_open_", ""]
            elif it["kind"] == "list":
                lines = [ln.strip() for ln in (v or "").splitlines() if ln.strip()] if isinstance(v, str) else []
                out += [f"**{it['q']}**"] + ([f"- {ln}" for ln in lines] or ["_open_"]) + [""]
            else:
                out += [f"**{it['q']}**", said(it, v), ""]
        out.append("")
    return out


def env_value(name: str) -> str:
    """A secret from the environment, else from `.env.agents` (gitignored)."""
    if os.environ.get(name):
        return os.environ[name]
    f = ROOT / ".env.agents"
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            k, _, v = line.partition("=")
            if k.strip() == name:
                return v.strip().strip('"').strip("'")
    return ""


def ws_conf() -> dict:
    return (CONFIG or {}).get("workshop", {}) if isinstance(CONFIG, dict) else {}


def host_url() -> str:
    return (os.environ.get("WORKSHOP_HOST_URL") or _t(ws_conf().get("host_url"))).rstrip("/")


def http_json(method: str, url: str, body=None, headers=None, timeout=20):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json", **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read() or b"null")


def send(wid: str, to: str = "", via: str = "", note: str = "", due: str = "", keys=None, reply_to: str = "") -> dict:
    via = via or _t(ws_conf().get("send_via")) or "file"
    if via not in VIAS:
        raise SystemExit(f"--via is file or vercel, not {via!r}")
    d = read_deck(wid)
    token = secrets.token_urlsafe(18)
    spec = form_spec(d, to, token, note, due, keys, reply_to=reply_to)
    if not spec["sections"]:
        raise SystemExit("Nothing to ask: no question, goals, rows, audience or personality board is switched on.")
    rec = {"v": 1, "to": to, "via": via, "token": token, "sent": datetime.now().isoformat(timespec="seconds"),
           "spec": spec, "answers": {}, "at": 0, "done": False, "received": ""}
    if via == "file":
        out = STORE / wid / "send" / f"{spec['save_as'].replace('-answers', '-questions')}"
        out.parent.mkdir(exist_ok=True)
        atomic_write(out, form_html(spec))
        rec["file"] = str(out.relative_to(ROOT) if out.is_relative_to(ROOT) else out)
    else:
        url, key = host_url(), env_value("WORKSHOP_ADMIN_KEY")
        if not url or not key:
            raise SystemExit("The hosted form is not set up in this workspace. Run `python3 brain/workshop.py host` "
                             "once, or send it as a file with --via file.")
        try:
            http_json("POST", f"{url}/api/form", {"token": token, "spec": spec}, {"x-workshop-key": key})
        except Exception as e:
            raise SystemExit(f"Could not create the form at {url}: {e}")
        rec["link"] = f"{url}/f/{token}"
    write_response(wid, rec)
    return rec


def receive(src: Path) -> tuple[str, dict]:
    """Read a form a client sent back: the downloaded copy of the page, answers inside."""
    text = src.read_text(encoding="utf-8")
    grab = lambda i: re.search(rf'<script id="{i}" type="application/json">(.*?)</script>', text, re.S)  # noqa: E731
    s, a = grab("spec"), grab("answers")
    spec = json.loads(s[1]) if s else None
    ans = json.loads(a[1]) if a else None
    if not spec or not spec.get("token"):
        raise SystemExit(f"{src} is not a workshop form.")
    if not ans:
        raise SystemExit(f"{src} has no answers in it: it is the form as it was sent, not the copy sent back.")
    wid = spec.get("id", "")
    rec = next((r for r in responses(wid) if r.get("token") == spec["token"]), None)
    if rec is None:
        folder(wid)  # raises when the workshop is not in this workspace
        rec = {"v": 1, "to": spec.get("to", ""), "via": "file", "token": spec["token"], "sent": spec.get("sent", ""),
               "spec": spec, "answers": {}, "at": 0, "done": False}
    if (ans.get("at") or 0) < (rec.get("at") or 0):
        raise SystemExit(f"{src} is older than the answers already received from {rec.get('to') or 'them'}; kept those.")
    rec.update(answers=ans.get("answers") or {}, at=ans.get("at") or 0, done=bool(ans.get("done")),
               received=datetime.now().isoformat(timespec="seconds"))
    write_response(wid, rec)
    return wid, rec


def pull(wid: str | None = None) -> list[tuple[str, dict, bool]]:
    """Fetch the latest answers for every hosted form; returns (workshop, record, changed)."""
    url, out = host_url(), []
    ids = [wid] if wid else [w["id"] for w in listing()]
    for w in ids:
        for rec in responses(w):
            if rec.get("via") != "vercel":
                continue
            base = (rec.get("link") or "").split("/f/")[0] or url
            got = http_json("GET", f"{base}/api/form?t={rec['token']}").get("answers")
            changed = bool(got) and (got.get("at") or 0) > (rec.get("at") or 0)
            if changed:
                rec.update(answers=got.get("answers") or {}, at=got.get("at") or 0, done=bool(got.get("done")),
                           received=datetime.now().isoformat(timespec="seconds"))
                write_response(w, rec)
            out.append((w, rec, changed))
    return out


# ── the server ─────────────────────────────────────────────────────────────

TYPES = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
         ".js": "text/javascript; charset=utf-8", ".json": "application/json; charset=utf-8",
         ".svg": "image/svg+xml", ".md": "text/markdown; charset=utf-8"}


class Handler(BaseHTTPRequestHandler):
    server_version = "workshop/1"

    def log_message(self, fmt, *args):  # one quiet line per write, nothing for reads
        if self.command in ("PUT", "POST"):
            sys.stderr.write(f"{datetime.now():%H:%M:%S} {self.command} {self.path}\n")

    def send(self, code, body=b"", ctype="application/json; charset=utf-8", extra=None):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False).encode()
        elif isinstance(body, str):
            body = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def file(self, path: Path):
        if not path.is_file():
            return self.send(404, {"error": "not found"})
        self.send(200, path.read_bytes(), TYPES.get(path.suffix, "application/octet-stream"))

    def body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}")

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/", "/index.html"):
            return self.file(APP / "home.html")
        if path.startswith("/w/"):
            try:
                folder(path[3:].strip("/"))
            except KeyError:
                return self.send(404, "No workshop by that name. <a href='/'>All workshops</a>", "text/html")
            return self.file(APP / "deck.html")
        if path.startswith("/p/"):  # the owner's preview of the form a client would get
            wid = path[3:].strip("/")
            try:
                d = read_deck(wid)
            except KeyError:
                return self.send(404, "No workshop by that name. <a href='/'>All workshops</a>", "text/html")
            return self.send(200, form_html(form_spec(d, token=f"preview-{wid}", preview=True)), TYPES[".html"])
        if path == "/favicon.ico":
            return self.send(204)
        if path.startswith("/a/"):
            name = path[3:]
            if "/" in name or name.startswith("."):
                return self.send(404, {"error": "not found"})
            return self.file(APP / name)
        if path == "/api/ping":
            return self.send(200, {"ok": True, "root": str(ROOT)})
        if path == "/api/library":
            return self.send(200, {"boards": library(), "us": default_us(), "projects": projects()})
        if path == "/api/workshops":
            return self.send(200, listing())
        m = re.match(r"^/api/workshops/([^/]+)(/notes\.md)?$", path)
        if m:
            try:
                d = read_deck(m[1])
            except KeyError:
                return self.send(404, {"error": "no such workshop"})
            if m[2]:
                return self.send(200, notes(d), TYPES[".md"],
                                 {"Content-Disposition": f'attachment; filename="{m[1]}-notes.md"'})
            return self.send(200, {"deck": d, "rev": d.get("rev", 0),
                                   "path": str((STORE / m[1] / "deck.json").relative_to(ROOT))})
        self.send(404, {"error": "not found"})

    do_HEAD = do_GET

    def do_POST(self):
        if self.path != "/api/workshops":
            return self.send(404, {"error": "not found"})
        try:
            b = self.body()
            deck = new_deck(_t(b.get("title")) or "Workshop", _t(b.get("client")), _t(b.get("date")),
                            _t(b.get("us")), on=b.get("on"), project=_t(b.get("project")))
            wid = create(deck)
        except Exception as e:
            return self.send(400, {"error": str(e)})
        self.send(201, {"id": wid, "url": f"/w/{wid}"})

    def do_PUT(self):
        m = re.match(r"^/api/workshops/([^/]+)$", self.path)
        if not m:
            return self.send(404, {"error": "not found"})
        try:
            b = self.body()
            deck = b["deck"]
            if not isinstance(deck, dict) or not isinstance(deck.get("boards"), list):
                raise ValueError("not a deck")
            r = save(m[1], b.get("base"), deck)
        except KeyError:
            return self.send(404, {"error": "no such workshop"})
        except Exception as e:
            return self.send(400, {"error": str(e)})
        self.send(200, r)


def default_us() -> str:
    eng = (CONFIG or {}).get("engagement", {}) if isinstance(CONFIG, dict) else {}
    ws = (CONFIG or {}).get("workshop", {}) if isinstance(CONFIG, dict) else {}
    us = _t(ws.get("studio")) or ""
    return "" if "{{" in us else us or ("" if "{{" in _t(eng.get("owner")) else _t(eng.get("owner")))


def projects() -> list[list[str]]:
    """[[key, label], …] when the workspace has more than one project, else []. One project
    needs no tag; two or more and every workshop has to say which it belongs to."""
    pr = (CONFIG or {}).get("projects", {}) if isinstance(CONFIG, dict) else {}
    keys = [k for k in pr.get("keys", []) if "{{" not in k]
    labels = pr.get("labels", []) or keys
    return [[k, labels[i] if i < len(labels) else k] for i, k in enumerate(keys)] if len(keys) > 1 else []


def port_of() -> int:
    ws = (CONFIG or {}).get("workshop", {}) if isinstance(CONFIG, dict) else {}
    try:
        return int(ws.get("port") or DEFAULT_PORT)
    except (TypeError, ValueError):
        return DEFAULT_PORT


def running(port: int) -> bool:
    """True when this repo's workshop server already answers on the port."""
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/ping", timeout=0.5) as r:
            return json.loads(r.read()).get("root") == str(ROOT)
    except Exception:
        return False


def port_free(port: int) -> bool:
    with socket.socket() as s:
        return s.connect_ex(("127.0.0.1", port)) != 0


def show(url: str) -> None:
    subprocess.run([sys.executable, str(BRAIN / "show.py"), url], check=False)


def ensure_server(port: int) -> bool:
    """Start the server in the background unless it already runs. True if it is up."""
    if running(port):
        return True
    if not port_free(port):
        print(f"Port {port} is taken by something else. Set [workshop] port in brain/workspace.toml.")
        return False
    log = BRAIN / "workshops" / ".server.log"
    STORE.mkdir(exist_ok=True)
    with open(log, "a") as f:
        subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "serve", "--port", str(port)],
                         stdout=f, stderr=f, start_new_session=True, cwd=ROOT)
    for _ in range(40):
        if running(port):
            return True
        time.sleep(0.1)
    print(f"The server did not start; see {log.relative_to(ROOT)}.")
    return False


def serve(port: int, open_path: str | None) -> int:
    if running(port):
        print(f"Already running: http://127.0.0.1:{port}/")
        if open_path is not None:
            show(f"http://127.0.0.1:{port}{open_path}")
        return 0
    STORE.mkdir(exist_ok=True)
    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Workshops at http://127.0.0.1:{port}/ — saving to {STORE.relative_to(ROOT)}/. Ctrl-C stops it.")
    if open_path is not None:
        threading.Timer(0.3, show, [f"http://127.0.0.1:{port}{open_path}"]).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


def set_host_url(url: str) -> None:
    """Write `[workshop] host_url` into workspace.toml, so the links survive this session."""
    f = BRAIN / "workspace.toml"
    text = f.read_text(encoding="utf-8")
    new, n = re.subn(r'(?m)^host_url\s*=\s*"[^"]*"', f'host_url = "{url}"', text, count=1)
    if n:
        atomic_write(f, new)
    else:
        print(f'Add this under [workshop] in brain/workspace.toml:  host_url = "{url}"')


def host(project: str = "") -> int:
    """Set up, or redeploy, the hosted form on the owner's Vercel account. Safe to re-run: each
    step checks before it acts. The deploy holds no answers; they sit in the project's Redis."""
    if not shutil.which("vercel"):
        print("The Vercel CLI is not installed. Run `npm i -g vercel`, then `vercel login`, then this again.")
        return 1
    if subprocess.run(["vercel", "whoami"], capture_output=True, text=True).returncode:
        print("Log in to Vercel first: `vercel login`, then run this again.")
        return 1
    vc = lambda *a, **k: subprocess.run(["vercel", *a, "--cwd", str(HOSTED)], text=True, **k)  # noqa: E731
    if not (HOSTED / ".vercel" / "project.json").exists():
        eng = _t((CONFIG or {}).get("engagement", {}).get("name") if isinstance(CONFIG, dict) else "")
        name = project or _t(ws_conf().get("host_project")) or \
            (f"{slugify(eng)}-workshop" if eng and "{{" not in eng else "workshop-forms")
        print(f"Linking a Vercel project called {name}.")
        if vc("link", "--yes", "--project", name).returncode:
            return 1
    envs = vc("env", "ls", "production", capture_output=True).stdout
    if not re.search(r"\b(KV_REST_API_URL|UPSTASH_REDIS_REST_URL)\b", envs):
        print("Adding a Redis store (Upstash, free tier) to hold the answers. The CLI may ask you to accept its terms.")
        if vc("integration", "add", "upstash/upstash-kv", "--no-env-pull").returncode:
            print("Add it in the dashboard instead: the project → Storage → Upstash for Redis → Connect. "
                  "Then run this again.")
            return 1
    key = env_value("WORKSHOP_ADMIN_KEY")
    if not key:
        key = secrets.token_urlsafe(32)
        with open(ROOT / ".env.agents", "a", encoding="utf-8") as f:
            f.write(f"\n# The key that lets this workspace create hosted workshop forms. Never share it.\nWORKSHOP_ADMIN_KEY={key}\n")
        print("Wrote WORKSHOP_ADMIN_KEY to .env.agents (gitignored).")
    if not re.search(r"\bWORKSHOP_ADMIN_KEY\b", envs):
        if vc("env", "add", "WORKSHOP_ADMIN_KEY", "production", "--sensitive", "--yes", "--force",
              input=key, capture_output=True).returncode:
            print("Could not add WORKSHOP_ADMIN_KEY to the Vercel project; add it in the dashboard with the "
                  "value from .env.agents, then run this again.")
            return 1
    shutil.copy2(FORM, HOSTED / "form.html")
    print("Deploying.")
    r = vc("deploy", "--prod", "--yes", capture_output=True)
    if r.returncode:
        print(r.stdout[-2000:], r.stderr[-2000:])
        return 1
    found = re.findall(r"https://[a-z0-9.-]+\.vercel\.app", r.stdout + r.stderr)
    proj = json.loads((HOSTED / ".vercel" / "project.json").read_text()).get("projectName", "")
    # The production alias is public; a deployment's own URL sits behind Vercel's login.
    candidates = ([f"https://{proj}.vercel.app"] if proj else []) + found
    for url in dict.fromkeys(candidates):
        try:
            ping = http_json("GET", f"{url}/api/form", timeout=15)
        except Exception:
            continue
        if ping.get("ok"):
            if not (ping.get("store") and ping.get("admin")):
                print(f"Deployed to {url}, but the function cannot see "
                      f"{'its Redis store' if not ping.get('store') else 'WORKSHOP_ADMIN_KEY'}. "
                      "Check the project's environment variables, then run this again.")
                return 1
            set_host_url(url)
            print(f"Ready: {url}. Forms sent with --via vercel get links there.")
            return 0
    print("Deployed, but no public address answered. If the project has Deployment Protection on its "
          "production domain, switch it off for this project, then run this again.")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("serve", help="run the server (home page at /)")
    s.add_argument("--port", type=int, default=None)
    s.add_argument("--open", nargs="?", const="", default=None, metavar="ID",
                   help="open the home page, or a workshop by id")
    n = sub.add_parser("new", help="create a workshop")
    n.add_argument("title", nargs="?", default="")
    n.add_argument("--client", default="")
    n.add_argument("--date", default="", help="the day of the workshop, e.g. 2026-11-12")
    n.add_argument("--us", default=None, help="your studio's name, set as text on the cover")
    n.add_argument("--boards", default=None, help="comma-separated keys to switch on")
    n.add_argument("--spec", default=None, help="a JSON file: title, client, date, us, project, boards")
    n.add_argument("--project", default="")
    n.add_argument("--open", action="store_true", help="start the server if needed and open it")
    sub.add_parser("list", help="list workshops")
    nt = sub.add_parser("notes", help="rewrite notes.md from deck.json")
    nt.add_argument("id")
    sub.add_parser("library", help="list the boards a workshop can hold")
    sd = sub.add_parser("send", help="send the deck's questions to someone as a form")
    sd.add_argument("id")
    sd.add_argument("--to", default="", help="who answers it; one form per person")
    sd.add_argument("--via", default="", choices=["", *VIAS], help="file (default) or vercel; see [workshop] send_via")
    sd.add_argument("--note", default="", help="a few lines from you, in place of the standard opening")
    sd.add_argument("--due", default="", help="when you need it, as it should read, e.g. 'Friday 13 November'")
    sd.add_argument("--boards", default=None, help="comma-separated keys, in place of the boards switched on")
    sd.add_argument("--reply-to", default="", help="the address the answers go back to; see [workshop] reply_to")
    sd.add_argument("--no-show", action="store_true", help="do not reveal the file or open the link")
    pv = sub.add_parser("preview", help="open the form a client would get, without sending it")
    pv.add_argument("id")
    rc = sub.add_parser("receive", help="read the answers file a client emailed back")
    rc.add_argument("file")
    pl = sub.add_parser("pull", help="fetch the answers to hosted forms")
    pl.add_argument("id", nargs="?", default=None)
    hs = sub.add_parser("host", help="set up or redeploy the hosted form on Vercel")
    hs.add_argument("--project", default="", help="the Vercel project's name")
    a = ap.parse_args()

    if a.cmd == "serve":
        return serve(a.port or port_of(), None if a.open is None else (f"/w/{a.open}" if a.open else "/"))
    if a.cmd == "new":
        spec = json.loads(Path(a.spec).read_text(encoding="utf-8")) if a.spec else {}
        title = a.title or spec.get("title", "")
        if not title:
            ap.error("a title, or a spec with one")
        deck = new_deck(title, a.client or spec.get("client", ""), a.date or spec.get("date", ""),
                        a.us if a.us is not None else spec.get("us", default_us()),
                        on=a.boards.split(",") if a.boards else None,
                        spec_boards=spec.get("boards"), project=a.project or spec.get("project", ""))
        wid = create(deck)
        print(f"{(STORE / wid / 'deck.json').relative_to(ROOT)}")
        if a.open:
            port = port_of()
            if ensure_server(port):
                show(f"http://127.0.0.1:{port}/w/{wid}")
        return 0
    if a.cmd == "list":
        for w in listing():
            print(f"{w['id']}  {w['answers']} answers on {w['boards']} boards  · updated {w['updated'][:16]}")
            for s in w["sent"]:
                print(f"    sent to {s['to'] or 'someone'} as a {'link' if s['via'] == 'vercel' else 'file'}: "
                      f"{s['answered']} of {s['of']} answered{', finished' if s['done'] else ''}")
        return 0
    if a.cmd == "send":
        rec = send(a.id, a.to, a.via, a.note, a.due, a.boards.split(",") if a.boards else None, a.reply_to)
        n = progress(rec)[1]
        print(f"{n} questions in {len(rec['spec']['sections'])} sections for {a.to or 'the client'}.")
        if rec["via"] == "file":
            print(f"Attach this file to an email: {rec['file']}")
            if not a.no_show:
                subprocess.run([sys.executable, str(BRAIN / "show.py"), "--reveal", str(ROOT / rec["file"])], check=False)
        else:
            print(f"Send this link: {rec['link']}")
            if not a.no_show:
                show(rec["link"])
        return 0
    if a.cmd == "preview":
        read_deck(a.id)
        port = port_of()
        if ensure_server(port):
            show(f"http://127.0.0.1:{port}/p/{a.id}")
        return 0
    if a.cmd == "receive":
        wid, rec = receive(Path(a.file).expanduser())
        n, t = progress(rec)
        print(f"{n} of {t} answered by {rec.get('to') or 'the client'}; in {(STORE / wid / 'notes.md').relative_to(ROOT)}")
        return 0
    if a.cmd == "pull":
        got = pull(a.id)
        if not got:
            print("No hosted forms out.")
        for wid, rec, changed in got:
            n, t = progress(rec)
            print(f"{wid}  {rec.get('to') or 'someone'}: {n} of {t} answered"
                  f"{', finished' if rec.get('done') else ''}{'' if changed else ' (no change)'}")
        return 0
    if a.cmd == "host":
        return host(a.project)
    if a.cmd == "notes":
        d = read_deck(a.id)
        atomic_write(folder(a.id) / "notes.md", notes(d))
        print((folder(a.id) / "notes.md").relative_to(ROOT))
        return 0
    if a.cmd == "library":
        for b in library():
            flag = "fixed" if b.get("fixed") else "on" if b.get("on") else "off"
            print(f"{b['key']:<8} {b['kind']:<10} {flag:<5} {b['name']}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
