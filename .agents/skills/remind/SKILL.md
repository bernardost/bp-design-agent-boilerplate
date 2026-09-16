---
name: remind
description: Put a reminder somewhere that will actually fire — a calendar event or a scheduled message — rather than a note in a repo nobody is watching. Use for /remind, "remind me to…", "don't let me forget…", "chase this on Friday", or whenever the owner hands over something to be surfaced at a future time.
---

# Remind

**The repo cannot remind anyone.** A session runs only while the owner is at the machine,
which is exactly when he does not need reminding. A reminder that lives in `brain/` fires at
nobody, and it fails silently, weeks later, in the one case he was relying on it. So this
command's whole job is getting the alarm *out* of the repo — and saying plainly when it
cannot.

## 1 · Resolve the date with a program, not in your head

```
python3 brain/when.py "<what the owner said>"
```

It prints the date, **the weekday**, a Unix timestamp and how far away it is. Use it every
time, including for phrases that look obvious. A model doing date arithmetic at the end of a
long session is exactly as reliable as a person doing it, and the failure mode is quiet: the
reminder is created, it looks right, and it fires on the wrong Friday.

If it refuses the phrase, **ask**. It refuses precisely so you do not guess.

## 2 · Say the resolved date back before scheduling

One line, with the weekday in it: *"Friday 18 Sep, 09:00 — chase Joe on the org chart."* The
weekday is what makes a misread visible; a bare date does not. Wait for the nod on anything
further out than a few days, or where being wrong would matter.

## 3 · Deliver it through the configured route

Read `reminders.route` in `brain/workspace.toml`.

- **`calendar`** — create an event at the resolved time with a notification on it, on
  `reminders.target` or the default calendar. Best option: it reaches the phone, it survives
  the laptop being shut, and the owner can move it himself.
- **`slack`** — schedule a message to `reminders.target` (a channel id, or his own user id for
  a DM) at the resolved Unix timestamp. **Hard limits: at least 2 minutes out, at most 120
  days.** Past 120 days this route cannot carry it — say so and offer the calendar.
- **`manual`** — do not schedule anything. Draft the reminder into `brain/drafts/` and tell
  him the file and the date, so setting it is one paste.
- **`""` (unset)** — see below.

Never substitute a channel for the configured one without saying so. **Email is not a
reminder route**: Gmail can send now and draft, but it cannot send later, so a "reminder"
mailed today for a date in November is just mail.

## 4 · Write it back into the record

`brain/tasks.md` owns the task; the channel owns the alarm. Same shape as the tracker
projection: the task line carries the work, and the note under it carries **the confirmation
the channel returned** — the event link or the scheduled-message id — plus the resolved date.
A reminder with no confirmation written back is one nobody can verify later, which puts us
back where we started.

In a multi-project engagement the task goes under its project heading like any other.

## 5 · Confirm in one line

What will fire, where, and when — *"Calendar event Friday 18 Sep 09:00, notification 1 day
before."* Then stop.

## When nothing is configured

Say it in one sentence and hand over the date, in the same breath:

> Nothing here can fire on Friday — `reminders.route` is unset. It's **Friday 18 Sep**; want
> it in your calendar, or shall I set that route up now?

Do not create the task and stay quiet about the missing alarm. Do not say "I'll remind you."
An honest refusal costs one sentence. A forgotten commitment costs whatever was forgotten,
and it costs the owner's trust in every reminder after it.

## Setting the route up

Offer this once, when a reminder is asked for and no route exists. `calendar` is the
recommendation because it reaches the phone. It needs the connector authorized — if the
Google Calendar tools are present but unauthorized, the owner runs the authentication once and
it holds after that. Record the answer in `brain/workspace.toml` under `[reminders]`, which is
what stops the question being asked again, and log the choice as a decision.
