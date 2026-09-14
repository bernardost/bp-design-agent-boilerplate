---
name: close
description: Wrap up a session so the next one — or the next device — knows exactly what is happening. Routes anything unrecorded to its owning file, rewrites now.md from scratch, lints the brain, regenerates feed.html, commits and pushes, and projects changed tasks to the tracker. Use for /close, "wrap up", "let's stop here", or when you have said it is worth wrapping and the owner agreed.
---

# Close the loop

The anxiety this answers: closing the editor and having the next session not know what is
happening. The files solve it — but only if they are written before the session ends. That is
this, and it is one word so it never gets skipped.

Work in this order. It is a sequence, not a menu.

**It is not eight sessions of work, either.** Push-as-you-go means most of what follows is
already on disk: step 1 catches the remainder, it does not re-derive the session. Steps 1 to 4
write to four different files — read them in one batch, write what each needs, and do not
narrate a step whose answer is "nothing". The whole close is minutes, and a close that takes
longer than the work it is recording is a close that gets skipped.

## 1 · Route what is still only in the conversation

Scan back over the session. Anything decided, realized, asked, or done that exists only in
your replies goes to its owning file now:

- a decision reached → a numbered file in `brain/decisions/`, with frontmatter tags
- a durable realization → `brain/insights/`, linked with `[[wiki-links]]`
- a question raised → `brain/open-questions.md`, with an owner tag: who can answer
- a decision that needs the owner → `brain/feed-items.md`, stating what it blocks
- raw thinking not yet routed → `brain/braindumps/`, verbatim
- a message you wrote for the owner to send → `brain/drafts/`, with `to:` filled in. Never a
  scratch directory: a draft they cannot find is a draft they never send
- directions weighed but not chosen → `brain/explorations/`, with a verdict on each.
  If one was picked, that is a decision above, and it links back to the exploration

If there is nothing, say so. An empty step is fine; a skipped one is not.

## 2 · Update `brain/tasks.md`

Every task that moved gets its status changed. Work you did that was never a task becomes one,
marked `done` — the file is the record, not a to-do list. Check the labels against
`tasks.labels` in `brain/workspace.toml`, and keep the projection pointer honest: `—` means
not yet pushed to the tracker.

## 3 · Rewrite `brain/now.md` from scratch

**Rewrite it. Do not edit it.** Rewriting is the only thing that enforces the one-screen
limit; editing is how it became sixteen kilobytes the last time. Open a blank page and write:
where we are against the current stage's bar, what's next and what unblocks it, what is
blocked and on whom.

The test for every line: *if it would still be true in two weeks, it belongs in its owning
file, linked from here.* Hard limit 2000 characters, and `doctor.py` will fail the run if you
exceed it.

## 4 · Refresh the bar status

If the current stage has a bar, update the `## BAR` block in `brain/feed-items.md`: one line
per condition, `met` / `partly` / `not-met`, each with its evidence or a pointer to it. The
condition *text* is read from the decision that owns it and is never retyped here — only the
judgment of whether it holds.

## 5 · Lint and render

```
python3 brain/render.py
```

That is `doctor.py`, `feed.py`, `spread.py` and `brief.py` in one process — the same four
reports under labelled rules, exiting non-zero on a doctor FAIL. Each still runs alone when
that is what you want (`/explore` calls `spread.py`, `/brief` calls `brief.py --open`); this
is the batch a close needs, as one command rather than four.

Fix every FAIL; read the reports and act on the ones that matter — an unknown tag, a stale
page, an unfilled config answer. Do not report a passing run you did not see.

Two of those reports are about the brief, and both mean the same thing: the owner has not
agreed to something the work is running on. A brief still `draft` after the work has moved,
or sections carrying no source tag, is worth a line in the hand-over rather than a silent pass.

## 6 · Commit and push

If `git.remote` is true in `brain/workspace.toml`, commit and push — one command, not four.
This is already the standing behavior for each unit of work; here it is the backstop, so most
of the time there is little left to send. The message says what moved, not "update files".

## 7 · Project changed tasks to the tracker

If a tracker is configured, push only the `tasks.md` lines that changed, and write the returned
key back into the pointer field — never guess an identifier. Only tasks project: never
decisions, insights, or open questions. A `skip` pointer never goes.

## 8 · Hand over in five lines or fewer

What moved, what is unrecorded and why, the single next action, and anything the owner owes
someone else — **including every draft still waiting to be sent, by name.** Write it for the next session — which may be on a phone, with no memory of this
one.
