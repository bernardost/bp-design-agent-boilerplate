---
name: workshop
description: Turn questions for a stakeholder into an async workshop they answer on their phone, in pieces — assumptions they confirm rather than blanks they fill. Use for /workshop, or when a discovery call was missed, a promised document never arrived, a decision-maker will not read a list of questions, or the work is blocked on information only a stakeholder has.
---

# Workshop — when the call does not happen

A client misses the workshop, does not send the document he promised, and will not read an
email with nine questions in it. The work needs his answers anyway. The move is to take the
call apart into screens he can answer alone, on a phone, in pieces, over a day — because every
tap is data and **a half-finished run is still data**, which is more than a cancelled call
gives you.

The method in one sentence, and it is the whole method: **state the assumption, let him
confirm it.** The more we assume and ask him to confirm, the less thought it costs him, and
cost to him is the only variable that decides whether this gets answered at all.

## When this is not the right move

When the question is one the stakeholder has to think out loud to answer. Every screen here
has to be a choice between things we could already draw. If you cannot write a defensible
assumption for a screen, that screen belongs in a conversation, not in a workshop — cut it and
say so.

Also not the move when nobody has read `brain/project-brief.md` and the open questions. A
workshop that asks what the client already told us on a recorded call is how you lose him on
screen two.

## The rules that hold up

1. **Every guessable screen arrives with our answer selected.** The fastest path through the
   whole thing is tapping Next. That is the design, not a shortcut.
2. **`chose` and `let stand` are different records.** Next with nothing touched saves our
   default flagged `let_stand`. In the answers file that is *inferred*, never his words.
   Without the flag, every default he skipped past hardens into a quote.
3. **The chapters you need to start come first.** Order so that stopping after chapter three
   still lets the work move. Never tell him where he may stop — a screen saying "that is
   everything we need" is an invitation to close the tab.
4. **Never ask what has already been heard.** Go through the brief, the briefings and the
   recordings first, and mark what is already known as off-limits.
5. **Some things stay ours.** Anything he has called interchangeable is our call to propose,
   not his to answer. Anything that is really an email stays an email. Taste questions can
   wait for a moment where taste is the subject.
6. **A tick must always add something.** "What should stay unsaid, all pre-ticked" reads as a
   trap. Invert it: "what may this say", nothing ticked. Ticking adds, never removes.
7. **Show, don't ask.** A question the stakeholder has to picture in his head is a question
   he postpones. Draw the thing and let him move, rank, tick or drag. The section below is
   the working part of this rule.
8. **Later screens read earlier answers.** Ask "what should each visitor take away?" using the
   audiences he ranked three screens ago, with a guess per audience. Building on his own
   answers is what makes it a workshop rather than a form.
9. **The container must not vote.** White, one sans, hairlines. It is the brief for work whose
   look is undecided; a mood in the chrome pre-empts the mood question. This is the one place
   the house style in `AGENTS.md` does apply to something a client sees, and for that reason.
10. **One link, one person, no login.** The token in the URL is the identity. A second person
    gets a second link. Nothing to sign up for, nothing to remember.
11. **Save on tap, no submit.** There is no finished state we depend on. Reopening lands on
    the first unanswered screen; the chapter menu is one tap away.
12. **Phone first.** He will open it in a taxi. Every drawing survives 390 pixels or it is not
    in the build.
13. **Never call it a quiz where he can see it.** To him it is the brief, in questions.

## Make it answerable — the visual half

This is where an async workshop is won or lost. The written outline is the content; the
controls are what make answering cost seconds instead of thought. **A screen that could be a
picture and is a paragraph instead is a screen he skips.**

**Match the control to the shape of the answer.** These are the ones that earn their place, and
each came from a board zone that worked in the room first:

| The answer is… | The control | Looks like |
|---|---|---|
| an order of importance | **rank** — drag the cards, cross out the ones that don't apply | audience cards, each with one line explaining who they are |
| a shortlist from many | **pick three** — a grid of stickies, three slots | "what must this do?" with the rest left as nice-to-have |
| a position between two poles | **a 2×2 with a draggable marker**, peers already plotted on it | where the company sits among the people it will be compared to |
| a reaction to alternatives | **tabs of drawn options**, one on screen at a time | three sitemaps as small trees, not three columns of bullets |
| taste | **a wall of real screenshots**, tap what feels right | peer sites and outside references, each with one line of why it is there |
| a word between two words | **a slider**, both ends labelled, seeded where we think it sits | discreet ←→ loud, investor ←→ operator |
| a sequence | **a flow of boxes he can rewrite** | what a visitor lands on, reads, believes, then does |
| a prohibition | **finish-the-sentence cards**, some already filled | "this must never…" with four of ours and a blank |
| a sentence only he has | **one short text field**, and only here | the thesis line, the relationship in his words |

