#!/usr/bin/env python3
"""config.py — read `brain/workspace.toml`, the one place a project constant lives.

    from config import CONFIG, ENGAGEMENT_NAME, PROJECT_KEYS, TRACKER_PREFIX, TASK_LABELS

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
    # The engagement: one client, one owner, one meeting stream. `[project]` is the older
    # name for this table and is still read — see `load()`.
    "engagement": {"name": "{{ENGAGEMENT_NAME}}", "owner": "{{OWNER}}", "is_template": False},
    # The strands of work inside it. One key = a single-project workspace, which pays none
    # of the tagging or filtering cost. `all` is reserved for engagement-wide records.
    "projects": {"keys": [], "labels": [], "work_lives": []},
    "tracker": {"name": "{{TRACKER_NAME}}", "prefix": ""},
    "tasks": {"labels": ["design", "research", "content", "handoff", "method",
                         "blocked-on-external", "bar", "deferred"]},
    "git": {"remote": False, "visibility": "private", "push_each_unit": True},
    "generation": {"route": "", "env_file": ".env.agents"},
    # Where a reminder is delivered. "" means none is configured, which the assistant has to
    # say out loud rather than quietly holding the reminder in a file that fires at nobody.
    "reminders": {"route": "", "target": "", "lead_time": "1 day"},
    "brief": {"publish": False},
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
    # `[project]` was this table's name before an engagement could hold several strands.
    # A clone written under the old name keeps working: its keys move to `[engagement]`,
    # and its singular `name` becomes the workspace's one project key.
    legacy = data.pop("project", None)
    if legacy:
        eng = dict(data.get("engagement") or {})
        for key in ("name", "owner", "is_template"):
            if key in legacy and key not in eng:
                eng[key] = legacy[key]
        data["engagement"] = eng
        projects = dict(data.get("projects") or {})
        if not projects.get("keys"):
            projects["keys"] = [_slug(legacy.get("name", ""))]
            projects["labels"] = [legacy.get("name", "")]
        if legacy.get("work_lives") and not projects.get("work_lives"):
            projects["work_lives"] = legacy["work_lives"]
        data["projects"] = projects
    return _merge(DEFAULTS, data)


def _slug(name: str) -> str:
    """A display name reduced to a project key. Only used to migrate an old `[project]`
    table; keys written by `/setup` are chosen by the owner and never derived."""
    out = "".join(c.lower() if c.isalnum() else "-" for c in name).strip("-")
    while "--" in out:
        out = out.replace("--", "-")
    return out or "core"


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

ENGAGEMENT_NAME = CONFIG["engagement"]["name"]
OWNER = CONFIG["engagement"]["owner"]
IS_TEMPLATE = bool(CONFIG["engagement"].get("is_template"))

# The strands. Keys are what records cite; labels are what headings and pages show.
PROJECT_KEYS = tuple(CONFIG["projects"].get("keys") or [])
_labels = list(CONFIG["projects"].get("labels") or [])
# A short `labels` list is not an error — a key with no display name shows as itself.
PROJECT_LABEL = {k: (_labels[i] if i < len(_labels) and _labels[i] else k)
                 for i, k in enumerate(PROJECT_KEYS)}
# `all` is always a valid value on a record: it governs the whole engagement.
PROJECT_VALUES = PROJECT_KEYS + ("all",)
# The one switch every check reads. Below two strands there is nothing to mix up, so the
# tagging and filtering stay invisible; they arrive with the second key and not before.
MULTI_PROJECT = len(PROJECT_KEYS) > 1
WORK_LIVES = CONFIG["projects"].get("work_lives") or []

# Page titles and kickers still want one name. The engagement is that name.
PROJECT_NAME = ENGAGEMENT_NAME
TRACKER_NAME = CONFIG["tracker"]["name"]
# "" in the file means no tracker; None is what the scripts test for.
TRACKER_PREFIX = CONFIG["tracker"]["prefix"] or None
TASK_LABELS = tuple(CONFIG["tasks"]["labels"])
GIT_REMOTE = bool(CONFIG["git"]["remote"])
GIT_VISIBILITY = CONFIG["git"]["visibility"]
PUSH_EACH_UNIT = bool(CONFIG["git"]["push_each_unit"])
CONFIDENTIAL_PATHS = CONFIG["confidential"].get("paths") or []
# Publishing the brief sends what it quotes to an external service. False until the owner says.
BRIEF_PUBLISH = bool(CONFIG["brief"].get("publish"))
# "" means no channel is configured; the scripts and the charter test for None.
REMINDER_ROUTE = CONFIG["reminders"].get("route") or None
REMINDER_TARGET = CONFIG["reminders"].get("target") or ""
REMINDER_LEAD = CONFIG["reminders"].get("lead_time") or "1 day"
# Only these actually fire at a future time. Gmail can draft and send now, never send later.
REMINDER_CAN_SCHEDULE = REMINDER_ROUTE in ("calendar", "slack")

# "" means the project generates no assets; the scripts test for None.
GENERATION_ROUTE = CONFIG["generation"].get("route") or None
GENERATION_ENV_FILE = CONFIG["generation"].get("env_file") or ".env.agents"


if __name__ == "__main__":
    import json
    print(json.dumps(CONFIG, indent=2))
    miss = placeholders(CONFIG)
    print("\nunfilled: " + (", ".join(miss) if miss else "none — run /setup to change answers"))
    print("projects: " + (", ".join(f"{k} ({PROJECT_LABEL[k]})" for k in PROJECT_KEYS)
                          or "none declared — /setup writes them")
          + ("  [multi-project: records carry `project:`]" if MULTI_PROJECT else ""))
