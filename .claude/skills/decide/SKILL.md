---
name: decide
description: Deliberately capture a decision as an ADR in brain/decisions/. Use when the user says /decide, "let's log this decision", or wants to make and record a choice.
---

# Decide

1. Take the topic from the arguments; if unclear, ask what's being decided.
2. Short interview — only what's missing, one question at a time:
   - What forced the choice? (context)
   - What was decided, and what alternatives were rejected?
   - What follows from it? (consequences)
3. Check `brain/decisions/` for conflicts or a decision this supersedes; if
   superseding, mark the old one `Status: superseded by NNNN` and tombstone it.
4. Write `brain/decisions/NNNN-short-title.md` in the standard format
   (see CLAUDE.md), with `[[links]]` to related insights and decisions.
5. If the decision changes current work, update `brain/now.md`.
6. Confirm with the path and a one-line restatement of the decision.