**Seed every control with our guess, visibly.** A slider starts where we think it sits. A rank
starts in an order. Stickies arrive with our words on them, sourced where they came from
something he said. He is correcting, not composing, and correcting is fast.

**Use his words on the cards.** Take the option wording, the brand adjectives and the slider
pairs from the recordings and threads, not from your own vocabulary — and tag them, so he
recognizes his own sentence instead of decoding ours. A guess in our language is a guess he has
to translate before he can agree with it.

**Write it the way you would say it.** Plain, non-technical, one idea per screen. No preamble —
the title and one line of setup, then the control. Never the word "quiz", never our internal
vocabulary (stage, bar, lens, exploration, IA), never a term of art where a plain one exists.
If a screen needs a paragraph to explain what it is asking, the question is wrong, not the
explanation.

**Every drawing is built for 390 pixels.** Trees and 2×2s are SVG on a fixed viewBox, scaled,
with labels flipped where they would run off the edge. Three things side by side become tabs.
A wall of screenshots takes the full width and goes large — a desktop with one small image per
row is a wasted screen.

## The run

**1 · Outline before code.** Write `brain/workshops/YYYY-MM-DD-<topic>-outline.md` in the shape
`brain/workshops/README.md` specifies: chapters, screens, and our assumption on every screen
with its source tag. Then **give the owner the path and let him cut it.** He will remove
screens, collapse a chapter, turn word-pairs into sliders, and rule on whatever you left open.
All of that is free here and expensive later. Do not build until he has cut it.

**2 · One data file is the workshop.** An array of screens — kind, options, default — plus a
`defaultValue()` for the let-stand row and a `summarize()` that renders any answer as one line
for our view. A dozen or so kinds covers everything: text, single, checklist, rank, pick,
sliders, matrix, wall, fields, toggles, sitemap, confirm-or-tick. The code mirrors the outline
and the outline stays the content source.

**3 · One component, one renderer, one table.** A client component holding position, answers, a
save queue and the chapter menu; a renderer that switches on kind; a "say it your way" text
field folded under every screen. Storage is one table keyed `(guest, screen)` with columns for
the value, a note, the `let_stand` flag and a timestamp, upserted through one route that checks
the token against a list of guests in an env var. No UI library, no diagram library — the
drawings are inline SVG.

**4 · Our view is a page.** `/answers?k=<admin>`: every screen, its answer in one line, and a
`chose` / `let stand` / `not reached` tag. That page is the one-page brief we send back, and it
is what you transcribe into `…-answers.md`.

**5 · Walk it headless at phone width. Then the owner runs it on a real phone.** Budget this;
it is not optional. The first run on a real engagement produced seven fixes that a headless
walk had shown as fine: a tick-to-exclude screen that read as a trap, three diagrams side by
side that did not fit, a screen that invited him to stop, optional fields that did not say they
were optional, a wall screen wasting a desktop, a screen ignoring the ranking he had just done,
and an end screen whose big button said "back to the start" so the whole thing read as
unfinished. Revise, then walk it again.

**6 · Wipe before sending, and build the reset button on day one.** The owner's test runs sit
in the same table under the client's name. That first run needed three wipes and had no reset
button. Put one in.

**7 · Send it, then watch.** The covering message is a draft in `brain/drafts/` like any other —
one link, one sentence about what it is, no instructions he has to follow. Then leave it alone.

## When the answers come back

Transcribe to `brain/workshops/YYYY-MM-DD-<topic>-answers.md`, verbatim, `chose` / `let stand`
/ `not reached` on every line. Then route it like a braindump: decisions to
`brain/decisions/`, realizations to `brain/insights/`, what is still open to
`brain/open-questions.md`, and update `brain/project-brief.md` where the workshop moved the
understanding. **Anything resting on a `let stand` says so where it is used.** Commit, push,
and tell the owner what changed and what he still has to chase.

## Cost

Roughly half a day from go to sent, including two revision passes, when the reference images
already exist in `brain/references/`. It is cheaper than rescheduling the call, and unlike the
call it produces a written record with attribution on every line.

## Next time

- The reset button goes in from the start.
- Take word-pairs and option wording from the source material before building, not from your
  own vocabulary — guesses there are guesses the client has to correct.
- Consider a ping to us on each chapter close, so we are not polling to see whether he started.
