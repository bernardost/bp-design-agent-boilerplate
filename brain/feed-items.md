# Feed items

*The owning file for **decisions awaiting the owner**. `brain/feed.py` renders this plus
`now.md`, `plan.md` and the bar conditions into `brain/feed.html`, which is a **projection** —
written outward, never read back as authority. Answers arrive as a paste-back block from the
page and are recorded here, then routed to their real owners (`decisions/`, `tasks.md`,
`open-questions.md`).*

**Format.** One item per `## FEED-n` block, newest first. The header line is
`## FEED-n · YYYY-MM-DD · status`, where status is `awaiting-you` · `answered` · `withdrawn`.
Then a bold title, then `key: value` lines, then the body.

Keys: `project` (which strand it is about, or `all`) · `owner` · `blocks` (what cannot move
until this is answered) · `cost` (what answering costs) · `options` (pipe-separated buttons;
free text is always available too) · `answered` (the answer and date, once given).

**Every item names its project.** The page renders it as a chip and filters on it. This exists
because two items once reached the owner reading like business from the strand he had open,
and were about another one — he answered the wrong project. Required once the engagement runs
more than one; `doctor.py` enforces it.

**Every item states what it blocks.** A question with no stated consequence is one a busy
person guesses at.

---

## BAR

*The current stage's exit conditions are **read from the decision that owns them** — never retyped
here, so they cannot drift from the decision. What this block adds is the one thing no file can
derive: whether each is met. Refreshed at close-the-loop, alongside `now.md`. Lines look like:*

    1: not-met · evidence or a pointer to it

*With more than one project, each line is prefixed by the project key, because each strand
exits its own bar:*

    portal/1: met · the three screens are in the shared file

---
