---
tags: [craft, process, system]
---
# A brand asset is obtained, never reconstructed
Date: 2026-09-17 · Status: accepted

## Context

On a live client project, an assistant given the client's brand guidelines **rebuilt their
logotype by hand** — three monoline SVG strokes standing in for a J, an A and a G — and it
shipped to a portal, where it stayed.

> *"For some reason, the agent decided to reconstruct their logotype, instead of somehow
> pulling it from the PDF or asking me for the appropriate file. This should never, ever
> happen."* ^[owner · session · 2026-09-17]

The detail that matters is **how close it was**. The lockup came faithfully off pages 4–5 of
the style guide the client had sent: side bar, name over CONSULTING, crossbar-less A. Only the
letterforms were invented, because no vector had been extracted. The real mark has modulated
strokes, a wedge-legged A, an angled terminal on the J, and a G whose bar meets the right side
low around a rectangular counter; the drawing had a circle with a gap.

**So everything a reviewer checks at a glance was correct.** That is what makes a structurally
faithful redraw the worst outcome rather than an honest middle ground — a crude fake gets
caught, and this one survived eight days on a live site. It is also the client's trademark.

The owner named the correct fallback himself:

> *"I thought we could extract the asset from the PDF. If we can't we shouldn't have tried to
> draw the logo. We should have added a text-only version."* ^[owner · session · 2026-09-17]

Extraction was in fact available the whole time. A logo in a brand PDF is nearly always vector,
and `pdftocairo -svg` brings out the real paths. The redraw ran on the excuse that extracting
felt hard and drawing felt easy.

**A second, separate failure sits underneath it.** The decision that recorded the drawing said
*"the wordmark is drawn, not set… one swap when they send a vector."* That decision carried
three future-tense clauses; two were routed to a task and a question the same day, and the
third became nothing — no task, no owner, no line in `now.md`. A promise with no owner is not a
deferral, it is a permanent state of affairs.

## Decision

1. **A brand asset is obtained, never reconstructed — no exceptions.** Not the logotype,
   wordmark, monogram, icon set or typeface. Not in SVG, CSS or code. Not "close enough until
   the real file arrives". Brand colours are read from the guidelines, never eyeballed off a
   rendered page.
2. **The order is extract, ask, text.** `brain/extract.py` makes the first step one command:
   inventory a guideline, pull a page out as real vector with `--page N --svg`, pull rasters,
   and write out the colours, fonts and the clearspace and misuse rules with `--spec`. If it
   will not come out clean, ask for the asset pack — every brand guideline ships with one.
3. **The fallback is text, and only text.** The client's name set in the working typeface, at
   the right size and position. Not a traced outline, not a simplified version, not a monoline
   interpretation, and above all **not the right structure with invented letterforms**. Text is
   obviously provisional, which is the property being chosen.
4. **Real assets live in `brain/brand/`, each declaring `source: extracted | supplied |
   own-work`.** Nothing can detect a trace by inspection, so the enforceable thing is the
   declaration; `doctor.py` fails a mark that declares none. `own-work` covers the one case
   where drawing is the job — a mark this engagement is itself designing. Reproducing an
   existing mark is never own-work.
5. **Every future-tense clause in a decision gets routed before the decision is closed.**
   `/decide` now requires it and says which clauses went where. `doctor.py` reports decisions
   that defer something and are cited by no task or question — a REPORT, because detecting a
   promise by its wording is a guess, and a guess that blocks the run gets ignored.
6. **`brain/brand/` is confidential by default**, added to `confidential.paths`.

## Consequences

- The right path is now cheaper than the wrong one, which is the only way a rule like this
  holds. Redrawing was never a decision anybody made; it was what happened when extraction
  looked like work.
- `craft.md` scores brand infidelity as an incident and caps the score at 3, ahead of
  everything else it judges. Getting the mark right is the floor a studio is hired for.
- Six tests cover it, including that a file which only *calls itself* a wordmark in its markup
  is caught, and that a plain asset is not.
- The cost is a declaration line on every brand file. It is paid by whoever adds the file, at
  the moment they know the answer.
- This does not retrieve the eight days. The live project still needs its swap, and the real
  file brings its own problems — it is the mark alone without the bar or the second word, it
  hard-codes a white fill against a light theme, and its artwork fills 73% of the viewBox, so
  dropped in at 30px it renders small and sits high. "Swap it later" is never as cheap as it
  sounds, which is the argument for not drawing it in the first place.
