#!/usr/bin/env python3
"""doctor.py — lint the brain, not the build.

    python3 brain/doctor.py          # exits 1 on any FAIL
    python3 brain/doctor.py --quiet  # only FAILs and the summary

The safeguards that survive in a workspace like this are the ones a program refuses to
let you past, not the ones written in a README.

Three FAIL checks, three REPORT sections. The split is the whole design:

  FAIL      a rule with one owner and no legitimate exceptions
  REPORT    a signal that is often fine — printed, never enforced

Adding a FAIL for something with legitimate exceptions trains you to ignore the output,
which costs more than the check is worth.
"""

import re
import subprocess
import sys
from pathlib import Path

BRAIN = Path(__file__).resolve().parent
ROOT = BRAIN.parent

NOW_MAX = 2000  # chars. "If it would still be true in two weeks, it doesn't belong."
TOMBSTONE = "do not cite"

# Project constants come from brain/workspace.toml via config.py — never from this file.
# The two scripts used to carry a TRACKER_PREFIX each with nothing checking they agreed.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import (  # noqa: E402
    CONFIG, TRACKER_PREFIX, TASK_LABELS, PROJECT_NAME, GIT_REMOTE, IS_TEMPLATE, placeholders,
)


# brain/tasks.md line grammar. Files own task state; the tracker is a projection, so the
# projection pointer is part of the line and not a thing to remember at push time.
TASK_STATUSES = ("later", "todo", "doing", "blocked", "done")
_KEY = rf"{TRACKER_PREFIX}-\d+|" if TRACKER_PREFIX else ""
POINTER_DESC = f"{TRACKER_PREFIX}-n|—|skip" if TRACKER_PREFIX else "—|skip"
TASK_LINE = re.compile(
    r"^- `(?P<status>\w+)`"           # status
    r" · (?P<prio>P[1-4])"            # priority
    r" · (?P<labels>.*?)"             # labels, or a bare em dash for none
    rf" · (?P<link>{_KEY}—|skip)"     # projection pointer
    r" — \*\*(?P<title>.+?)\*\*\s*$"
)

# Directories whose .md files participate in [[link]] resolution.
LINK_DIRS = [BRAIN / "insights", BRAIN / "decisions", BRAIN / "braindumps",
             BRAIN / "explorations"]

# Files that describe what is true *now*. Only these may not carry a dead pointer.
# A dated record (a decision, an insight, a findings file) citing a since-superseded decision was
# correct when written; rewriting it would be falsifying the record, and the tombstone on
# the target is what protects the reader who follows the link.
CURRENT_STATE = [
    BRAIN / "now.md",
    BRAIN / "open-questions.md",
    ROOT / "AGENTS.md",
    ROOT / "CLAUDE.md",
]
CURRENT_STATE_DIRS: list = []
# Everything scanned for links and stale citations.
SCAN_DIRS = [BRAIN, ROOT / "docs"]
SKIP_PARTS = {"__pycache__", ".git", "archive", "context"}

fails: list[str] = []
notes: list[str] = []


def md_files(dirs):
    for d in dirs:
        if not d.exists():
            continue
        for p in sorted(d.rglob("*.md")):
            if SKIP_PARTS & set(p.parts):
                continue
            yield p


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


# ── FAIL 1 ── now.md is a pointer file, not a narrative ────────────────────────
def check_now_size():
    now = BRAIN / "now.md"
    if not now.exists():
        fails.append("brain/now.md is missing")
        return
    n = len(now.read_text(encoding="utf-8"))
    if n > NOW_MAX:
        over = n - NOW_MAX
        fails.append(
            f"brain/now.md is {n} chars, {over} over the {NOW_MAX} limit.\n"
            f"      Do not trim it — rewrite it from scratch. Accretion is what made it 16k.\n"
            f"      Anything still true in two weeks belongs in its owning file, linked from here."
        )
    else:
        notes.append(f"now.md {n}/{NOW_MAX} chars")


