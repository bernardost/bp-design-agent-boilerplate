---
name: decide
description: Deliberately capture a decision in brain/decisions/. Use when the user says /decide, "let's log this decision", or wants to make and record a choice.
---

# Decide

1. Take the topic from the arguments; if unclear, ask what's being decided.
   **Know which project it belongs to.** With more than one key in `[projects]`
   (`brain/workspace.toml`), that is part of what is being decided — if the conversation
   has not settled it, ask in one line. `all` is for a decision that binds every strand,
   not for one you are unsure about.
2. Short interview — only what's missing, one question at a time:
   - What forced the choice? (context)
   - What was decided, and what alternatives were rejected?
   - What follows from it? (consequences)
3. Check `brain/decisions/` for conflicts or a decision this supersedes; if
   superseding, mark the old one `Status: superseded by [[slug]]` and tombstone it.
4. Write `brain/decisions/YYYY-MM-DD-short-title.md` in the standard format (see
   `AGENTS.md`) — today's date, then a slug nothing else in the folder uses. Frontmatter
   carries tags from `brain/tags.md` and, in a multi-project engagement, `project:`.
   Link out with `[[slug]]` wiki-links to related insights and decisions.
   **Never number the file.** A number is claimed from a pool every parallel session
   shares, which is what the date replaced.
5. If the decision changes current work, update that project's section of `brain/now.md`.
6. Commit and push — a logged decision is a completed unit of work.
7. Confirm with the path and a one-line restatement of the decision, naming the project
   it lands under when the engagement has more than one.
