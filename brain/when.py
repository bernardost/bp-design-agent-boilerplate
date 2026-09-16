#!/usr/bin/env python3
"""when.py — turn "next friday 9am" into an exact instant, arithmetic done by a program.

    python3 brain/when.py "next friday 9am"
    python3 brain/when.py "in 3 days" --now 2026-09-16T18:00

    resolved   2026-09-25 09:00  (Friday)
    unix       1790madeup
    in         8 days, 15 hours
    → confirm the weekday with the owner before scheduling anything.

**Why this exists.** An assistant asked to "remind me Friday" computes the date in its head,
and a model doing date arithmetic is exactly as reliable as a person doing it at the end of a
long day. The failure is quiet: the reminder is created, it looks right, and it fires on the
wrong Friday. A reminder nobody can trust is worse than no reminder, because it replaces the
owner's own note.

So the rule is that nothing schedules a reminder from a date the assistant worked out. This
resolves the phrase, prints the weekday back for the owner to recognise, and hands over a Unix
timestamp for whichever channel is actually doing the delivery.

Deliberately small. It understands the phrases people actually say about reminders and says so
plainly when it does not understand one, rather than guessing — a guess here is the whole bug.
"""

from __future__ import annotations

import re
import sys
from datetime import datetime, timedelta

WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
# The default hour for a bare day. Nine in the morning is when a reminder is useful; midnight
# is when it is missed, and "friday" never means 00:00 to the person saying it.
DEFAULT_HOUR = 9


class Unresolved(ValueError):
    """The phrase was not understood. Ask, never guess."""


def _time_of_day(text: str) -> tuple[str, int | None, int]:
    """Pull a clock time out of the phrase, returning the phrase without it."""
    m = re.search(r"\b(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b", text)
    if m:
        hour = int(m.group(1)) % 12 + (12 if m.group(3) == "pm" else 0)
        return text[:m.start()] + text[m.end():], hour, int(m.group(2) or 0)
    m = re.search(r"\b(?:at\s+)?(\d{1,2}):(\d{2})\b", text)
    if m:
        return text[:m.start()] + text[m.end():], int(m.group(1)), int(m.group(2))
    return text, None, 0


def resolve(phrase: str, now: datetime | None = None) -> datetime:
    """A natural phrase → an exact local datetime. Raises `Unresolved` rather than guessing."""
    now = now or datetime.now()
    text = " ".join(phrase.lower().split())
    text, hour, minute = _time_of_day(text)
    text = text.strip(" ,")

    def at(d: datetime, default_hour: int = DEFAULT_HOUR) -> datetime:
        h = default_hour if hour is None else hour
        return d.replace(hour=h, minute=minute, second=0, microsecond=0)

    # An explicit date is the only form with no ambiguity, so it is tried first.
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", text)
    if m:
        return at(datetime(int(m.group(1)), int(m.group(2)), int(m.group(3))))

    if text in ("", "today"):
        return at(now)
    if text == "tomorrow":
        return at(now + timedelta(days=1))
    if text in ("tonight", "this evening"):
        return at(now, 19 if hour is None else hour)

    m = re.fullmatch(r"in (\d+) (minute|hour|day|week|month)s?", text)
    if m:
        n, unit = int(m.group(1)), m.group(2)
        if unit == "minute":
            return (now + timedelta(minutes=n)).replace(second=0, microsecond=0)
        if unit == "hour":
            return (now + timedelta(hours=n)).replace(second=0, microsecond=0)
        days = {"day": 1, "week": 7, "month": 30}[unit] * n
        return at(now + timedelta(days=days))

    # "friday" means the next one, never today — someone saying it on a Friday means the next.
    # "next friday" means the one after that. Both are stated back with the weekday so the
    # owner catches a misread before anything is scheduled.
    m = re.fullmatch(r"(next |this )?(" + "|".join(WEEKDAYS) + r")", text)
    if m:
        target = WEEKDAYS.index(m.group(2))
        ahead = (target - now.weekday()) % 7 or 7
        if (m.group(1) or "").strip() == "next":
            ahead += 7
        return at(now + timedelta(days=ahead))

    raise Unresolved(
        f"cannot resolve {phrase!r}. Ask the owner for a date — a guess here is the bug "
        f"this file exists to prevent.")


def describe(when: datetime, now: datetime | None = None) -> str:
    now = now or datetime.now()
    delta = when - now
    if delta.total_seconds() < 0:
        return "in the past"
    days, rem = delta.days, delta.seconds
    bits = ([f"{days} day{'s' if days != 1 else ''}"] if days else []) + \
           ([f"{rem // 3600} hour{'s' if rem // 3600 != 1 else ''}"] if rem // 3600 else [])
    return ", ".join(bits) or f"{rem // 60} minutes"


def main() -> int:
    argv, args, now = sys.argv[1:], [], None
    i = 0
    while i < len(argv):
        if argv[i] == "--now":
            now = datetime.fromisoformat(argv[i + 1])
            i += 2                      # the flag AND its value; skipping only the flag left
            continue                    # the timestamp in the phrase, which then never parsed
        args.append(argv[i])
        i += 1
    if not args:
        print(__doc__.strip().split("\n\n")[1])
        return 1
    try:
        when = resolve(" ".join(args), now)
    except Unresolved as e:
        print(f"when: {e}")
        return 1
    print(f"  resolved   {when:%Y-%m-%d %H:%M}  ({when:%A})")
    print(f"  unix       {int(when.timestamp())}")
    print(f"  in         {describe(when, now)}")
    print("  → say the weekday back to the owner before scheduling anything.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