# ── FAIL 2 ── superseded and retired files announce themselves ─────────────────
def check_tombstones():
    checked = 0
    for p in md_files([BRAIN / "decisions"]):
        text = p.read_text(encoding="utf-8")
        head = text[:1200].lower()
        is_dead = bool(
            re.search(r"^status:\s*retired", text, re.M | re.I)
            or re.search(r"status:\s*\**superseded", text[:400], re.I)
        )
        if not is_dead:
            continue
        checked += 1
        if TOMBSTONE not in head:
            fails.append(
                f"{rel(p)} is superseded/retired but carries no tombstone.\n"
                f"      Add a header in the first lines containing \"{TOMBSTONE}\" and naming\n"
                f"      what replaced it. Stale content that announces itself can't be cited back at you."
            )
    notes.append(f"{checked} superseded/retired file(s), all tombstoned" if not fails else
                 f"{checked} superseded/retired file(s) checked")


# ── FAIL 3 ── a current-state file must not cite a dead one ────────────────────
def dead_decisions() -> dict[str, str]:
    dead = {}
    for p in md_files([BRAIN / "decisions"]):
        text = p.read_text(encoding="utf-8")
        if re.search(r"status:\s*\**superseded", text[:400], re.I):
            dead[p.stem] = rel(p)
    return dead


def check_stale_citations():
    dead = dead_decisions()
    if not dead:
        notes.append("no superseded decisions to police")
        return

    targets = [p for p in CURRENT_STATE if p.exists()] + list(md_files(CURRENT_STATE_DIRS))
    hits = 0
    for p in targets:
        for line_no, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            for stem in dead:
                if stem not in line:
                    continue
                low = line.lower()
                if any(w in low for w in ("supersed", "former", "retired", "cancel",
                                          "replaced", "do not cite", "was ")):
                    continue  # explicitly flagged as history
                hits += 1
                fails.append(
                    f"{rel(p)}:{line_no} — a current-state file cites superseded {stem}.\n"
                    f"      → {line.strip()[:88]}\n"
                    f"      Point it at the replacement, or mark the citation as historical."
                )
    if not hits:
        notes.append(f"{len(dead)} superseded decision(s), no current-state file cites them")


