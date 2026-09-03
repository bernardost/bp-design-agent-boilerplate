# Drafts

*The owner of **anything written for the owner to send**: an email, a Slack message, a comment
on someone else's ticket. It sits here until it goes out, and it stays here after.*

This folder exists because of one failure. A draft written into a scratch directory — the
agent's own working space, outside the repo, in a path nobody can be expected to remember —
is a draft that never gets sent. **Nothing the owner has to read or act on is ever written
outside this repo.** If it is for them, it lands in the folder that owns it, and you say where
you put it.

Drafts stay after sending, and that is deliberate: what we actually told a client is evidence,
and a claim about it is subject to the same rule as any other — who said it, where, when
(`brain/sources.md`).

## Format

One file per message, named `YYYY-MM-DD-slug.md`:

```markdown
---
to: Dana Okonjo <dana@example.com>
channel: email                 # email | slack | linear | other
subject: Portal estimate — the two files we are still missing
status: draft                  # draft | sent
sent:                          # YYYY-MM-DD, filled when status becomes sent
tags: [portal]
---
Hi Joe,

Quick one before Friday. …
```

- **The body is exactly what gets sent, and nothing else.** No heading, no preamble, no note
  to the owner about the draft — those go in your reply, not in the file. The point is that
  the whole body pastes into Gmail or Slack unedited, which is also what the feed's copy
  button hands over.
- **`subject:` is the display title** for every channel, not just email. For a Slack message
  it is the one line that says what the message is for, so the feed can list it.
- **`to:` is a person, not a placeholder.** A draft addressed to nobody cannot be sent, and
  `doctor.py` reports it.
- Frontmatter tags come from `brain/tags.md`, same vocabulary as everywhere else.

## After it goes out

Set `status: sent` and fill `sent:`. Never delete the file. If the owner edited the message
before sending, **update the body to what was actually sent** — a draft that disagrees with
what the client received is worse than no record, because the next session will quote it.

`brain/feed.html` lists unsent drafts at the top of its own panel, with a button that copies
the body, and keeps the sent ones as a quiet list underneath.
