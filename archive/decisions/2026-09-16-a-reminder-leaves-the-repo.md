---
tags: [process, system]
---
# A reminder leaves the repo, or it is not a reminder
Date: 2026-09-16 · Status: accepted

## Context

The owner asked what happens when he says *"remind me of X"*:

> *"Not sure I can trust the actual agent to remind me of something. Ideally, reminders are
> actual reminders in google calendar or the user's preferred channel. Sometimes agents get
> dates confused, and also I might not have my laptop on when a reminder is due."*
> ^[owner · session · 2026-09-16]

Both halves are right, and they fail differently.

**The repo cannot fire.** A session runs only while the owner is at the machine, which is
exactly when he does not need reminding. Every mechanism available to an agent here — a task
line, a scheduled wakeup, a cron in the session — dies with the session or needs the laptop
open. So *"I'll remind you"* is a promise that breaks quietly, weeks later, in the one case he
was relying on it. Worse than not writing it down: it stops him writing it down himself.

**The date is the second failure, and the more insidious one.** A model computing "Friday"
from today's date at the end of a long session is exactly as reliable as a person doing it,
and being wrong is invisible — the reminder gets created, it looks right, and it fires on the
wrong Friday. A reminder nobody can trust is worse than none for the same reason: it has
already replaced the owner's own note by the time it is wrong.

## Decision

**A reminder is a projection, like the tracker. `tasks.md` holds the truth; a channel outside
this repo holds the alarm. If no channel holds it, there is no reminder and the assistant says
so.**

1. **`brain/when.py` resolves the date, never the model.** It takes the phrase, prints the
   resolved instant, **the weekday**, a Unix timestamp and the distance — and **refuses
   phrases it does not understand** rather than guessing, because the guess is the bug. The
   assistant says the date and weekday back before anything is scheduled: a bare date hides a
   misread, a weekday does not.
2. **`reminders.route` in `brain/workspace.toml` says where it fires.** `calendar` is the
   recommendation, because it reaches the phone and survives the laptop being shut. `slack`
   genuinely schedules but reaches only 120 days out. `manual` drafts and lets the owner set
   it. **Email is deliberately not a route**: Gmail can send now and draft, but it cannot send
   later, so a mail sent today for a date in November is not a reminder.
3. **With no route, say it in one line and hand over the date.** Never create the task and
   stay quiet about the missing alarm. An honest refusal costs one sentence; a forgotten
   commitment costs whatever was forgotten, and then it costs the credibility of every
   reminder after it.
4. **The confirmation the channel returns is written back** into the task's note — the event
   link, the scheduled-message id. Without it nobody can check later that the alarm exists,
   which is the state this decision exists to leave behind.
5. **`/remind` is the command**, and `doctor.py` prints the configured route on every run so a
   workspace that cannot fire announces it rather than looking equipped.

## Consequences

- The owner can tell, from one line of `doctor.py`, whether this workspace can remind him.
- `when.py` is small and refuses more than it resolves. That is the correct bias here: an
  unresolved phrase costs one question, a mis-resolved one costs the reminder.
- Calendar needs its connector authorized once. Until then the honest answer is the one-liner,
  not a silent fallback to a channel the owner did not choose.
- This is the second rule of its shape, and they point in opposite directions on purpose:
  [[everything-for-the-owner-lives-in-the-repo]] says a drafted message belongs in the tree
  where he can find it, and this says an alarm belongs outside it where it can actually go
  off. The test is the same both times — *could he act on it without being told where to look?*
