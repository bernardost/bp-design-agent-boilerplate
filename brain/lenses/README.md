# `lenses/` — what "good" means, per domain

*One file per standard the reviewer can be pointed at. `/reviewer <lens> <scope>` picks one.
Written at `/setup`; edit any time the standard moves.*

The `/reviewer` skill holds what never bends — independence, evidence over impression, the
findings format, the severities, the two-round limit, `brain/reviews/` as its only write
location. **This directory holds everything that changes with what is being judged.** The
split is the whole design: improvements to the skill are portable to every clone, and a
project's standard never has to be edited into skill text.

## The lens contract

Every lens file answers four questions, and a lens that skips one is not finished:

1. **What to look at** — the artifacts this lens judges.
2. **What to refuse to look at** — the context that would compromise the judgment. This is
   not the same for every lens, and it is the reason lenses are separate files rather than
   sections of one.
3. **What it is judged on** — numbered, concrete, checkable against the artifact.
4. **What is explicitly not the standard** — so reviews stay useful.

## The lenses that ship

- **`record.md`** — is the project's record honest? Provenance, stage discipline,
  decision-trail consistency, claim-versus-page. Reads widely across the brain. **This is the
  default when `/reviewer` is invoked with no lens named.**
- **`motion.md`** — does the work move the way this project decided? Ships with the rules that
  hold regardless, and two empty sections `/motion` fills with this project's own vocabulary.
- **`house.md`** — does a page generated for the owner look right? Inter, white paper, hairline
  rules, colour only where it carries intent. Governs `feed.html` and its siblings, never the
  project's own work.
- **`deck.md`** — would an agency hand this over? Titles that carry the argument, plain
  English, a held grid, ideas drawn rather than bulleted. Governs what goes **out** — a deck,
  a proposal, a client document — where `craft.md` governs how anything looks.
- **`craft.md`** — is the work any good to look at? Composition, type, colour, motion,
  restraint, AI tells. Sees the rendered artifact and nothing else.

Add your own — `accessibility.md`, `content.md`, `performance.md` — by writing a file that
answers the four questions. Nothing needs to be registered anywhere; `doctor.py` finds them.

## Why two critics and not one

`record` and `craft` disagree about question 2, and irreconcilably. A record review has to
read the decisions, the brief, and the builder's trail to check whether claims match the
page. A craft review has to see **only the artifact**, because knowing what the work was
trying to do is exactly what stops you from noticing it did not do it.

Both are slow, deliberate, owner-invoked passes that write findings. Neither is the fast
screenshot loop during a build — that is `/critique`, which writes nothing and lives outside
this directory on purpose.
