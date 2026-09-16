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

TOMBSTONE = "do not cite"

# Project constants come from brain/workspace.toml via config.py — never from this file.
# The two scripts used to carry a TRACKER_PREFIX each with nothing checking they agreed.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import (  # noqa: E402
    CONFIG, TRACKER_PREFIX, TASK_LABELS, PROJECT_NAME, GIT_REMOTE, IS_TEMPLATE, placeholders,
    MULTI_PROJECT, PROJECT_KEYS, PROJECT_LABEL, PROJECT_VALUES,
    REMINDER_ROUTE, REMINDER_TARGET, REMINDER_CAN_SCHEDULE,
)

# chars. "If it would still be true in two weeks, it doesn't belong." A second strand of work
# buys a small allowance and not a second screen: now.md answers "what is happening" for the
# whole engagement, and an engagement with six strands still gets one screen to say it in.
NOW_MAX = 2000 + 500 * max(0, len(PROJECT_KEYS) - 1)

# Which record classes name the strand they belong to. Braindumps and briefings are
# deliberately absent: both are verbatim captures that legitimately span the engagement, and
# routing is what assigns a project — to the decision or task that comes out, not to the dump.
PROJECT_TAGGED_DIRS = ("decisions", "insights", "explorations", "workshops")

# Decision filenames are `YYYY-MM-DD-slug.md`: the date orders them, the slug identifies them.
# The old `NNNN-slug.md` claimed a number from a pool shared with every parallel session, so
# two sessions writing at once collided by construction. Legacy names still resolve and are
# reported, never failed — a half-migrated tree has to keep working. `brain/redate.py` migrates.
DATED_NAME = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]*$")
NUMBERED_NAME = re.compile(r"^(\d{4})-(?!\d{2}-\d{2})[a-z0-9][a-z0-9-]*$")


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
             BRAIN / "explorations", BRAIN / "workshops"]

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


def frontmatter(text: str) -> str:
    """The raw YAML-ish block between the opening and closing `---`, or ""."""
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    return text[3:end] if end != -1 else ""


def record_project(text: str) -> str | None:
    """The `project:` value in a record's frontmatter, or None if it carries none."""
    m = re.search(r"^project:\s*(.+?)\s*$", frontmatter(text), re.M)
    return m.group(1).strip().strip("\"'") if m else None


def is_template_file(p: Path) -> bool:
    """README and the `0000-` decision template describe the format; they are not records."""
    return p.name == "README.md" or p.stem.startswith("0000")


# ── FAIL 0 ── every record names the strand of work it belongs to ──────────────
def check_record_projects():
    """One engagement can carry several projects, and the records must not blend.

    The failure this prevents is concrete: a question raised about one strand surfaced in the
    owner's feed looking like business from another, and he answered the wrong project. The
    fix is a `project:` key in frontmatter and a filter in every projection —
    compartmentalize in the projection, never in the storage.

    Silent below two strands. A workspace with one project has nothing to mix up, so the
    tagging would be pure ceremony; it switches on with the second key in `workspace.toml`."""
    if not MULTI_PROJECT:
        notes.append("one project — records carry no `project:` key")
        return
    missing, unknown, counts = [], [], {}
    for d in PROJECT_TAGGED_DIRS:
        for path in md_files([BRAIN / d]):
            if is_template_file(path):
                continue
            value = record_project(path.read_text(encoding="utf-8"))
            if not value:
                missing.append(rel(path))
            elif value not in PROJECT_VALUES:
                unknown.append((rel(path), value))
            else:
                counts[value] = counts.get(value, 0) + 1
    if missing:
        fails.append(
            f"{len(missing)} record(s) name no project, and this engagement carries "
            f"{len(PROJECT_KEYS)}.\n"
            "      → " + "\n      → ".join(missing[:6])
            + (f"\n      … and {len(missing) - 6} more" if len(missing) > 6 else "") + "\n"
            f"      Add `project:` to the frontmatter. One of: {' '.join(PROJECT_KEYS)}, or\n"
            f"      `all` for a record that governs the whole engagement. An untagged record\n"
            f"      is invisible to every filtered view."
        )
    for path, value in unknown:
        fails.append(
            f"{path} — unknown project `{value}`.\n"
            f"      One of: {' '.join(PROJECT_KEYS)}, or `all`.\n"
            f"      Keys are declared in brain/workspace.toml under [projects]; an invented\n"
            f"      one lands in no view at all."
        )
    if counts and not missing and not unknown:
        notes.append("projects " + " ".join(f"{counts[k]} {k}" for k in sorted(counts)))


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


