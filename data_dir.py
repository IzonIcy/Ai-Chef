"""Central location for user data files.

Every JSON file the app persists lives in one directory instead of being
scattered across whatever directory the user happened to launch from.

Resolution order:
1. ``AI_CHEF_DATA_DIR`` env var (useful for tests and portable installs)
2. ``$XDG_DATA_HOME/ai-chef`` when XDG_DATA_HOME is set
3. ``~/.local/share/ai-chef``
"""

import os
from pathlib import Path


def get_data_dir() -> Path:
    """Return the user data directory, creating it if needed."""
    override = os.getenv("AI_CHEF_DATA_DIR")
    if override:
        base = Path(override)
    else:
        xdg = os.getenv("XDG_DATA_HOME")
        if xdg:
            base = Path(xdg) / "ai-chef"
        else:
            base = Path.home() / ".local" / "share" / "ai-chef"
    base.mkdir(parents=True, exist_ok=True)
    return base