# ── FAIL 4 ── brain/tasks.md keeps its line grammar ────────────────────────────
def task_lines() -> list[tuple[int, str]]:
    """Candidate task lines: bullets starting with a backtick, outside fenced blocks.
    The fence check matters — the format template inside the code fence looks like a task
    line and is not one."""
    tasks = BRAIN / "tasks.md"
    if not tasks.exists():
        return []
    out, fenced = [], False
    for line_no, line in enumerate(tasks.read_text(encoding="utf-8").splitlines(), 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced and line.startswith("- `"):
            out.append((line_no, line))
    return out


def check_tasks():
    """Files own task state. The grammar is enforced because the projection pointer
    lives on the line — if the shape rots, the push to the tracker stops being mechanical
    and becomes a judgment call at the end of a long session, which is when it will be skipped."""
    tasks = BRAIN / "tasks.md"
    if not tasks.exists():
        fails.append(
            "brain/tasks.md is missing — it owns task state.\n"
            "      now.md cannot hold a backlog: a backlog is still true in two weeks."
        )
        return

    candidates = task_lines()
    if not candidates:
        notes.append("tasks.md has no task lines")
        return

    by_status: dict[str, int] = {}
    unmirrored = 0
    for line_no, line in candidates:
        m = TASK_LINE.match(line)
        if not m:
            fails.append(
                f"brain/tasks.md:{line_no} — task line does not match the grammar.\n"
                f"      → {line.strip()[:88]}\n"
                f"      Expected: - `status` · Pn · `label` … · {POINTER_DESC} — **Title**"
            )
            continue
        status, labels = m["status"], m["labels"].strip()
        if status not in TASK_STATUSES:
            fails.append(
                f"brain/tasks.md:{line_no} — unknown status `{status}`.\n"
                f"      → {m['title'][:70]}\n"
                f"      One of: {' '.join(TASK_STATUSES)}"
            )
            continue
        if labels != "—":
            for lab in re.findall(r"`([^`]+)`", labels):
                if lab not in TASK_LABELS:
                    fails.append(
                        f"brain/tasks.md:{line_no} — unknown label `{lab}`.\n"
                        f"      → {m['title'][:70]}\n"
                        f"      One of: {' '.join(TASK_LABELS)}, or — for none.\n"
                        f"      Labels are projected to the tracker; an invented one lands nowhere."
                    )
        by_status[status] = by_status.get(status, 0) + 1
        if m["link"] == "—":
            unmirrored += 1

    order = [s for s in TASK_STATUSES if s in by_status]
    notes.append("tasks " + " ".join(f"{by_status[s]} {s}" for s in order))
    if unmirrored:
        notes.append(f"{unmirrored} not yet projected to the tracker")

    check_no_projection_keys_in_prose()


def check_no_projection_keys_in_prose():
    """A tracker key may appear only in the pointer field, never in a note.

    Caught the hard way: cross-referencing one task from another by its tracker key makes the
    truth file depend on the projection's numbering — precisely backwards, and the keys
    silently pointed at the wrong issues the moment the tracker assigned them in a different
    order than expected. Cross-reference by *title*. The projection is downstream; nothing
    upstream may cite it."""
    tasks = BRAIN / "tasks.md"
    if not tasks.exists() or not TRACKER_PREFIX:
        return
    fenced = False
    for line_no, line in enumerate(tasks.read_text(encoding="utf-8").splitlines(), 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced or not re.search(rf"{TRACKER_PREFIX}-\d+", line):
            continue
        if TASK_LINE.match(line):
            continue  # the pointer field: the one legitimate home
        fails.append(
            f"brain/tasks.md:{line_no} — a tracker key appears outside the pointer field.\n"
            f"      → {line.strip()[:88]}\n"
            f"      Cross-reference the other task by *title*. Files are upstream of the\n"
            f"      projection, so nothing here may depend on the tracker's numbering."
        )


# ── REPORT ── task state versus what the projection last saw ───────────────────
def report_projection():
    """Not a failure. The tracker is a write-only projection and is *expected* to be stale
    between session ends. This prints what the next push owes it, so 'mirror at session end'
    is a visible number rather than a thing to remember."""
    rows = [(n, l) for n, l in task_lines() if TASK_LINE.match(l)]
    if not rows:
        return
    matches = [TASK_LINE.match(l) for _, l in rows]
    pending = [m for m in matches if m["link"] == "—"]
    skipped = [m for m in matches if m["link"] == "skip"]
    # "carries a pointer", not "is open in the tracker" — this reads a file, so it cannot
    # know the board's state. Claiming otherwise would be the laundering CLAUDE.md forbids.
    carried = len(rows) - len(pending) - len(skipped)
    print(f"  projection {len(rows)} task(s) · {carried} carry a tracker pointer · "
          f"{len(pending)} awaiting first push · {len(skipped)} never projected")
    for m in pending[:5]:
        print(f"               new: {m['title'][:64]}")
    if len(pending) > 5:
        print(f"               … and {len(pending) - 5} more")


# ── REPORT ── dated records pointing at superseded decisions ────────────────────────
def report_historical_citations():
    """Not a failure: a decision or findings file citing a since-superseded decision was correct
    when written. The tombstone on the target is the protection. Printed so the count is
    visible — if it grows fast, the supersession was probably badly communicated."""
    dead = dead_decisions()
    if not dead:
        return
    per: dict[str, int] = {}
    for p in md_files(SCAN_DIRS):
        if p.stem in dead:
            continue
        text = p.read_text(encoding="utf-8")
        for stem in dead:
            if stem in text:
                per[stem] = per.get(stem, 0) + 1
    if per:
        total = sum(per.values())
        print(f"  history    {total} dated-record citation(s) of superseded decisions "
              f"(fine — target is tombstoned):")
        for stem, c in sorted(per.items(), key=lambda kv: -kv[1]):
            print(f"               {stem} ({c} files)")


# ── REPORT ── unresolved [[links]] ─────────────────────────────────────────────
def report_links():
    """NOT a failure. CLAUDE.md: 'a link to a note that doesn't exist yet marks future work.'
    Enforcing this would break the convention it is meant to protect, so it prints."""
    known = {p.stem for d in LINK_DIRS if d.exists() for p in d.rglob("*.md")}
    known |= {p.stem for p in BRAIN.glob("*.md")}  # now, plan, project-brief…
    unresolved: dict[str, list[str]] = {}
    for p in md_files(SCAN_DIRS):
        for target in re.findall(r"\[\[([^\]|#]+?)\]\]", p.read_text(encoding="utf-8")):
            t = target.strip()
            if t and t not in known and not t.startswith("0"):
                unresolved.setdefault(t, []).append(rel(p))
            elif t.startswith("0") and t not in known:
                unresolved.setdefault(t, []).append(rel(p))
    if not unresolved:
        print("  links      all [[links]] resolve")
        return
    print(f"  links      {len(unresolved)} unresolved — future work, or a typo:")
    for t, srcs in sorted(unresolved.items(), key=lambda kv: -len(kv[1]))[:12]:
        print(f"               [[{t}]]  ({len(srcs)}×, e.g. {srcs[0]})")
    if len(unresolved) > 12:
        print(f"               … and {len(unresolved) - 12} more")


# ── REPORT ── one-owner rule: the same claim in many files ─────────────────────
def report_duplication():
    """Cheap proxy for the one-owner rule: which insight notes are restated, not linked."""
    counts: dict[str, int] = {}
    ins = BRAIN / "insights"
    if not ins.exists():
        return
    for p in md_files(SCAN_DIRS):
        text = p.read_text(encoding="utf-8")
        for note in ins.glob("*.md"):
            if f"[[{note.stem}]]" in text:
                counts[note.stem] = counts.get(note.stem, 0) + 1
    hot = sorted((c, n) for n, c in counts.items() if c >= 6)
    if hot:
        print(f"  one-owner  {len(hot)} note(s) linked from 6+ files — check they link, not restate:")
        for c, n in sorted(hot, reverse=True)[:5]:
            print(f"               {n} ({c} files)")


# ── REPORT ── question-number collisions ──────────────────────────────────────
def report_question_numbers():
    q = BRAIN / "open-questions.md"
    if not q.exists():
        return
    nums = [m for line in q.read_text(encoding="utf-8").splitlines()
            if not re.search(r"see (below|above)", line, re.I)  # cross-refs, not definitions
            for m in re.findall(r"\((Q\d+)\)", line)]
    dupes = sorted({n for n in nums if nums.count(n) > 1}, key=lambda s: int(s[1:]))
    if dupes:
        print(f"  questions  DUPLICATE numbers in open-questions.md: {', '.join(dupes)}")
        print("               two sessions numbered independently — renumber the one with fewer citations")
    else:
        highest = max((int(n[1:]) for n in nums), default=0)
        print(f"  questions  {len(set(nums))} unique, highest Q{highest}, no collisions")


# ── REPORT ── the tag vocabulary ───────────────────────────────────────────────
def report_tags():
    """Tags are global to the brain: a decision and an insight sharing one is the point
    (decision 0004). Unknown tags REPORT rather than FAIL — a new tag is usually legitimate,
    and failing on it would train you to ignore this output. What is worth seeing is the
    shape of the vocabulary: singletons that should have been [[links]], and files with no
    tags at all, which are invisible to every tag query and to the Obsidian graph."""
    vocab, counts, untagged = {}, {}, []
    tags_file = BRAIN / "tags.md"
    if tags_file.exists():
        for line in tags_file.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^-\s+`([a-z0-9-]+)`\s*—\s*(.+)$", line.strip())
            if m:
                vocab[m.group(1)] = m.group(2)

    for path in md_files([BRAIN / "decisions", BRAIN / "insights", BRAIN / "braindumps",
                          BRAIN / "briefings", BRAIN / "explorations"]):
        if path.name == "README.md" or path.stem.startswith("0000"):
            continue
        text = path.read_text(encoding="utf-8")
        found = []
        if text.startswith("---"):
            fm = text[3:text.find("\n---", 3)] if "\n---" in text[3:] + "\n---" else ""
            tm = re.search(r"^tags:\s*\[(.*?)\]", fm, re.M)
            if tm:
                found = [t.strip().strip("\"'") for t in tm.group(1).split(",") if t.strip()]
        if not found:
            untagged.append(rel(path))
        for t in found:
            counts[t] = counts.get(t, 0) + 1

    if not vocab and not counts:
        print("  tags       no tags yet — brain/tags.md owns the vocabulary")
        return
    unknown = sorted(t for t in counts if vocab and t not in vocab)
    unused = sorted(t for t in vocab if t not in counts)
    top = sorted(counts.items(), key=lambda kv: -kv[1])[:6]
    print(f"  tags       {len(counts)} in use over {sum(counts.values())} file(s)"
          + (f", {len(vocab)} defined in tags.md" if vocab else ", tags.md defines none yet"))
    if top:
        print("               " + " · ".join(f"{t} ({c})" for t, c in top))
    if unknown:
        print(f"               not in tags.md: {', '.join(unknown)} — define or rename")
    if unused:
        print(f"               defined but unused: {', '.join(unused)}")
    singles = sorted(t for t, c in counts.items() if c == 1)
    if singles and sum(counts.values()) >= 30:
        print(f"               one file only: {', '.join(singles)} — a theme of one is a [[link]]")
    if untagged:
        print(f"               {len(untagged)} file(s) with no tags, e.g. {untagged[0]}")


# ── REPORT ── the lenses the reviewer can be pointed at ───────────────────────
def report_lenses():
    """`brain/lenses/` holds what "good" means, one file per domain, and `/reviewer` runs
    exactly one per pass. Not a FAIL: a clone legitimately ships `craft.md` unfilled, and the
    reviewer is required to say so in its own verdict. What is worth printing is which lenses
    exist and which are still template — an unfilled lens reviewed against silently is the
    failure mode the whole split was meant to prevent."""
    d = BRAIN / "lenses"
    if not d.exists():
        print("  lenses     brain/lenses/ is missing — /reviewer has no standard to read")
        return
    found, unfilled = [], []
    for path in sorted(d.glob("*.md")):
        if path.name == "README.md":
            continue
        found.append(path.stem)
        text = path.read_text(encoding="utf-8")
        # The house convention for an unwritten section: an italic parenthetical.
        if re.search(r"^\*\(", text, re.M) or "{{" in text:
            unfilled.append(path.stem)
    if not found:
        print("  lenses     none defined — /reviewer has no standard to read")
        return
    print(f"  lenses     {len(found)}: {', '.join(found)}")
    if unfilled:
        print(f"               still template: {', '.join(unfilled)} — /setup fills these, and\n"
              f"               the reviewer must say so in its verdict until they are written")


# ── REPORT ── explorations, and whether any of them ever landed ───────────────
def report_explorations():
    """An exploration is options, not a decision (AGENTS.md). Two things rot here and neither
    is a rule with no exceptions, so both print. A file with no verdicts is an unfinished
    session — normal mid-run, stale after a week. A file whose surviving direction never
    produced a decision is the seam failing quietly: the work moved on, and the record never
    recorded what was picked."""
    d = BRAIN / "explorations"
    if not d.exists():
        return
    files = [p for p in sorted(d.glob("*.md")) if p.name != "README.md"]
    if not files:
        print("  explore    no explorations filed yet — /explore writes them")
        return
    no_verdict, unlanded = [], []
    for path in files:
        text = path.read_text(encoding="utf-8")
        if not re.search(r"^Verdict:", text, re.M | re.I):
            no_verdict.append(rel(path))
            continue
        live = len(re.findall(r"^Verdict:\s*live", text, re.M | re.I))
        # Did any decision link back? That link is the only legitimate seam.
        cited = any(f"[[{path.stem}]]" in q.read_text(encoding="utf-8")
                    for q in md_files([BRAIN / "decisions"]))
        if live and not cited:
            unlanded.append(rel(path))
    print(f"  explore    {len(files)} exploration(s) filed")
    for f in no_verdict:
        print(f"               no verdicts yet: {f} — every direction needs live|rejected")
    for f in unlanded:
        print(f"               live direction, no decision cites it: {f}\n"
              f"               → picking one means a numbered decision that links back")


# ── REPORT ── is this workspace actually configured? ──────────────────────────
def report_config():
    """A half-configured workspace should announce itself rather than quietly run with a
    placeholder in the page title and the tracker push."""
    miss = placeholders(CONFIG)
    if not (BRAIN / "workspace.toml").exists():
        print("  config     brain/workspace.toml is missing — run /setup (defaults in use)")
    elif miss:
        print(f"  config     {len(miss)} unfilled: {', '.join(miss)} — run /setup")
    elif IS_TEMPLATE:
        print(f"  config     {PROJECT_NAME} — the template repo itself; a clone runs /setup")
    else:
        tr = TRACKER_PREFIX or "no tracker"
        print(f"  config     {PROJECT_NAME} · {tr} · remote {'on' if GIT_REMOTE else 'off'}")


# ── REPORT ── has the page been regenerated since the files moved? ────────────
def report_feed():
    """The page is a projection. Stale is not a failure — it is a projection, and it is
    expected to lag between wrap-ups. Printed so /close has a number to act on."""
    out = BRAIN / "feed.html"
    if not out.exists():
        print("  feed       not generated yet — python3 brain/feed.py")
        return
    age = out.stat().st_mtime
    stale = [s for s in ("now.md", "plan.md", "tasks.md", "feed-items.md", "open-questions.md")
             if (BRAIN / s).exists() and (BRAIN / s).stat().st_mtime > age]
    print("  feed       current" if not stale
          else f"  feed       STALE behind {', '.join(stale)} — python3 brain/feed.py")


# ── shared helpers for the reports below ──────────────────────────────────────
def _inbound() -> dict:
    """`stem -> {citing files}` across the scanned tree.

    A decision is cited three ways in practice — `[[0007-slug]]`, `[[0007]]`, and the bare
    token `0007` in prose — so all three count. Without that, every decision cited the way
    the charter actually recommends (restate the content, cite the number) would read as an
    orphan."""
    texts = {p: p.read_text(encoding="utf-8") for p in md_files(SCAN_DIRS)}
    keys = {}
    for p in texts:
        keys.setdefault(p.stem, p)
        m = re.match(r"^(\d{4})-", p.name)
        if m:
            keys.setdefault(m.group(1), p)
    out: dict = {p.stem: set() for p in texts}
    for src, text in texts.items():
        for key, target in keys.items():
            if target == src:
                continue
            hit = (f"[[{key}]]" in text or f"[[{key}|" in text
                   or (len(key) == 4 and key.isdigit()
                       and re.search(rf"(?<![\w-]){key}(?![\w-])", text)))
            if hit:
                out[target.stem].add(rel(src))
    return out


def _last_touched() -> dict:
    """`relative path -> YYYY-MM-DD`, the later of git history and filesystem mtime.

    mtime alone is wrong in a fresh clone — checkout stamps every file with the clone time,
    so nothing would ever look stale. git alone is wrong for edits you have not committed
    yet. The later of the two is right in both cases, and degrades to mtime outside a repo."""
    from datetime import datetime as _dt
    dates: dict = {}
    try:
        out = subprocess.run(
            ["git", "-C", str(ROOT), "log", "--pretty=format:%ad", "--date=short",
             "--name-only"], capture_output=True, text=True, timeout=20)
        current = None
        for line in out.stdout.splitlines():
            line = line.strip()
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", line):
                current = line
            elif line and current:
                dates.setdefault(line, current)
    except Exception:
        pass
    for p in md_files(SCAN_DIRS):
        r = rel(p)
        mt = _dt.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d")
        dates[r] = max(dates.get(r, mt), mt)
    return dates


# ── REPORT ── notes nothing points at ────────────────────────────────────────
def report_orphans():
    """The inverse of the unresolved-link report, and the blind spot it left: a link pointing
    at nothing is visible, a note nothing points at is invisible. An orphan is not wrong —
    the newest decision has not been cited yet by definition — but a decision or insight that
    stays unreferenced is one the work never actually used."""
    inbound = _inbound()
    orphans = []
    for path in md_files([BRAIN / "decisions", BRAIN / "insights"]):
        if path.name == "README.md" or path.stem.startswith("0000"):
            continue
        if not inbound.get(path.stem):
            orphans.append(rel(path))
    if not orphans:
        print("  orphans    every decision and insight is cited somewhere")
        return
    print(f"  orphans    {len(orphans)} note(s) nothing links to or cites:")
    for o in orphans[:6]:
        print(f"               {o}")
    if len(orphans) > 6:
        print(f"               … and {len(orphans) - 6} more")


# ── REPORT ── has now.md fallen behind the brain? ────────────────────────────
def report_now_freshness():
    """The portability question, made checkable. `now.md` is what the next session — or the
    next device — reads first, so the risk is not that it is wrong but that the work moved
    after it was last written. Reported, never enforced: mid-session it is *expected* to
    lag, and the fix is `/close`."""
    dates = _last_touched()
    now_rel = rel(BRAIN / "now.md")
    now_date = dates.get(now_rel)
    if not now_date:
        return
    newer = sorted(((d, f) for f, d in dates.items()
                    if f != now_rel and f.startswith("brain/") and d > now_date), reverse=True)
    if not newer:
        print(f"  now.md     current as of {now_date}")
        return
    print(f"  now.md     last written {now_date}; {len(newer)} brain file(s) changed since "
          f"— run /close")
    for d, f in newer[:4]:
        print(f"               {d}  {f}")
    if len(newer) > 4:
        print(f"               … and {len(newer) - 4} more")


# ── REPORT ── tombstoned files still living in the brain ─────────────────────
def report_archive_candidates():
    """The mirror of the tombstone FAIL. That one catches a dead file with no warning label;
    this one catches a file that carries the label but never moved, which is how `archive/`
    stays empty while the live brain fills with material nobody may cite."""
    stragglers = []
    for path in md_files(SCAN_DIRS):
        if path.stem.startswith("0000"):
            continue  # the template's "copy me; do not cite" is not a tombstone
        if TOMBSTONE in path.read_text(encoding="utf-8")[:1200].lower():
            stragglers.append(rel(path))
    if not stragglers:
        return
    print(f"  archive    {len(stragglers)} tombstoned file(s) still outside archive/:")
    for s in stragglers:
        print(f"               {s} — move it, so the live brain holds only citable material")


# ── REPORT ── the glossary ────────────────────────────────────────────────────
def report_glossary():
    """Proper nouns are the class of information a new session most often lacks, and the one
    most likely to be invented confidently. Counting is all this can honestly do."""
    p = BRAIN / "glossary.md"
    if not p.exists():
        print("  glossary   brain/glossary.md is missing — it owns people and project shorthand")
        return
    text = p.read_text(encoding="utf-8")
    def count(section: str) -> int:
        m = re.search(rf"^## {section}\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
        return len(re.findall(r"^-\s+\*\*", m.group(1), re.M)) if m else 0
    hot, full = count("Hot"), count("Full")
    if hot + full == 0:
        print("  glossary   empty — seed it at /setup from the People answers")
        return
    warn = "  ← over a dozen; demote the cold ones" if hot > 12 else ""
    print(f"  glossary   {hot} hot · {full} full{warn}")
    inferred = len(re.findall(r"`?inferred`?", text, re.I))
    if inferred:
        print(f"               {inferred} entry/entries marked inferred — good, keep it that way")


def main() -> int:
    quiet = "--quiet" in sys.argv
    print("brain doctor\n")

    check_now_size()
    check_tombstones()
    check_stale_citations()
    check_tasks()

    if not quiet:
        print("reports (never fail the run)")
        report_projection()
        report_links()
        report_historical_citations()
        report_duplication()
        report_question_numbers()
        report_tags()
        report_config()
        report_glossary()
        report_lenses()
        report_explorations()
        report_orphans()
        report_archive_candidates()
        report_now_freshness()
        report_feed()
        print()

    if fails:
        print(f"FAIL — {len(fails)} problem(s)\n")
        for i, f in enumerate(fails, 1):
            print(f"  {i}. {f}\n")
        return 1

    print("PASS — " + " · ".join(notes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
