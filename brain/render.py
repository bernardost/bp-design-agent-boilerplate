#!/usr/bin/env python3
"""render.py — lint the brain and rebuild every projection, in one process.

    python3 brain/render.py

`/close` used to end with a separate command per projection — `doctor.py`, `feed.py`,
`spread.py`, `board.py`, `brief.py`. They cost a fraction of a second of CPU between them;
what they cost was a round trip each at the tail of every session, which is the part a person
actually feels. This runs the same `main()`s in order and prints the same output under
labelled rules.

**It adds no behavior of its own.** Each script stays independently runnable — `/explore`
calls `spread.py` alone, `/brief` calls `brief.py --open` — and this is only the batch that
`/close` needs. Exit code is doctor's: non-zero means a FAIL to fix before committing.
"""

from __future__ import annotations

import sys
from pathlib import Path

BRAIN = Path(__file__).resolve().parent
sys.path.insert(0, str(BRAIN))

import board  # noqa: E402
import brief  # noqa: E402
import doctor  # noqa: E402
import feed  # noqa: E402
import playground  # noqa: E402
import spread  # noqa: E402

STEPS = [("doctor", doctor), ("feed", feed), ("spread", spread),
         ("board", board), ("brief", brief), ("playground", playground)]


def main() -> int:
    status = 0
    argv = sys.argv
    for name, mod in STEPS:
        print(f"\n─── {name} " + "─" * (60 - len(name)))
        sys.argv = [f"{name}.py"]
        try:
            code = mod.main() or 0
        except SystemExit as e:  # argparse --help, or a script that exits early
            code = e.code if isinstance(e.code, int) else 1
        finally:
            sys.argv = argv
        if name == "doctor":
            status = code
    return status


if __name__ == "__main__":
    sys.exit(main())
