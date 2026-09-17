# Design skills survey — what to take, and what we already have

*2026-09-17. Read the sources of the design skills installed on this machine and the two
community ones most often recommended, to see what should change about how this workspace
handles the early stages of design. Kept here rather than in `brain/` because it is about the
boilerplate, not about any project run with it. `/setup` deletes `archive/` on a clone.*

The brief was to get closer to Claude Design's output on the work that happens before a build:
exploring several directions, establishing a visual language, validating interaction concepts.

## The finding that reframes the rest

**This workspace is already strong at the two stages everyone recommends buying, and weak at a
third stage nobody in the survey names.**

`/explore` does divergence better than either community skill: it seeds each direction from a
random string so the starting point is derived rather than recalled, it demands six to eight
rather than three, it requires one uncomfortable entry, and it renders them side by side so
taste acts on the work instead of on the prose about it. `frontend-design` asks for a plan and
one direction. `impeccable shape` plans one screen. Neither has anything like the seed.

`/critique` does verification better than the Reddit loop the brief describes: fresh context,
render only, the critic never sees the code or the conversation, scored against `craft.md`,
re-scored in a *new* context each round because a critic that saw its last score defends it.
The brief's "do not let the coding agent evaluate its own UI from source code alone" is a rule
this repo already enforces structurally rather than by asking nicely.

So the plan below is small and specific. Adopting `impeccable` wholesale would replace two good
things with two adequate ones and add twenty-four commands to a workspace with eleven.

**The gap is in the middle.** `/explore` produces *specimens* — fifteen lines of HTML showing a
palette, a type pairing and a layout logic, deliberately not a screen, because building screens
means the best-executed pitch wins instead of the best idea. That rule is right for divergence.
But the next thing that exists is the production build. Nothing sits between an ingredient
swatch and real code, which means **no interaction concept is ever validated, and no full screen
with real content is ever judged before the architecture is committed.** That middle artifact is
exactly what Claude Design produces.

---

## The skills

### `frontend-design` — Anthropic, installed here

A 71-line creative stance, no scripts, no state. Its spine is a calibration list: the five
clusters AI-generated design currently falls into, named concretely enough to check against —
the cream-and-terracotta serif look, the near-black with one acid accent, the broadsheet with
hairline rules, the SaaS card kit, and a set of "template chrome" tells.

**Strength.** The calibration list is the most useful page of design writing in the survey,
because it is falsifiable. It also insists the brief's own words win where the brief pins a
direction down, which stops the anti-default rule becoming its own default. Its writing section
— errors do not apologize, a button that says "Publish" produces a toast that says "Published" —
is better UX-copy guidance than anything in the paid-looking alternatives.

**Weakness.** Biased toward building. Its workflow is plan → review the plan → build, with one
direction throughout; the brief's own suggestion of asking it for three directions first is a
correction, not a feature. It also has no memory between runs and says so, suggesting you keep
notes yourself.

**Verdict: take the calibration list, not the workflow.** Our `/explore` already beats its
process. Its five clusters belong in `craft.md`, which currently lists ten tells that skew
toward decoration and misses every one of frontend-design's five.

**One uncomfortable consequence.** Three of its named tells describe this repo's own house
style for owner-facing pages: the broadsheet with hairline rules and zero border-radius, the
tracked-out all-caps eyebrow label, and meta strings joined with middle dots. `feed.html` is
built from all three. The charter already firewalls this — the house style governs artifacts
for the owner and is explicitly never inherited by the product — so nothing is broken. But the
firewall now matters more than when it was written, and `craft.md` must never absorb the house
style as a standard, or every product gets judged against a look that reads as generated.

### `impeccable` — community, not installed

Twenty-four commands, a shared config, per-route "surface" contracts, and a `PRODUCT.md` /
`DESIGN.md` split. Supports seventeen harnesses including Codex and Cursor from one install.

**Strength, and it is a real one: 61 deterministic detector rules that run with no LLM and no
API key.** Nested cards, weak contrast, cramped spacing, small touch targets, overused fonts,
bounce easing, pure blacks, gray-on-color text. Rules can be suppressed per project, per file,
or inline with a comment carrying a reason. This is `doctor.py` applied to design, and it is
the one idea in the survey this workspace has no equivalent of.

