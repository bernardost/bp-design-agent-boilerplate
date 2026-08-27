# `archive/` — retired, kept, not cited

`doctor.py` deliberately does not scan this directory, and nothing in the live brain may
cite anything here.

## What's in it

**`decisions/0001`–`0011` and `braindumps/2026-08-26`** — the design rationale for the
boilerplate itself: why "decision" replaced "ADR", why every project constant moved into one
config file, why `AGENTS.md` is the charter, why tags are global, why the assistant pushes as
it goes and calls the wrap-up, and why the visual feed is an experiment rather than a rule.

They were originally the live record, on the reasoning that the template should dogfood its
own rules and `/setup` would blank the brain on clone. The owner changed that on 2026-08-27:
**the boilerplate ships blank**, so a clone is clean whether or not `/setup` is ever run, and
nobody inherits somebody else's project history. The rationale is preserved here rather than
deleted, because a retired rule is training material.

Read them if you are changing how the workspace itself works. Do not cite them from a live
file. If you want them gone entirely: `rm -rf archive/` — the git history still has them.

`/setup` removes this directory on a fresh clone.
