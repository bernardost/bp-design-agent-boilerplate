---
tags: [review, craft, concept, process]
---
# [[lenses-two-critics-and-a-place-to-diverge]] — Lenses, two critics, and a place to diverge
Date: 2026-09-01 · Status: accepted

## Context

The workspace was built entirely for convergence: one owner per class of information, exit
bars, tombstones, and a reviewer that audits the record. Good discipline, and for design work
it left two holes.

**Nothing here ever looked at a picture.** `/reviewer` reviews files. `brain/review-lens.md`
listed accessibility, token consistency, layer hygiene, handoff completeness — all necessary,
none of it able to tell you the work is boring.

**Nothing here generated options.** Every command tightens the record. The stage check, read
plainly, treats going wide as drift, so the first idea anyone had tended to become the idea.

The owner's framing is what shaped the answer: *"maybe we need more facets to this agent — a
set of skills for generating ideas / brainstorming / reviewing visual assets, another set for
QA and other domains."* The first draft of this work put visual critique inside
`.claude/skills/reviewer/SKILL.md`, which is exactly the dilution that question was pointing
at: a taste rubric dragged into every process review and a process rubric into every taste
review.

## Decision

**Roles split by stance; add a second axis for domain, and do not add a fourth role.**
Builder, helper and reviewer stay as they are. What was missing was not another stance.

1. **`brain/review-lens.md` becomes `brain/lenses/`** — one file per standard, each answering
   four questions: what to look at, **what to refuse to look at**, what it is judged on, what
   is explicitly not the standard. `record.md` ships filled (it judges the brain, so it is the
   same on every project) and is the default; `craft.md` ships as a template `/setup` fills.
   `/reviewer` takes the lens as an argument and runs exactly one per pass.

   The reviewer skill gets *smaller*: it keeps only the invariants — independence, the `⚖️`
   tell, evidence over impression, agreement-is-cheap, the findings format, the severities,
   the two-round limit, `brain/reviews/` as its only write location. Adding a domain is now
   adding a file, never editing a skill.

2. **Two critics, because they are different animals.** `/critique` is the fast inner loop
   during a build — fresh context, screenshot only, scores against the craft lens, capped at
   five rounds, **writes nothing to the brain**. `/reviewer craft` is the slow owner-invoked
   pass that writes findings. Merging them would have broken the reviewer's economics: "every
   pass ends with a finding" is right for one deliberate pass and nonsense thirty times an
   hour. They share `brain/lenses/craft.md`, which is what keeps one bar instead of two.

3. **`/explore` and `brain/explorations/`** — the divergent half, and a new owned class.
   Options are neither decisions nor insights: filed in `decisions/` they would log choices
   nobody made. Rejected directions stay. Picking one produces exactly one numbered decision
   that links back, and **that link is the only seam** between the two halves of the brain.

4. **Three narrow charter edits**, and deliberately no more. Going wide inside the current
   stage is not running ahead. The house style governs artifacts made *for the owner to read*
   and is never inherited by the product — otherwise this file's taste silently becomes every
   client's. And `/critique` and `/explore` are the named carve-out from "don't spawn
   subagents unless asked", because invoking them is the ask.

## Consequences

- **Supersedes the split in [[the-reviewers-lens-is-a-project-file]], and keeps its principle.** [[the-reviewers-lens-is-a-project-file]] said invariant belongs in
  the skill and variable in a project file; that was right, and it assumed one variable. The
  line moved: stage discipline and provenance turn out to be *record-lens* content rather than
  skill content, because a craft pass must not read them.
- The reviewer skill is now identical in every clone *and* extensible per project, which [[the-reviewers-lens-is-a-project-file]]
  could only half deliver.
- **New rot to watch, and `doctor.py` reports both:** a `craft.md` never filled in, and an
  exploration whose surviving direction never produced a decision. Neither is a FAIL — an
  unfilled lens is legitimate on a fresh clone, and a FAIL with exceptions trains you to
  ignore the output.
- Cost: one more command to remember, plus an argument on one that existed. Accepted as the
  cheapest shape that does not put a fourth charter in front of the owner.
- **`generation.route` and `.env.agents`** ship alongside, because the craft lens penalizes
  gradients-standing-in-for-art and an agent with no image generator cannot honestly score
  better.
