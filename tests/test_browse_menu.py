"""Tests for the browse/search menu in ai_chef.py.

``browse_all_recipes`` now takes a free-text query before the structured
filters, so the two compose: a search narrows the pool and the cook time,
difficulty, dietary, and cuisine prompts narrow it further. These tests drive
the menu with scripted answers rather than testing the filter layer again.
"""

from io import StringIO

import pytest
from rich.console import Console

import ai_chef


@pytest.fixture
def console_capture(monkeypatch):
    buffer = StringIO()
    monkeypatch.setattr(ai_chef, 'console', Console(file=buffer, width=250, no_color=True))
    return buffer


def _answers(monkeypatch, *responses):
    """Script Prompt.ask to return ``responses`` in order, '' when exhausted."""
    queue = list(responses)
    monkeypatch.setattr(ai_chef.Prompt, 'ask', lambda *a, **k: queue.pop(0) if queue else '')
    monkeypatch.setattr(ai_chef.Confirm, 'ask', lambda *a, **k: False)


def test_search_query_narrows_results(monkeypatch, console_capture):
    _answers(monkeypatch, 'stir-fry', '', '', '', '')  # query, then four filters

    ai_chef.browse_all_recipes()

    out = console_capture.getvalue()
    assert 'Chicken Stir-Fry with Broccoli' in out
    # Other recipes are filtered out by the search.
    assert 'Beef Tacos' not in out


def test_unmatched_search_reports_and_returns(monkeypatch, console_capture):
    _answers(monkeypatch, 'zzzznotarecipe')

    ai_chef.browse_all_recipes()

    assert 'Nothing matches' in console_capture.getvalue()


def test_empty_query_browses_everything_and_lists_cuisines(monkeypatch, console_capture):
    _answers(monkeypatch, '', '', '', '', '')

    ai_chef.browse_all_recipes()

    out = console_capture.getvalue()
    assert 'Cuisines available:' in out
    assert 'Beef Tacos' in out
    assert 'Chicken Stir-Fry with Broccoli' in out


def test_search_results_can_be_narrowed_by_cuisine(monkeypatch, console_capture):
    # "chicken" finds three recipes across Asian and American; an Italian
    # cuisine filter must remove all of them.
    _answers(monkeypatch, 'chicken', '', '', '', 'Italian')

    ai_chef.browse_all_recipes()

    assert 'No recipes match your filters' in console_capture.getvalue()


def test_search_and_cuisine_that_agree_keep_the_recipe(monkeypatch, console_capture):
    _answers(monkeypatch, 'shrimp', '', '', '', 'Italian')

    ai_chef.browse_all_recipes()

    out = console_capture.getvalue()
    assert 'Shrimp Scampi' in out
    assert 'Found 1 recipes' in out


def test_filters_apply_on_top_of_search(monkeypatch, console_capture):
    # "chicken" finds 3 chicken recipes; a 20 minute cap keeps only the stir-fry.
    _answers(monkeypatch, 'chicken', '20', '', '', '')

    ai_chef.browse_all_recipes()

    out = console_capture.getvalue()
    assert 'Chicken Stir-Fry with Broccoli' in out
    assert 'One-Pan Chicken Broccoli Rice' not in out
