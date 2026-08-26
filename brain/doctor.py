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
import sys
from pathlib import Path

BRAIN = Path(__file__).resolve().parent
ROOT = BRAIN.parent

NOW_MAX = 2000  # chars. "If it would still be true in two weeks, it doesn't belong."
TOMBSTONE = "do not cite"

# ── Project configuration — the one block to edit when adopting this template ───────────
# TRACKER_PREFIX: the issue-key prefix of your external tracker (e.g. "PROJ" for PROJ-12).
# None if the project has no tracker: pointers are then `—` (not yet projected) or `skip`.
TRACKER_PREFIX: str | None = "PROJ"
# TASK_LABELS: the label vocabulary for brain/tasks.md. `bar` = inside the current stage's
# exit criterion; `deferred` = real work explicitly NOT a prerequisite for the current
# stage, which must never be presented as one. Labels encode the stage-exit criterion in
# the grammar rather than in prose, so "is this required before we can move on?" is a grep
# and not a judgement call.
TASK_LABELS = ("build", "spec", "evals", "method", "blocked-on-external", "bar", "deferred")

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
LINK_DIRS = [BRAIN / "insights", BRAIN / "decisions", BRAIN / "braindumps"]

# Files that describe what is true *now*. Only these may not carry a dead pointer.
# A dated record (an ADR, an insight, a findings file) citing a since-superseded ADR was
# correct when written; rewriting it would be falsifying the record, and the tombstone on
# the target is what protects the reader who follows the link.
CURRENT_STATE = [
    BRAIN / "now.md",
    BRAIN / "open-questions.md",
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
def dead_adrs() -> dict[str, str]:
    dead = {}
    for p in md_files([BRAIN / "decisions"]):
        text = p.read_text(encoding="utf-8")
        if re.search(r"status:\s*\**superseded", text[:400], re.I):
            dead[p.stem] = rel(p)
    return dead


def check_stale_citations():
    dead = dead_adrs()
    if not dead:
        notes.append("no superseded ADRs to police")
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
        notes.append(f"{len(dead)} superseded ADR(s), no current-state file cites them")


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
        if fenced or not re.search(rf"{TRACKER_PREFIX}-\\d+", line):
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


# ── REPORT ── dated records pointing at superseded ADRs ────────────────────────
def report_historical_citations():
    """Not a failure: an ADR or findings file citing a since-superseded decision was correct
    when written. The tombstone on the target is the protection. Printed so the count is
    visible — if it grows fast, the supersession was probably badly communicated."""
    dead = dead_adrs()
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
        print(f"  history    {total} dated-record citation(s) of superseded ADRs "
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
