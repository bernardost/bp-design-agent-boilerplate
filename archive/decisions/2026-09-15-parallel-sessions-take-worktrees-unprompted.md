---
tags: [process]
---
# [[parallel-sessions-take-worktrees-unprompted]] — Parallel sessions take worktrees, unprompted
Date: 2026-09-15 · Status: accepted

## Context

The owner runs several sessions at once, in separate tabs, on a real project. That is a
deliberate choice and not the same thing as one agent spawning subagents:

> *"I often open up a couple of tabs and have agents do things in parallel. I prefer this way
> rather than asking one agent to spawn a different one, it's essentially two separate
> conversations anyway."* ^[owner · session · 2026-09-15]

What happened instead was a quiz. A session would notice another agent working, stop, describe
the situation, offer options, and wait for the owner to explain an arrangement he had set up on
purpose. The charter already said not to make a case for a small ask; this was worse than a
case, because it also blocked.

## Decision

A session that sees any sign of a second one in this repo **creates a worktree and says one
line about it.** No question, no menu. The signs are cheap and concrete: `git worktree list`
showing more than one, a dirty tree the session did not dirty, a branch or commit that appeared
mid-session, another local agent session, or the owner saying so. With no sign at all, the
worktree is still *offered* in one sentence when the task is one the owner might plausibly run
alongside something else — ignorable, never a question.

Worktrees go to `../<repo>-wt/<slug>` on their own branch, outside the repo so nothing in the
brain scans them, removed once the branch lands. In Claude Code `EnterWorktree` does the same
thing and is used instead of the raw git command.

The rule carries one carve-out that makes it safe: **the current-state files stay with the
merging session.** `now.md`, `tasks.md` and `feed-items.md` are rewritten whole by every
session that closes, so two sessions touching them conflict every time. Decisions, insights,
explorations and drafts are new files per unit of work; they merge clean and get written as
usual from inside a worktree.

## Consequences

- The owner never again explains his own parallelism to an agent.
- `git.push_each_unit` still holds inside a worktree — the branch is pushed, not main.
- The `/close` ritual is now unambiguous about who owns the current-state rewrite when more
  than one session is live, which it was not before.
- A session that guesses wrong and takes a worktree nobody needed costs one branch and one
  line of text. That asymmetry is why the default is act-then-say rather than ask.
- **Numbered files collide, and the worktree does not prevent it.** Writing this decision hit
  exactly that: another session had already pushed its own `[[close-is-one-command-and-a-few-minutes]]`, so three files had to be
  renumbered on the rebase. Nothing detects it in advance, because the number a session picks
  depends on a commit it has not fetched. Two habits contain it — `git pull` before touching
  anything, which the charter's orient step already requires and which this session skipped,
  and renumbering on the rebase rather than forcing. Filenames are cheap to change while
  nothing cites them; the fix is to renumber before anything links to the number.

---

*Added 2026-09-15, after the fact: the consequence above treated the numbering collision as a
discipline problem and prescribed pulling first and renumbering on the rebase. That was the
wrong fix for the right observation. `[[decisions-are-dated-not-numbered]]` supersedes it —
dated filenames remove the shared pool, which is what makes this decision's "decisions merge
clean" claim true rather than aspirational. The rest of this decision stands.*