Its `PRODUCT.md` / `DESIGN.md` split is also sound and maps onto what we have: durable product
truth versus tactical visual direction, which is `project-brief.md` versus `lenses/craft.md`.

**Weakness.** Twenty-four commands is a vocabulary to learn, and the adjustment commands
(`bolder`, `quieter`, `distill`, `delight`, `overdrive`) are a worse version of what `/explore`
does properly — they push one design around rather than putting real alternatives beside it.
The install writes six directories and a JSON config into the project, and hooks into the
harness. For a workspace whose claim is that it needs nothing but a text editor and `python3`,
that is a large dependency to take on for one good idea.

**Verdict: do not install. Build the detector ourselves.** The rules are the value and they are
not secret; a hundred lines of Python against our own tell list is a better fit than a Node
toolchain, and it matches the existing shape of the repo exactly.

### `ui-ux-pro-max` — community, not installed

A searchable catalog queried through a Python CLI: 67 UI styles, 161 palettes, 57 font
pairings, 99 UX guidelines, 25 chart types. Generates a first-pass design system from a domain
prompt — "fintech dashboard" returns a coherent style, palette and typography.

**Strength.** Genuine breadth for option generation, and a domain-to-direction mapping that
neither other skill has. It bans Inter, Roboto and system fonts outright as AI-overused.

**Weakness, and it is disqualifying for our early stage.** A catalog encourages style sampling
over product thinking, which is precisely the failure `/explore`'s seed exists to prevent. A
direction picked from a list of 67 is recalled, not derived — the same failure mode as an
unseeded model, with a longer menu. Sixty-one of its "reasoning rules" are unverifiable
marketing counts.

**Verdict: reject for divergence. Possible as a reference shelf**, consulted the way
`brain/references/` is — measured against, never copied toward. Low priority.

### `make-interfaces-feel-better` — installed here

148 lines plus four reference files on typography, surfaces, animations and performance.
Concentric border radius, optical over geometric alignment, layered shadows over borders,
interruptible transitions, staggered enters, tabular numbers, `text-wrap: balance`.

**Strength.** The best detail-scale material in the survey, and specific enough to check:
outer radius = inner radius + padding is a rule with a right answer.

**Weakness.** Entirely late-stage. It has nothing to say about direction, hierarchy or whether
the screen is the right screen. Applied early it produces a beautifully detailed version of the
wrong design.

**Verdict: adopt at the detail scale only.** `craft.md` already judges at two scales and its
"detail" scale is thin — one line about optical alignment and spacing. This is what fills it.

### `design` — the canvas skill, available in this session and unused

Claude Design's canvas, running inside Claude Code. It drafts a multi-artboard visual design as
`.dc.html` artboards laid out on one pan/zoom canvas and publishes it as an artifact; where
saving is enabled the owner then refines elements directly — click to select, properties panel,
inline text editing, undo/redo — and Save publishes a new version.

**This is the missing middle artifact, and it is already installed.** It produces screens on a
canvas rather than ingredients on a page, which is the thing `/explore`'s specimens deliberately
are not and the production build comes too late to be. It is also the literal answer to "get
closer to Claude Design's output", because it is Claude Design.

**Weakness.** It publishes to claude.ai, which puts it squarely under the confidentiality rule —
anything quoting client material needs the owner's say-so first, the same gate `brief.publish`
already governs. It also draws screens rather than running them, so it shows interaction
*concepts* and not interaction *behaviour*; validating that a control feels right still needs
something running.

**Verdict: adopt, as the stage between `/explore` and the build.**

---

## Where the gaps actually are

1. **No prototype stage.** Specimen → production build, with nothing between. The biggest gap,
   and the direct cause of the next two.
2. **No interaction validation.** Nothing in the workspace asks whether a flow works before the
   architecture is committed. `/critique` judges a render; a render cannot be clicked.
3. **No real content.** Nothing says placeholder copy invalidates a hierarchy judgement, though
   it does: lorem text produces even density and hides every overflow the real string causes.
