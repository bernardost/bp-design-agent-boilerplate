# `archive/` — retired, kept, not cited

`doctor.py` deliberately does not scan this directory, and nothing in the live brain may
cite anything here.

## What's in it

**`decisions/[[a-design-project-workspace-that-resets-on-clone]]`–`[[lenses-two-critics-and-a-place-to-diverge]]` and `braindumps/2026-08-26`** — the design rationale for the
boilerplate itself: why "decision" replaced "ADR", why every project constant moved into one
config file, why `AGENTS.md` is the charter, why tags are global, why the assistant pushes as
it goes and calls the wrap-up, and why the visual feed is an experiment rather than a rule.

`[[lenses-two-critics-and-a-place-to-diverge]]` is later than the rest and was written straight to this directory: it changes how the
workspace itself works — lenses, the two critics, and a place to diverge — which is
boilerplate rationale, not any project's record. `review-lens.md` sits here too, tombstoned,
as the file `brain/lenses/` replaced.

**`[[the-reply-has-two-zones]]`–`[[everything-for-the-owner-lives-in-the-repo]]`** were written here for the same reason, and they come from one source: the
owner ran the workspace on a real project and sent back what was wrong with it. `[[the-reply-has-two-zones]]` — the
reply has two zones and the owner's half sits in a box, because process narration and things
needing his attention were arriving mixed together. `[[the-brief-is-a-gate-and-evidence-is-cited-quietly]]` — the brief is a gate before the
work starts, and evidence is cited quietly, which is how the absolute rule about labelling
evidence stops destroying the documents it applies to. `[[everything-for-the-owner-lives-in-the-repo]]` — everything for the owner lives
in the repo, prompted by a drafted email saved to a scratch directory he had no way to find.

**`[[close-is-one-command-and-a-few-minutes]]`** is separate: `/close` became one command and a few minutes, with `brain/render.py`
standing in for the four scripts it used to run by hand.

**`[[parallel-sessions-take-worktrees-unprompted]]`–`[[an-async-workshop-replaces-the-call-nobody-attends]]`** came from the same source a fortnight later: the owner ran the workspace on
another project and sent back three things. `[[parallel-sessions-take-worktrees-unprompted]]` — parallel sessions take a git worktree
unprompted, because an agent that stops to ask about the tabs he opened on purpose is a tax on
the way he actually works. `[[focus-mode-is-the-default]]` — focus mode is assumed, so the final message is the only
message, which is decision `[[the-reply-has-two-zones]]` enforced by the harness rather than by style. `[[an-async-workshop-replaces-the-call-nobody-attends]]` — an
async workshop replaces the call nobody attends, and the rule that makes it safe is recording
"chose" separately from "let stand", so a guess of ours never hardens into a client
requirement.

**`[[stop-slop-is-embedded-not-vendored]]`** answers whether to vendor `stop-slop`: no — the rules it adds beyond what the
charter already banned go into `AGENTS.md` itself, where Codex and Cursor can read them, and
the em-dash rule is rejected on the record so nobody strips them later on the charter's
authority.

**`[[projects-are-strands-of-one-engagement]]`** and **`[[decisions-are-dated-not-numbered]]`**
come from running the workspace on a live engagement carrying several strands of work. The
first says one workspace serves one engagement while every record names its project, and that
the separation happens in the projection rather than in the storage. The second replaces the
`NNNN-` decision filename with `YYYY-MM-DD-slug`, because a number claimed from a pool every
parallel session shares collides by construction — and records that the dated name is what
makes `[[parallel-sessions-take-worktrees-unprompted]]`'s "decisions merge clean" true.

They were originally the live record, on the reasoning that the template should dogfood its
own rules and `/setup` would blank the brain on clone. The owner changed that on 2026-08-27:
**the boilerplate ships blank**, so a clone is clean whether or not `/setup` is ever run, and
nobody inherits somebody else's project history. The rationale is preserved here rather than
deleted, because a retired rule is training material.

Read them if you are changing how the workspace itself works. Do not cite them from a live
file. If you want them gone entirely: `rm -rf archive/` — the git history still has them.

`/setup` removes this directory on a fresh clone.
