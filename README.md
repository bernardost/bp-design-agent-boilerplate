# agent-workspace-boilerplate

A blank workspace for running a project with a Claude Code (or similar) assistant as a
disciplined collaborator. Clone it at the start of a new engagement; the assistant reads
`CLAUDE.md` as its charter and keeps the record honest from day one.

Extracted from a live client engagement where every rule here was earned by a failure.
The product code, client material, and engagement specifics were stripped; the method —
decision logging, one-screen state, files-as-truth, stage discipline, the self-linting
brain — is the part that carries.

## How to adopt it

1. Clone, then `rm -rf .git && git init` (your project's history starts empty).
2. Open a Claude Code session in the root. The bootstrap block at the top of
   `CLAUDE.md` tells the assistant what to do on the first session: interview you,
   fill the placeholders, write the first `now.md` and ADR 0001, configure
   `doctor.py`/`feed.py`, and delete the block.
3. From then on: start sessions by orienting, end sessions by closing the loop.
   `python3 brain/doctor.py` at both ends.

## What's inside

| Path | What it is |
|---|---|
| `CLAUDE.md` | the assistant's charter — behaviors, invariants, session ritual |
| `brain/now.md` | the one-screen current state; rewritten, never grown (2000-char limit) |
| `brain/plan.md` | the stage arc; each stage's exit bar is an ADR written on entry |
| `brain/tasks.md` | the owner of task state, in a grep-able line grammar |
| `brain/decisions/` | ADRs — every decision reached in conversation gets one |
| `brain/insights/` | durable realizations, one idea per file, `[[wiki-linked]]` |
| `brain/open-questions.md` | questions with owner tags: who can answer |
| `brain/braindumps/` | verbatim dumps; processing routes content out, never rewrites |
| `brain/reviews/` | the independent reviewer's findings and the builder's answers |
| `brain/feed-items.md` | decisions awaiting the owner, rendered into `feed.html` |
| `brain/doctor.py` | lints the brain: hard FAILs for rules with no exceptions, reports for the rest |
| `brain/feed.py` | renders `brain/feed.html` — a self-glossing readout of where things stand |
| `.claude/skills/` | `/braindump` · `/decide` · `/status` · `/reviewer` |

## The ideas underneath

- **One owner per class of information.** Everything else links, never restates.
- **Files are the truth; outward tools are projections.** The tracker and the feed
  page are written outward at session end and never read back as authority.
- **Enforce with a program, not a README.** The rules that survive are the ones
  `doctor.py` refuses to let you past.
- **Stages end by a bar written on entry.** Otherwise every next step is genuinely
  useful and nothing ever ends.
- **Never delete; tombstone.** A superseded file gets a "do not cite" header naming
  its replacement and moves to `archive/`.
