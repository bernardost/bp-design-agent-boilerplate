# Review lens

*What "good" means **on this project**. The `/reviewer` skill holds what never bends —
independence, evidence, the findings format, the two-round limit. This file holds the part
that changes from project to project, and the reviewer reads it at the start of every pass.
Written by `/setup`; edit it whenever the standard moves.*

**If this file is empty, the reviewer says so in its verdict** rather than quietly reviewing
against nothing.

---

## What this project is judged on

1. **A fresh clone actually works.** Every claim about the first-run experience is checked by
   running it, not by reading the skill that describes it. A clone is the only real test.
2. **No ceremony without evidence.** A check, a file, or a ritual that has not been shown to
   pay for itself is a finding. This workspace's failure mode is accreting discipline.
3. **The rules the template ships are the rules it obeys.** Any invariant in the charter that
   this repo's own brain violates is a blocking finding — dogfooding is the whole warrant.
4. **Plain language over jargon.** The owner is a designer. Terminology borrowed from software
   practice needs a reason to stay.
5. **Scripts stay dependency-free and version-tolerant.** Standard library only, and no
   Python-version floor that a stock macOS `python3` would trip over.

## What is explicitly not the standard here

- Polish of onboarding copy, before a clone has been run end to end.
- Test coverage as a number. The bar is "the documented path was executed", not a percentage.

*For a design project, this section is usually: accessibility, brand and token consistency,
file hygiene in the design tool, handoff completeness, and whether the artifact matches the
brief. `/setup` rewrites this file from the quiz.*
