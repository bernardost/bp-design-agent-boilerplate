# Feed items

*The owning file for **decisions awaiting the owner**. `brain/feed.py` renders this plus
`now.md`, `plan.md` and the bar conditions into `brain/feed.html`, which is a **projection** —
written outward, never read back as authority. Answers arrive as a paste-back block from the
page and are recorded here, then routed to their real owners (`decisions/`, `tasks.md`,
`open-questions.md`).*

**Format.** One item per `## FEED-n` block, newest first. The header line is
`## FEED-n · YYYY-MM-DD · status`, where status is `awaiting-you` · `answered` · `withdrawn`.
Then a bold title, then `key: value` lines, then the body.

Keys: `owner` · `blocks` (what cannot move until this is answered) · `cost` (what answering
costs) · `options` (pipe-separated buttons; free text is always available too) · `answered`
(the answer and date, once given).

**Every item states what it blocks.** A question with no stated consequence is one a busy
person guesses at.

---

## BAR

*The current stage's exit conditions are **read from the decision that owns them** — never retyped
here, so they cannot drift from the decision. What this block adds is the one thing no file can
derive: whether each is met. Refreshed at close-the-loop, alongside `now.md`. Lines look like:*

    1: not-met · evidence or a pointer to it

---

1: met · charter, skills, both scripts and README renamed; grep clean outside dated records and quotes
2: met · brain/workspace.toml + brain/config.py; doctor.py and feed.py hold no project constants
3: met · AGENTS.md is the charter, CLAUDE.md is a one-line @import
4: met · frontmatter tags across the brain, brain/tags.md owns the vocabulary, doctor reports them
5: partly · in the charter and followed this session (pushed mid-session, signalled at the seam); one session is not yet a habit
6: met · past items collapse (verified on a fixture), feed.py is inside /close, doctor reports a stale page
7: partly · fresh-clone mechanics verified (skills, gitignore, charter import, both scripts); the /setup interview is untested — see FEED-1

---

## FEED-1 · 2026-08-26 · awaiting-you

**Should a clone's first run be the only way to get a working workspace?**

owner: Bernardo
blocks: the last condition of the stage-one bar — running a real clone end to end
cost: five minutes of reading, or ten if you want to try the clone yourself
options: I'll run the clone test | You run it and report | Skip it for now

`/setup` is written and it is the centerpiece of the first-run experience, but nothing has
executed it on a genuinely fresh clone. Everything else in the stage-one bar is done or
nearly so.

The reason this is a question rather than a task I just do: a real clone test means creating a
throwaway directory, running the interview against invented answers, and deleting it. I can do
that convincingly, but the answers will be mine, not a real project's — so it proves the
mechanics and not the experience. The alternative is that the first real test is your next
actual design project, which is riskier but tells you something a fixture cannot.
