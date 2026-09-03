# Sources

*The owner of **what the assistant watches** outside this repo. `/setup` writes it by asking,
then probing what is actually reachable; `/briefing` reads it and writes a dated file in
`brain/briefings/`.*

**Connections are per-person, not per-repo.** This file can name a Slack channel or a Linear
team; it can never carry credentials, and a connector that works on one machine may be absent
on another. So every line carries a state:

- `connected` — reachable from this machine, and confirmed by an actual call
- `wanted` — the source is real and matters, but the connector isn't reachable here

**Format.** One line per source:

```
- `kind` · identifier · state — why it matters
```

`kind` is one of: `slack` · `fathom` · `granola` · `gmail` · `calendar` · `linear` · `notion`
· `figma` · `other`.

**Every line a briefing pulls from a source is attributed** — who said it, where, when, with a
link where one exists. A summary with no attribution is laundering and does not get written.

## The source tag

Attribution is written inline, in any file in the brain, in one form:

```
The client wants SSO before launch. ^[Dana · kickoff call · 2026-08-11 14:20](https://meetings.example.com/r/4821?t=860)
The roster is a version behind. ^[Ravi · #client-portal · 2026-08-28](https://slack.com/…)
Two more workstreams are probably coming. ^[inferred]
```

`who · where · when`, and where a link exists it goes **to the moment** — a recording URL
with its timestamp, a message permalink, the mail thread. A link to the tool's front page is
not attribution.

`feed.py` renders the tag as a faint superscript numeral, hover-revealed and listed at the
foot of the page. That is deliberate: the rule above is non-negotiable, and a page that
prints provenance inside its sentences is a page nobody finishes reading. So the claim stays
clean and the evidence stays reachable.

**`^[inferred]` is required for anything worked out rather than heard**, and it renders as its
own word in ochre rather than a numeral. A guess that reads like a quote is the failure the
whole convention exists to prevent — `doctor.py` counts sections that carry neither.

---

## Watched

*(none yet — `/setup` fills this by asking, then probing what is actually reachable)*

## Wanted, not connected

*(sources worth having when the connector becomes available — this is also the fix-it list)*