def task_sections() -> dict:
    """`line number -> project key` for every task line, from the nearest `##` heading above it.

    Tasks carry their strand in the document structure rather than in the line grammar: the
    line is already dense, and a heading is what the owner reads anyway. A heading matches by
    key or by display label, either case."""
    tasks = BRAIN / "tasks.md"
    if not tasks.exists():
        return {}
    by_name = {k.lower(): k for k in PROJECT_KEYS}
    by_name.update({v.lower(): k for k, v in PROJECT_LABEL.items()})
    out, current, fenced = {}, None, False
    for line_no, line in enumerate(tasks.read_text(encoding="utf-8").splitlines(), 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        if line.startswith("## "):
            current = by_name.get(line[3:].strip().lower())
        elif line.startswith("- `"):
            out[line_no] = current
    return out


def check_task_projects():
    """A task under no project heading belongs to nothing, and the tracker push has nowhere
    to file it. Silent below two strands, like every other part of this."""
    if not MULTI_PROJECT:
        return
    sections = task_sections()
    orphans = [n for n, key in sections.items() if key is None]
    if not orphans:
        if sections:
            per: dict = {}
            for key in sections.values():
                per[key] = per.get(key, 0) + 1
            notes.append("tasks by project " + " ".join(f"{per[k]} {k}" for k in sorted(per)))
        return
    fails.append(
        f"brain/tasks.md — {len(orphans)} task line(s) sit under no project heading "
        f"(line{'s' if len(orphans) > 1 else ''} {', '.join(str(n) for n in orphans[:8])}"
        + (" …" if len(orphans) > 8 else "") + ").\n"
        f"      Every task belongs to one strand. Group them under a `## ` heading naming\n"
        f"      the project: {' · '.join(PROJECT_LABEL[k] for k in PROJECT_KEYS)}"
    )


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

    check_task_projects()
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
def slug_of(stem: str) -> str:
    """`2026-09-15-focus-mode-is-the-default` → `focus-mode-is-the-default`.

    The date orders the log; the slug is the identity. Links are written as `[[slug]]` so a
    citation survives a corrected date, and so nothing in the brain depends on a position in
    a sequence that two parallel sessions both try to claim."""
    m = re.match(r"^\d{4}-\d{2}-\d{2}-(.+)$", stem)
    return m.group(1) if m else stem


def link_keys() -> dict:
    """Every string a `[[link]]` may legitimately use → the file it resolves to.

    Three forms, because all three are written in practice: the full stem, the bare slug of a
    dated file, and the bare number of a legacy `NNNN-` one."""
    files = [p for d in LINK_DIRS if d.exists() for p in d.rglob("*.md")]
    files += list(BRAIN.glob("*.md"))  # now, plan, project-brief…
    keys: dict = {}
    slugs: dict = {}
    for p in files:
        keys.setdefault(p.stem, p)
        if DATED_NAME.match(p.stem):
            slugs.setdefault(slug_of(p.stem), []).append(p)
        m = NUMBERED_NAME.match(p.stem)
        if m:
            keys.setdefault(m.group(1), p)
    for slug, paths in slugs.items():
        # An ambiguous slug is unciteable, which check_slug_collisions() fails on. Resolve it
        # to the first so one bad pair does not print as a hundred broken links.
        keys.setdefault(slug, paths[0])
    return keys


# ── FAIL 6 ── two records cannot share one slug ────────────────────────────────
def check_slug_collisions():
    """`[[the-portal-is-live]]` has to mean one file. Two decisions written under the same
    slug on different days are each other's broken link, and no reader can tell which one a
    citation meant — the one case in this scheme with no legitimate exception."""
    slugs: dict = {}
    for d in LINK_DIRS:
        if not d.exists():
            continue
        for path in d.rglob("*.md"):
            if is_template_file(path) or not DATED_NAME.match(path.stem):
                continue
            slugs.setdefault(slug_of(path.stem), []).append(rel(path))
    for slug, paths in sorted(slugs.items()):
        if len(paths) > 1:
            fails.append(
                f"two records share the slug `{slug}`, so `[[{slug}]]` names neither.\n"
                "      → " + "\n      → ".join(paths) + "\n"
                f"      Rename one to say what makes it different. The date orders the log;\n"
                f"      the slug is the identity, and an identity has to be unique."
            )


def report_links():
    """NOT a failure. CLAUDE.md: 'a link to a note that doesn't exist yet marks future work.'
    Enforcing this would break the convention it is meant to protect, so it prints."""
    known = set(link_keys())
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
    ([[tags-are-global-and-the-vault-is-the-graph]]). Unknown tags REPORT rather than FAIL —
    a new tag is usually legitimate,
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
                          BRAIN / "briefings", BRAIN / "explorations",
                          BRAIN / "workshops"]):
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
    no_verdict, unlanded, thin, stale = [], [], [], []
    for path in files:
        text = path.read_text(encoding="utf-8")

        # A direction with no specimen renders as an empty frame in `spread.py` — which is
        # the point of showing the gap rather than hiding it, but eight of them means the
        # page is prose again and there is nothing to compare at a glance.
        dirs = len(re.findall(r"^###\s+", text, re.M))
        specs = len(re.findall(r"^```specimen\b", text, re.M))
        if dirs and specs < dirs:
            thin.append((rel(path), dirs - specs, dirs))
        page = path.with_suffix(".html")
        if dirs and (not page.exists() or page.stat().st_mtime < path.stat().st_mtime):
            stale.append(rel(path))

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
    for f, missing, total in thin:
        print(f"               {missing} of {total} directions have no specimen: {f}")
    for f in stale:
        print(f"               page not rendered or older than the file: {f}\n"
              f"               → python3 brain/spread.py")


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


