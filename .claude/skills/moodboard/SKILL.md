---
name: moodboard
description: Connect the research already in the workspace into ideas, group the ideas into narratives, and render them as a canvas the owner can read at a glance — a vision for the brand, not a specification of it. Use for /moodboard, "put a moodboard together", "what does all this research add up to", or whenever the material has piled up and nobody has said what it means.
---

# Moodboard — connect what we already have

A moodboard documents ideas and articulates them into a vision. Everything it is built from
is already in this workspace: the client's own words, the references, the briefing, the
braindumps, the brief. **The job is connection, not production.** You are not designing
anything here and you are not collecting anything new. You are saying what the material adds
up to, in ideas somebody could argue with.

## Read this first, because it is the failure

**Asked for a moodboard, a model produces a style guide.** Swatches with hex values, a type
scale, three sections named Colour, Typography and Imagery, a rule about the logo. It happens
every time, it is not a lapse in effort, and it is what predicting the likely next token
returns — "moodboard" sits next to a million brand manuals in the training data and next to
almost nothing that reasons.

The artifact it produces is worse than nothing. It specifies a design nobody chose, from
research nobody read, at the stage where the question is still what the work is *about*. It
looks finished, so it ends the conversation it was supposed to start.

**A style guide says what the design is. A moodboard argues what it could mean.** If a
section of your board could be pasted into a brand manual unchanged, it is the failure, and
the fix is not to soften it — it is to delete it and find the idea it was standing in for.

Three tells, and any one of them means start over:

- **Sections named after the toolbox.** Colour / Typography / Imagery / Voice. That is
  organizing by the designer's tools instead of by the argument. A narrative is *"the part
  that has to be trusted with money"*, and the colour, type and imagery all show up inside it.
- **Nothing anyone could disagree with.** *"Clean, modern, trustworthy"* rejects nothing, so
  it proposes nothing.
- **Values instead of intentions.** `#0D0D0E`, `1.25 ratio`, `Inter Medium`. That is the next
  stage's work and it is being done before the direction exists.

## Where this sits

Research → **`/moodboard`** (what does it all mean) → `/explore` (six to eight directions,
seeded, with specimens) → a decision. The board is the layer where thinking happens; the
spread is where alternatives get made; the decision is where one gets chosen. **This command
decides nothing**, and nothing in the brain may cite an idea from it as chosen.

If the owner asks for a moodboard and what they need is directions to choose between, say so
in one line and offer `/explore` instead. The reverse too.

## The run

**1 · Read the desk.** Before writing a word: `context/` (whatever the client sent),
`brain/references/` (the images, including `against/`), the newest `brain/briefings/`, the
`brain/braindumps/`, `brain/project-brief.md`, and `brain/glossary.md` so you decode names
rather than guessing at them. Note what the client said in their own words — those quotes are
plates, and the good ones carry a whole idea by themselves.

If there is almost nothing there, stop and say so. A board built from an empty workspace is a
board built from the model's priors, which is the style guide again wearing a different hat.

**2 · Find the ideas, not the categories.** An idea is a claim about what the work should
*mean* or *do to someone*, specific enough to be wrong. Eight to fourteen of them. Pull them
out of the material: a phrase the client repeated, a tension between two things they said, a
reference that does not fit the others and is more interesting for it.

Each one gets a title and one sentence, and **that pair has to sell it on its own** — the
board is read at a glance first. Write the sentence as the thing you would say out loud, not
as a definition.

**3 · Ground each idea in plates.** A plate is material off the desk: an image that exists in
this workspace, or a verbatim quote with its attribution. Nothing invented, ever — you cannot
describe a photograph nobody has. Caption an image with **what to take from it**, never with
what it is: *"the way the grid breaks on the third column"*, not *"Pentagram poster"*.

An idea with no plate is allowed when the idea genuinely arrived first. Say so rather than
padding it with a plate that does not argue for it.

**4 · Write the detail underneath.** Two or three short paragraphs saying how the idea comes
together across layout, imagery, type, tone of voice and colour — **as intention, not as
specification.** *"Tabular figures everywhere a number appears, and a baseline grid strict
enough that columns line up across cards; type doing the work a border would otherwise do"* is
detail. *"Inter, 16/24, 1.25 scale"* is the next stage.

**5 · Connect them, and this is what makes it a board.** `Connects:` names other ideas by
title. An idea joined to nothing is either the beginning of a second board or it is filler.
Two ideas that pull against each other are the most valuable thing on the page — connect them
and say in the detail that they are in tension, because the tension is what the design has to
resolve.

**6 · Group them into narratives that sell.** Two to four. Each narrative has a name, and one
line saying the story it tells and why it belongs to *this* brand rather than to any brand.
The narratives are the argument; the ideas are its evidence. A narrative that is just a bucket
("Other ideas") means the grouping has not been done.

Then write the `Vision:` line — one paragraph, what all of it adds up to. Write it last, from
what is actually on the board, never first as a thesis the ideas are then bent toward.

**7 · Write the file and render it.** `brain/moodboards/YYYY-MM-DD-<topic>.md` in the shape
`brain/moodboards/README.md` specifies, tagged from `brain/tags.md`, carrying the strand's
`project:` key. Then `python3 brain/board.py` and give the owner the path.

**8 · Take the reaction, in their words.** Ask which ideas they would kill and which one they
would build the whole thing on. Take it verbatim — *"marginalia is too cute next to a
balance"* is usable, *"I don't love it"* is not; push for the specific when what comes back
rejects nothing. Mark the dead ones `Cut:` with the reason, in their words. **Cut ideas stay
on the board.** Re-run `board.py` so the page and the file agree.

## Guardrails

- **No new material.** If the board needs an image nobody has, that is a task and a line in
  `now.md`, not a description of an image you wish existed. Generating one is worse: it puts
  a made-up artefact next to real evidence and they read as equals.
- **Brand assets are never drawn.** The charter's rule is absolute and it applies here even
  though this looks like a sketch. A plate showing the client's mark is their file, extracted
  with `brain/extract.py` or supplied — never redrawn to make the board look complete.
- **One project per board.** The ideas are judged against one strand's brief. A board mixing
  two strands argues for a brand nobody is building.
- **It is not a deliverable for the client** unless the owner says it is. It is a thinking
  artifact for this engagement, and it holds quotes and references that may be confidential.
- **The house style is the page's, not the work's.** `board.py` renders in the workspace's
  own look because the owner is reading it. Nothing on the board prescribes that look for the
  project — see the charter's line on generated artifacts.
- **Do not re-open what is decided.** Check `brain/decisions/` first. A board arguing for
  something already settled is contradiction, and the charter says raise it rather than
  quietly proposing around it.

## Where it goes next

A board that changed what the work is about produces either an exploration (`/explore`, taking
the surviving narratives as its brief) or a decision — and whichever it is links back to the
board file by name. Until one exists, `now.md` says the work is making sense of the research,
and names no direction.
