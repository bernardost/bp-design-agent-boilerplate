---
tags: [process]
---
# The sentence rules are checked in code, and a session reads less before it writes
Date: 2026-11-11 · Status: accepted

## Context

The owner's two complaints about projects built from this template: the materials agents
write carry Claude's clichés, and as a project grows the agent follows the conversation
instead of its skills and the charter, while the routines (the reply shape, `doctor.py`,
`now.md`) keep working.

Measured across six projects on his disk: "reads as" 140 times in one brain, "lands" 145,
"quietly" 38, "load-bearing" 16 with the word on the charter's banned list the whole time.
The same phrases sat in the template's own text (12, 15 and 9 times), and the charter told
agents to keep em dashes while the owner's global `stop-slop` skill bans them. Nothing
checked a sentence: `doctor.py` had thirty checks and none read prose.

On the second complaint: before any write, a session loaded the charter (25 KB), 36 skill
descriptions (10 KB), then `tasks.md` whole. One project's `tasks.md` was 203 KB and 2,328
lines with no open task in it. `project-brief.md` was read whole at 17 KB. `doctor.py`
printed 118 lines when nothing was wrong. The lens for the deliverable in hand was read only
by `/deck`, `/critique` and `/prototype`.

## Decision

1. **`brain/prose.py`** holds the banned phrases, openers, consulting words and shapes
   ("not X, it's Y", three short sentences, the em dash) as data, and lints markdown and HTML
   with verbatim material, code, italics and task lines removed. `doctor.py` fails a file
   written or changed in the last seven days on a hit and reports the older ones;
   `prose.py --report` prints the table for a whole project. A `PostToolUse` hook,
   `.claude/hooks/lint_prose.py`, runs it on every `.md` or `.html` the assistant writes and
   hands the hits back in the same turn.
2. **The template's own text is clean**, and `test_brain.py` keeps it so. The charter, the
   skills, the lenses and the READMEs were rewritten without the register they taught; the
   em dash rule is now "avoid", matching `stop-slop`.
3. **Every producing skill ends with a Language section** naming the lens to read before
   writing and the lint to run after.
4. **`brain/archive_tasks.py`** moves tasks done for 30 days (dated by `git blame`) to
   `archive/tasks.md`; `/close` runs it; `doctor.py` fails `tasks.md` past 300 lines. The
   orient order reads only the brief's `Status:` line and headings, and `doctor.py` prints
   only the reports that found something (`--all` prints every one).
5. **Less is always on.** Skill descriptions are one sentence each (10 KB to 6.7 KB across
   36 skills). The charter lost its "How this file is written" section (now in `README.md`)
   and the decision format (now in `brain/decisions/README.md`), and shortened its longest
   rules: 25.4 KB to 24.1 KB. The thirteen vendored skills stay as they are: their
   descriptions are already short, and nesting them would break `vendor.py`.

## Consequences

- A project takes all of this with `/update`, except the hook: `.claude/settings.json` is a
  merge file, so the `PostToolUse` entry is ported by hand once.
- An old project will show hundreds of reported hits and fail only on what it writes from
  now on. `prose.py --report` is the number to watch.
- The lint will flag a legitimate sentence now and then. The fix is to rewrite it or to
  narrow the list in `prose.py`, never to skip the check.
- The charter is 24 KB, not the 15 KB first proposed; the rules it still holds were each
  earned by a failure, and none was cut for size alone.
