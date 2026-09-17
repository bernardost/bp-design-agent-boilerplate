# `brand/` — the client's real assets, and nothing that imitates them

**The rule, and it has no exceptions: a brand asset is obtained, never reconstructed.**

Not redrawn, not re-traced, not approximated, not "close enough until they send the real one."
Not the logotype, not the wordmark, not the monogram, not the icon set, not the brand typeface,
not the exact colours eyeballed off a rendered page.

This exists because it happened. An assistant given a client's brand guidelines rebuilt their
logotype by hand instead of taking it out of the PDF or asking for the file. A redrawn mark is
wrong in ways that survive review — the curve is off, the counters are not theirs, the spacing
is a guess — and it is wrong while looking plausible enough to ship. It is also the client's
trademark, which is not ours to redraw.

## Getting the real thing

```
python3 brain/extract.py <the-guidelines.pdf>              # what is in there, and where
python3 brain/extract.py <pdf> --page N --svg              # that page as vector
python3 brain/extract.py <pdf> --images                    # raster images
python3 brain/extract.py <pdf> --spec                      # colours, fonts, the written rules
```

A logo in a brand PDF is nearly always vector, and `--svg` brings out the actual paths rather
than a picture of them. Run `--spec` too, always: clearspace, minimum size and the misuse rules
are the part everyone skims and then violates.

**If it will not come out clean, ask.** Every brand guideline ships with an asset pack, and the
owner can get it in a message. Waiting for a file is a delay; shipping a fake mark is an
incident.

## Every file here declares where it came from

One line at the top of an SVG, or a line in `manifest.md` for a binary:

```
<!-- source: extracted · acme-brand.pdf p.1 · 2026-09-17 -->
<!-- source: supplied · asset pack from the client · 2026-09-17 -->
<!-- source: own-work · mark designed in this engagement · 2026-09-17 -->
```

`own-work` is the one case where drawing is right: a mark **this engagement is designing**.
Reproducing someone's existing mark is never own-work, whatever the tooling.

`doctor.py` fails on a brand mark with no source line. It cannot tell a traced logo from a real
one by looking, so it asks the only question that can be answered honestly.

## Placeholders, while you wait — text, and only text

Work does not stop for a missing asset. It continues with **the client's name set in the
working typeface**, at the right size and in the right position. That is the whole allowance.

Not a traced outline. Not a simplified version. Not a monoline interpretation. And above all
**not the correct structure with invented letterforms** — that is the worst outcome, not a
reasonable compromise. It is what happened: a lockup taken faithfully from the style guide,
with the letterforms guessed because no vector had been extracted. The arrangement was right,
so nothing looked wrong, so it stayed up for eight days on a live site.

Text is obviously provisional. That is the property you are choosing it for.

**And file the swap as a task the same day**, naming who can send the file. A deferred asset
with no owner is a permanent one.

## Confidentiality

This directory holds client material. Add it to `confidential.paths` in `brain/workspace.toml`
before putting anything in it, and never paste its contents into an external service without
the owner's say-so.
