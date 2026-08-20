"""Shared fixtures for AI Chef tests.

meal_planner.py and gamification.py both key state off
``datetime.now(timezone.utc)``. To keep tests deterministic we patch each
module's ``datetime`` name with a :class:`Clock` whose "now" is a fixed
timestamp that tests can advance explicitly.
"""

import datetime as _real_datetime
from datetime import datetime, timedelta, timezone

import pytest

import gamification
import meal_planner

# A fixed Monday; avoids weekend/midnight edge cases and keeps week_start
# calculations stable.
_DEFAULT_START = datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc)


class Clock:
    """Stand-in for a ``datetime`` module with a controllable ``now()``."""

    def __init__(self, start=None):
        self.current = start if start is not None else _DEFAULT_START

    def now(self, tz=None):
        return self.current

    def advance(self, *, days=0, hours=0):
        self.current = self.current + timedelta(days=days, hours=hours)

    def strptime(self, date_string, fmt):
        # Deliberate passthrough to the real datetime for expiry parsing
        return _real_datetime.datetime.strptime(date_string, fmt)  # noqa: DTZ007

    def fromisoformat(self, date_string):
        return _real_datetime.datetime.fromisoformat(date_string)

    def today_str(self):
        return self.current.strftime("%Y-%m-%d")

    def week_start_str(self):
        today = self.current.date()
        week_start = today - timedelta(days=today.weekday())
        return week_start.isoformat()


@pytest.fixture
def clock(monkeypatch):
    """Freeze datetime for meal_planner and gamification at a fixed Monday."""
    frozen = Clock()
    monkeypatch.setattr(meal_planner, "datetime", frozen)
    monkeypatch.setattr(gamification, "datetime", frozen)
    return frozen