# ── REPORT ── is anything drafted and still waiting on the owner to send it? ──
def report_drafts():
    """A message written for the owner and never sent is the cheapest thing in the workspace
    to lose, and losing it costs a week of someone else's waiting.

    The format is `brain/drafts/README.md`. Three things break here: a draft addressed to
    nobody cannot be sent; a draft still unsent after a week is either forgotten or was never
    needed; and a file whose name misses `YYYY-MM-DD-slug.md` is invisible to the feed, which
    is the same as not existing.
    """
    folder = BRAIN / "drafts"
    if not folder.exists():
        return
    files = [p for p in sorted(folder.glob("*.md")) if p.name != "README.md"]
    if not files:
        print("  drafts     none written — a message for the owner to send lands here")
        return

    from datetime import date
    today = date.today()
    unsent, stale, unaddressed, badname, nosentdate = [], [], [], [], []
    for path in files:
        m = re.match(r"^(\d{4}-\d{2}-\d{2})-(.+)\.md$", path.name)
        if not m:
            badname.append(rel(path))
            continue
        text = path.read_text(encoding="utf-8")
        fm = re.match(r"^---\n(.*?)\n---", text, re.S)
        meta = {}
        if fm:
            for ln in fm.group(1).splitlines():
                k, _, v = ln.partition(":")
                if _:
                    meta[k.strip()] = v.strip()
        sent = (meta.get("status", "draft").lower() == "sent")
        if sent:
            if not meta.get("sent"):
                nosentdate.append(rel(path))
            continue
        unsent.append(rel(path))
        if not meta.get("to"):
            unaddressed.append(rel(path))
        try:
            days = (today - date.fromisoformat(m.group(1))).days
        except ValueError:
            days = 0
        if days >= 7:
            stale.append((rel(path), days))

    print(f"  drafts     {len(files)} draft(s) · {len(unsent)} waiting on the owner to send")
    for f in unaddressed:
        print(f"               no `to:` — cannot be sent: {f}")
    for f, d in stale:
        print(f"               unsent for {d} days: {f}\n"
              "               → send it, or say why it is not needed and mark it")
    for f in nosentdate:
        print(f"               status: sent but no `sent:` date: {f}")
    for f in badname:
        print(f"               name is not YYYY-MM-DD-slug.md, so the feed cannot see it: {f}")


