"""Tests for the TUI menus in ai_chef.py.

The AI-backed menus (custom recipe, cooking tips, substitutions) must not
prompt the user for input when ``OPENAI_API_KEY`` is unset. The generator
functions degrade to a message on their own, but rendering that message into a
Panel looks like a real answer, so the menus bail out before prompting instead.
"""

import ai_chef


def _block_prompts(monkeypatch):
    """Make any interactive prompt a hard failure.

    If a menu prompts while the API key is missing, the test should fail loudly
    rather than hang waiting on stdin.
    """

    def _boom(*args, **kwargs):
        raise AssertionError('menu prompted for input despite missing OPENAI_API_KEY')

    monkeypatch.setattr(ai_chef.Prompt, 'ask', _boom)
    monkeypatch.setattr(ai_chef.Confirm, 'ask', _boom)
    monkeypatch.setattr(ai_chef.os, 'getenv', lambda name, default=None: default)


def _output(monkeypatch, capsys):
    """Route Rich output to a capturable buffer and return the text."""
    from io import StringIO

    from rich.console import Console

    buffer = StringIO()
    monkeypatch.setattr(ai_chef, 'console', Console(file=buffer, width=200, no_color=True))
    return buffer


def test_ai_recipe_menu_returns_early_without_api_key(monkeypatch):
    _block_prompts(monkeypatch)
    buffer = _output(monkeypatch, None)

    ai_chef.ai_recipe_menu()

    assert 'OPENAI_API_KEY not found' in buffer.getvalue()


def test_cooking_tips_menu_returns_early_without_api_key(monkeypatch):
    _block_prompts(monkeypatch)
    buffer = _output(monkeypatch, None)

    ai_chef.ai_cooking_tips_menu()

    out = buffer.getvalue()
    assert 'OPENAI_API_KEY not found' in out
    # The user must not be asked for a recipe name first.
    assert 'Enter recipe name' not in out


def test_substitutions_menu_returns_early_without_api_key(monkeypatch):
    _block_prompts(monkeypatch)
    buffer = _output(monkeypatch, None)

    ai_chef.ingredient_substitutions_menu()

    out = buffer.getvalue()
    assert 'OPENAI_API_KEY not found' in out
    assert 'Enter ingredient to substitute' not in out
