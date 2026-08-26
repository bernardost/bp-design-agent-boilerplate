# `decisions/` — the ADR log

One file per decision, `NNNN-lowercase-kebab-title.md`, numbered in order. A decision stated
or reached in conversation gets logged here unprompted — that is the assistant's job, not a
favor. Superseded ADRs get their `Status:` line changed to `superseded by NNNN`, plus a "do not cite" tombstone header,
and stay put (doctor.py checks both). Copy `0000-adr-template.md` to start one.