# ── REPORT ── is there a brief, was it agreed, and is anything in it unsourced? ─
def report_brief():
    """The brief is the gate `/brief` exists to hold: the owner's yes to a stated
    understanding of the project, before the work advances on an unstated one.

    Three things rot here, and none of them is a rule without exceptions.

    A brief with no `Status:` line has never been put in front of anyone. An *approved* brief
    naming no decision is a verbal yes, which the record does not keep. And a section of prose
    carrying no `^[…]` source tag is a claim about a client with nothing behind it — which is
    the charter's "label evidence, never launder it" rule, made countable.
    """
    path = BRAIN / "project-brief.md"
    if not path.exists():
        print("  brief      brain/project-brief.md is missing")
        return
    text = path.read_text(encoding="utf-8")

    m = re.search(r"^Status:\s*(.+)$", text, re.M)
    if not m:
        print("  brief      no Status: line — nothing records whether it was ever agreed\n"
              "               → add `Status: draft` under the title, then /brief")
    elif m.group(1).strip().lower().startswith("approved"):
        if not re.search(r"\[\[\d{4}", m.group(1)):
            print("  brief      approved but names no decision — a verbal yes the record "
                  "does not keep\n"
                  "               → Status: approved YYYY-MM-DD · [[decision-slug]]")
        else:
            print(f"  brief      {m.group(1).strip()}")
    else:
        print(f"  brief      {m.group(1).strip()} — awaiting the owner")

    # Sections holding real prose but no attribution, and sections still holding the template's
    # own parenthetical prompt. Both are printed by name so there is something to act on.
    unsourced, unwritten = [], []
    for sec in re.finditer(r"^##\s+(.+?)\s*\n(.*?)(?=^##\s|\Z)", text, re.M | re.S):
        name, body = sec.group(1).strip(), sec.group(2).strip()
        if not body or re.fullmatch(r"\*\(.*?\)\*", body, re.S):
            unwritten.append(name)
        elif "^[" not in body:
            unsourced.append(name)
    if unwritten:
        print(f"               {len(unwritten)} section(s) unwritten: {', '.join(unwritten)}")
    if unsourced:
        print(f"               {len(unsourced)} section(s) with no source tag: "
              f"{', '.join(unsourced)}\n"
              "               → ^[who · where · when](link), or ^[inferred] if it is yours")

    page = BRAIN / "brief.html"
    if not page.exists():
        if not IS_TEMPLATE:
            print("               page not rendered — python3 brain/brief.py")
    else:
        stale = [f for f in ("project-brief.md", "open-questions.md", "plan.md", "tasks.md")
                 if (BRAIN / f).exists()
                 and (BRAIN / f).stat().st_mtime > page.stat().st_mtime]
        if stale:
            print(f"               page STALE behind {', '.join(stale)} — "
                  "python3 brain/brief.py")


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

    A record is cited two ways in practice — by its full stem, `[[2026-09-15-the-slug]]`, and
    by the slug alone, `[[the-slug]]` — plus, in a tree not yet migrated, by a legacy decision's
    bare number. All of them count. Without that, every decision cited the way the charter
    actually recommends would read as an orphan."""
    texts = {p: p.read_text(encoding="utf-8") for p in md_files(SCAN_DIRS)}
    keys = {}
    for p in texts:
        keys.setdefault(p.stem, p)
        if DATED_NAME.match(p.stem):
            keys.setdefault(slug_of(p.stem), p)
        # A legacy `NNNN-slug` is still cited by its bare number. A dated `YYYY-MM-DD-slug`
        # must NOT be — the leading group is the year, and every mention of "2026" would
        # otherwise read as a citation of every decision written in it.
        m = NUMBERED_NAME.match(p.stem)
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
    yet. The later of the two is right in both cases, and degrades to mtime outside a repo.

    Values are full ISO timestamps, not dates. At date granularity a decision written an hour
    after `now.md` was rewritten reads as *not* newer, which silences the freshness report for
    the rest of the day — and the rest of the day is exactly when a long session drifts."""
    from datetime import datetime as _dt
    dates: dict = {}
    try:
        out = subprocess.run(
            ["git", "-C", str(ROOT), "log", "--pretty=format:%ad", "--date=iso-strict",
             "--name-only"], capture_output=True, text=True, timeout=20)
        current = None
        for line in out.stdout.splitlines():
            line = line.strip()
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}T[\d:]{8}[+-][\d:]+", line):
                current = line[:19]
            elif line and current:
                dates.setdefault(line, current)
    except Exception:
        pass
    for p in md_files(SCAN_DIRS):
        r = rel(p)
        mt = _dt.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%dT%H:%M:%S")
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
    # In the boilerplate itself `now.md` is a placeholder a clone fills in, so it can never be
    # "fresh" and this report would advise /close forever — which is how a report teaches you
    # to skip reading the reports.
    if IS_TEMPLATE:
        print("  now.md     placeholder — the template ships blank; a clone writes it at /setup")
        return
    dates = _last_touched()
    now_rel = rel(BRAIN / "now.md")
    now_date = dates.get(now_rel)
    if not now_date:
        return
    newer = sorted(((d, f) for f, d in dates.items()
                    if f != now_rel and f.startswith("brain/") and d > now_date), reverse=True)
    if not newer:
        print(f"  now.md     current as of {now_date[:10]}")
        return
    print(f"  now.md     last written {now_date[:10]}; {len(newer)} brain file(s) changed since "
          f"— run /close")
    for d, f in newer[:4]:
        print(f"               {d[:10]}  {f}")
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


