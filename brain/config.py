#!/usr/bin/env python3
"""config.py — read `brain/workspace.toml`, the one place a project constant lives.

    from config import CONFIG, PROJECT_NAME, TRACKER_PREFIX, TASK_LABELS

`doctor.py` and `feed.py` import from here and hold no project constants of their own. That
is the point: the two used to carry a `TRACKER_PREFIX` each, with nothing checking they
agreed, and a prefix that disagrees with itself silently breaks the projection.

`tomllib` is standard library from Python 3.11. A stock macOS `python3` can still be 3.9, and
a linter that crashes on the machine it was cloned onto is worse than no linter, so there is a
fallback parser for the small subset of TOML this file uses: `[table]` headers, `key = "str"`,
`key = true|false`, and `key = ["a", "b"]` on one line. Nothing else — if `workspace.toml`
ever needs more than that, require 3.11 instead of growing this.
"""

from pathlib import Path

BRAIN = Path(__file__).resolve().parent
ROOT = BRAIN.parent
CONFIG_PATH = BRAIN / "workspace.toml"

PLACEHOLDER = "{{"  # an unfilled answer from the setup quiz

DEFAULTS: dict = {
    "project": {"name": "{{PROJECT_NAME}}", "owner": "{{OWNER}}", "work_lives": [],
                "is_template": False},
    "tracker": {"name": "{{TRACKER_NAME}}", "prefix": ""},
    "tasks": {"labels": ["design", "research", "content", "handoff", "method",
                         "blocked-on-external", "bar", "deferred"]},
    "git": {"remote": False, "visibility": "private", "push_each_unit": True},
    "confidential": {"paths": ["context/"]},
}


def _fallback_parse(text: str) -> dict:
    """The subset described in the module docstring. Python < 3.11 only."""
    out: dict = {}
    table = out
    for raw in text.splitlines():
        stripped = raw.strip()
        line = "" if stripped.startswith("#") else raw.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            table = out.setdefault(line[1:-1].strip(), {})
            continue
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip()
        if val.startswith("[") and val.endswith("]"):
            table[key] = [v.strip().strip('"\'') for v in val[1:-1].split(",") if v.strip()]
        elif val in ("true", "false"):
            table[key] = val == "true"
        else:
            table[key] = val.strip('"\'')
    return out


def _merge(base: dict, over: dict) -> dict:
    out = {k: (dict(v) if isinstance(v, dict) else v) for k, v in base.items()}
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k].update(v)
        else:
            out[k] = v
    return out


def load() -> dict:
    """Config merged over the defaults. A missing file is not an error — a fresh clone has
    not run `/setup` yet, and the tools have to work well enough to say so."""
    if not CONFIG_PATH.exists():
        return _merge(DEFAULTS, {})
    text = CONFIG_PATH.read_text(encoding="utf-8")
    try:
        import tomllib
        data = tomllib.loads(text)
    except ImportError:
        data = _fallback_parse(text)
    return _merge(DEFAULTS, data)


def placeholders(cfg: dict | None = None) -> list:
    """`table.key` for every answer `/setup` never filled in. Reported, never fatal —
    a half-configured workspace should announce itself rather than pretend."""
    cfg = cfg or load()
    out = []
    for table, keys in cfg.items():
        if not isinstance(keys, dict):
            continue
        for key, val in keys.items():
            vals = val if isinstance(val, list) else [val]
            if any(isinstance(v, str) and PLACEHOLDER in v for v in vals):
                out.append(f"{table}.{key}")
    return out


CONFIG = load()

PROJECT_NAME = CONFIG["project"]["name"]
OWNER = CONFIG["project"]["owner"]
WORK_LIVES = CONFIG["project"].get("work_lives") or []
IS_TEMPLATE = bool(CONFIG["project"].get("is_template"))
TRACKER_NAME = CONFIG["tracker"]["name"]
# "" in the file means no tracker; None is what the scripts test for.
TRACKER_PREFIX = CONFIG["tracker"]["prefix"] or None
TASK_LABELS = tuple(CONFIG["tasks"]["labels"])
GIT_REMOTE = bool(CONFIG["git"]["remote"])
GIT_VISIBILITY = CONFIG["git"]["visibility"]
PUSH_EACH_UNIT = bool(CONFIG["git"]["push_each_unit"])
CONFIDENTIAL_PATHS = CONFIG["confidential"].get("paths") or []


if __name__ == "__main__":
    import json
    print(json.dumps(CONFIG, indent=2))
    miss = placeholders(CONFIG)
    print("\nunfilled: " + (", ".join(miss) if miss else "none — run /setup to change answers"))
