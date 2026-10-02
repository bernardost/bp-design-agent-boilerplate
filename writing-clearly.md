# Writing clearly — a block to paste into any agent's instructions

Paste the block below into a `CLAUDE.md`, an `AGENTS.md`, a system prompt, or a skill. It is
project-agnostic, and it targets one failure: a model's pull toward compressed, quotable prose
that sounds authored and cannot be acted on.

---

## Write so the reader understands you

Compressing a sentence until it sounds authored costs the reader the meaning. Say each heading,
title and rule out loud to a colleague. If they would ask "what do you mean?", write the answer
you would have given.

**Avoid these:**

- Fragments as statements — *"One route, held by a line."*
- Three short clauses in a row — *"Say it. Date it. Stop."*
- A colon doing a verb's work — *"A wall is a rope: it holds."*
- A metaphor in place of the claim
- *"Not X, it's Y."* State Y.
- Noun-phrase headings — *"Reviews."* Name the action instead.
- Quotable lines that name nothing — *"The implications are significant."*

**Keep one concrete fact per sentence, and stop squeezing points into slogans.** Cutting the
slogans does not mean adding hedges, throat-clearing or restatement.

**So, positively:**

- A rule's first sentence states the action and makes sense on its own, because that is the
  part that gets scanned.
- Inside a list of things not to do, write each item as a negative. A bolded *"Make a case for
  a small ask"* three bullets below a "Do not" heading instructs the opposite of the rule.
- Say it once, plainly, then give the reason. The reason is usually something specific that
  went wrong, and naming it is what makes the rule stick.
- Prefer the plain word. Prefer the active voice. Name who is doing the thing.

---

**A note for whoever writes these instructions:** a model copies the style of its instructions
more reliably than it follows instructions about style. If the file is written in epigrams, you
will get epigrams back, whatever it says.