# ── FAIL 5 ── a question in the feed says which project it is about ────────────
def check_feed_item_projects():
    """The failure that produced this check: two items reached the owner's feed reading like
    business from the strand he had open, and were about another one. He answered the wrong
    project. A question with no strand on it is a question asked of the wrong context."""
    if not MULTI_PROJECT:
        return
    path = BRAIN / "feed-items.md"
    if not path.exists():
        return
    bad = []
    for chunk in re.split(r"\n(?=## FEED-)", path.read_text(encoding="utf-8"))[1:]:
        head = chunk.split("\n", 1)[0]
        m = re.match(r"##\s*(FEED-\d+)", head)
        if not m:
            continue
        value = re.search(r"^project:\s*(\S+)\s*$", chunk, re.M)
        if not value:
            bad.append((m.group(1), None))
        elif value.group(1) not in PROJECT_VALUES:
            bad.append((m.group(1), value.group(1)))
    for item, value in bad:
        fails.append(
            f"brain/feed-items.md — {item} "
            + (f"names unknown project `{value}`." if value else "names no project.") + "\n"
            f"      Add a `project:` line. One of: {' '.join(PROJECT_KEYS)}, or `all`.\n"
            f"      The feed renders it as a chip and filters on it; without one the owner\n"
            f"      reads the question against whichever strand he happens to have open."
        )


# ── REPORT ── decision filenames, and what a numbered one still costs ──────────
def report_decision_names():
    """A decision is `YYYY-MM-DD-slug.md`. The date orders the log; the slug is the identity
    that links point at. Neither is claimed from a pool, so two sessions writing at the same
    time produce two files that merge clean — which is exactly what the old `NNNN-` names
    could not do, because the next number depends on a commit the session has not fetched.

    Legacy names are reported, never failed: a half-migrated tree has to keep working, and
    the rename is one command."""
    d = BRAIN / "decisions"
    if not d.exists():
        return
    dated, numbered, odd = [], [], []
    for path in sorted(d.glob("*.md")):
        if is_template_file(path):
            continue
        if DATED_NAME.match(path.stem):
            dated.append(path.stem)
        elif NUMBERED_NAME.match(path.stem):
            numbered.append(path.stem)
        else:
            odd.append(path.stem)
    if not (dated or numbered or odd):
        print("  decisions  none logged yet — /decide writes them")
        return
    print(f"  decisions  {len(dated) + len(numbered) + len(odd)} logged · {len(dated)} dated"
          + (f" · {len(numbered)} still numbered" if numbered else "")
          + (f" · {len(odd)} off-format" if odd else ""))
    if numbered:
        print(f"               numbered names collide between parallel sessions — "
              f"python3 brain/redate.py --apply")
    for stem in odd[:4]:
        print(f"               off-format: {stem} — expected YYYY-MM-DD-slug")


# ── REPORT ── can anything here actually fire at a future time? ────────────────
def report_reminders():
    """Not a failure — a workspace legitimately has no reminder channel. What it must never do
    is *look* like it has one. An assistant that says "I'll remind you" with nothing outside
    the repo behind it has made a promise that breaks weeks later, silently, in the one case
    the owner was relying on it. Printing the route is what keeps that visible."""
    if not REMINDER_ROUTE:
        print("  reminders  no route configured — /remind must say so and hand over the date,\n"
              "             never hold a reminder in a file that fires at nobody")
        return
    where = f" → {REMINDER_TARGET}" if REMINDER_TARGET else " → default target"
    print(f"  reminders  {REMINDER_ROUTE}{where}")
    if not REMINDER_CAN_SCHEDULE:
        print(f"             `{REMINDER_ROUTE}` does not fire on its own — /remind drafts, "
              f"the owner sets it")
    elif REMINDER_ROUTE == "slack":
        print("             scheduled messages reach 120 days out; past that, use a calendar")


def main() -> int:
    quiet = "--quiet" in sys.argv
    print("brain doctor\n")

    check_now_size()
    check_record_projects()
    check_slug_collisions()
    check_feed_item_projects()
    check_tombstones()
    check_stale_citations()
    check_tasks()

    if not quiet:
        print("reports (never fail the run)")
        report_projection()
        report_decision_names()
        report_links()
        report_historical_citations()
        report_duplication()
        report_question_numbers()
        report_tags()
        report_config()
        report_reminders()
        report_glossary()
        report_lenses()
        report_brief()
        report_drafts()
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