4. **AI tells are LLM-judged only.** `craft.md` lists ten and a model scores them. `doctor.py`
   is this repo's whole argument that a rule which survives is one a program enforces, and the
   craft rules are the ones exempted from it.
5. **`craft.md`'s tell list is out of date and skewed.** Ten entries, mostly decoration. Missing
   all five of frontend-design's current clusters and everything at detail scale.
6. **Nothing holds the chosen visual language after a direction wins.** The decision records
   *which* direction; the palette, type ramp and spacing logic live only inside the exploration
   file and the builder's head, so the build re-derives them and drifts. There is no `DESIGN.md`.
7. **State coverage is mentioned once and enforced nowhere.** `/critique` step 1 asks for empty
   and error states; no lens scores them and nothing fails without them.

## The plan

Ordered by value per unit of work. Each step stands alone — stopping after two leaves the
workspace better, not half-migrated.

**1 · Fill `craft.md`'s tell list, and split it by scale.** Add frontend-design's five
calibration clusters at composition scale and `make-interfaces-feel-better`'s checkable rules at
detail scale. Cost: one file, an hour. This is the highest-value change in the survey because
every `/critique` and every `/reviewer craft` pass reads it, so it compounds across every
project. Guard it with a line saying the house style in `AGENTS.md` is not a standard for
product work — and note that three house-style traits are on the tell list.

**2 · A `DESIGN.md` equivalent, written when a direction is picked.** The convergence seam
currently produces one decision naming the winner. It should also produce
`brain/lenses/visual-language.md`: the palette as named tokens, the type pairing and ramp, the
spacing and radius logic, density, motion principles, and the explicit anti-patterns for *this*
product. `craft.md` judges; this one generates, and the build reads it instead of re-deriving.
Owner: the same decision that closes the exploration.

**3 · `/prototype` — the missing middle.** Between the picked direction and the build: one
disposable screen flow, real content, the states that matter, no component abstraction and no
production architecture. Two routes, chosen by what needs validating. `design` (the canvas) when
the question is composition and visual language, because artboards side by side answer that
fastest and the owner can push pixels himself. A throwaway HTML page when the question is
whether an interaction *feels* right, because that has to run. The rule that makes it work is
that the output is explicitly thrown away — premature component abstraction locking in a weak
design is the failure this prevents.

**4 · `brain/detector.py` — the deterministic tell checker.** `impeccable`'s best idea, built to
our shape. Parse the generated HTML and CSS of a prototype or an artifact and flag what a
program can see without judgement: nested cards, identical radius on everything, a single
shadow value reused, contrast below the floor, touch targets under 44px, line length over 80
characters, banned faces, `cubic-bezier` bounce, pure `#000`. Suppressible per file with an
inline comment carrying a reason, exactly as `doctor.py`'s reports are. It does not replace
`/critique` — it removes the mechanical findings so the expensive critic spends its pass on
composition and taste.

**5 · A content rule, one paragraph in `/prototype` and `craft.md`.** Real strings or no
verdict: the longest realistic name, the empty list, the error, the number with five digits.
Cheapest item here and it prevents a whole class of wrong judgement.

**6 · State coverage in `craft.md` section 3.** Default, empty, loading, error, narrow. A
composition judged only in its happy state has been judged on its easiest frame.

## What not to do

- **Do not install `impeccable`.** Two of its three good ideas we already do better; the third
  is a hundred lines of Python.
- **Do not add a catalog to the divergence step.** `ui-ux-pro-max` and `/explore`'s seed are
  opposed by construction — one recalls, the other derives.
- **Do not run several aesthetic skills as equally authoritative.** They disagree, and a build
  that obeys all of them obeys none. `craft.md` stays the single standard; everything adopted
  here gets folded into it rather than sitting beside it.
- **Do not let the house style leak into product judgement.** It is now on a published list of
  AI tells. It is still right for `feed.html`, which is an internal instrument, and it has never
  been right as a default for client work.
- **Do not systematize before the direction is validated.** Tokens and components extracted from
  an unvalidated design lock in its mistakes and make them expensive to reverse.
