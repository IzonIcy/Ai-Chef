"""Shared JSON persistence helpers.

Every manager class used to hand-roll the same open/json.load/json.dump
pattern, and writes went straight to the live file — a crash mid-write could
corrupt saved streaks, plans, or recipes. One implementation on purpose:
atomic writes (temp file + os.replace) and consistent error handling live
here now.
"""

import json
import os
from pathlib import Path


def load_json(path: str | Path, default):
    """Load JSON from `path`, returning `default` when missing or corrupt."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default
    except (OSError, json.JSONDecodeError):
        return default


def save_json_atomic(path: str | Path, data) -> None:
    """Write `data` as JSON without ever leaving a truncated file behind.

    The payload lands in a temp file in the same directory and is moved into
    place with os.replace, which is atomic on POSIX and Windows. A crash
    mid-write leaves the previous file intact.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(target.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, target)
