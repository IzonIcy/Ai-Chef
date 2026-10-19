"""Untrusted text must not be read as Rich markup, and must not carry escapes.

Recipe fields arrive from model output and from whatever the user types at a
prompt. Rich treats "[" in a string as a tag, so a recipe named
"Pasta [/bold yellow]" raised MarkupError out of display_recipe and took the
menu down with it. Rich also passes raw escape sequences through to the
terminal, where an OSC sequence can retitle the window or rewrite the
clipboard. Both are pinned here.
"""

from io import StringIO

from rich.console import Console

import ai_chef


def _capture(monkeypatch, *, force_terminal=False, highlight=True):
    """Route Rich output to a buffer and return it.

    ``force_terminal`` keeps Rich's own colour codes in the output, which is
    what a real terminal receives. ``highlight`` stays on to match the app's
    own Console; turn it off when a test needs to see a stray escape sequence
    in one piece, because the highlighter's own codes split them up.
    """
    buffer = StringIO()
    monkeypatch.setattr(
        ai_chef,
        'console',
        Console(
            file=buffer,
            width=200,
            no_color=not force_terminal,
            force_terminal=force_terminal,
            highlight=highlight,
        ),
    )
    return buffer


def _recipe(**overrides):
    recipe = {
        'name': 'Test',
        'cook_time': 10,
        'difficulty': 'easy',
        'servings': 2,
        'cuisine': 'Italian',
        'ingredients': ['pasta'],
        'instructions': ['Boil'],
    }
    recipe.update(overrides)
    return recipe


# Rich markup in recipe text


def test_recipe_name_with_a_closing_tag_does_not_crash(monkeypatch):
    buffer = _capture(monkeypatch)

    # Used to raise MarkupError: a closing tag with nothing open to close.
    ai_chef.display_recipe(_recipe(name='Pasta [/bold yellow]'))

    assert '[/bold yellow]' in buffer.getvalue()


def test_recipe_markup_is_shown_literally(monkeypatch):
    buffer = _capture(monkeypatch)

    ai_chef.display_recipe(_recipe(name='[red]Pasta[/red]'))

    # Escaped, so the tags survive as text instead of styling the name.
    assert '[red]Pasta[/red]' in buffer.getvalue()


def test_ingredients_and_instructions_escape_their_markup(monkeypatch):
    buffer = _capture(monkeypatch)

    ai_chef.display_recipe(_recipe(ingredients=['[red]pasta[/red]'], instructions=['[/dim] boil']))

    output = buffer.getvalue()
    assert '[red]pasta[/red]' in output
    assert '[/dim] boil' in output


def test_recipe_metadata_escapes_its_markup(monkeypatch):
    buffer = _capture(monkeypatch)

    ai_chef.display_recipe(_recipe(cuisine='[red]Italian[/red]', cook_time='10 [fast]'))

    output = buffer.getvalue()
    assert '[red]Italian[/red]' in output
    assert '10 [fast] minutes' in output


def test_plan_table_escapes_recipe_names(monkeypatch):
    buffer = _capture(monkeypatch)

    table = ai_chef._render_plan_table(
        {'Monday': {'recipe': 'Pasta [/bold]', 'cook_time': 20, 'servings': 2}}
    )
    ai_chef.console.print(table)

    assert '[/bold]' in buffer.getvalue()


# Terminal escape sequences


def test_escape_sequences_are_stripped_from_untrusted_text():
    hostile = '\x1b]0;retitled\x07 and \x1b[31mred\x1b[0m'

    assert ai_chef._strip_escape_sequences(hostile) == ' and red'


def test_clipboard_osc_sequence_is_stripped():
    assert ai_chef._strip_escape_sequences('\x1b]52;c;aGk=\x07') == ''


def test_newlines_and_tabs_survive():
    assert ai_chef._strip_escape_sequences('line1\nline2\ttabbed') == 'line1\nline2\ttabbed'


def test_escape_sequences_are_stripped_before_markup_is_escaped():
    assert ai_chef._escape_markup('\x1b[31m[red]x[/red]\x1b[0m') == '\\[red]x\\[/red]'


def test_instruction_escapes_are_stripped_not_just_mangled(monkeypatch):
    # Highlighting is off so the payload arrives in one piece. With it on,
    # Rich's own codes happen to split the sequence, which disguises whether
    # we stripped it ourselves or just got lucky.
    buffer = _capture(monkeypatch, force_terminal=True, highlight=False)

    ai_chef.display_recipe(_recipe(instructions=['Boil \x1b[2J water']))

    output = buffer.getvalue()
    assert '\x1b[2J' not in output
    assert 'water' in output


def _ai_menu(monkeypatch, *, ask, tips):
    """Drive the cooking tips menu with the API key faked and the rest patched."""
    monkeypatch.setattr(ai_chef.os, 'getenv', lambda name, default=None: 'test-key')
    monkeypatch.setattr(ai_chef.Prompt, 'ask', lambda *args, **kwargs: ask)
    monkeypatch.setattr(ai_chef, 'get_cooking_tips', lambda *args, **kwargs: tips)


def test_cooking_tips_panel_strips_escapes_from_model_text(monkeypatch):
    # Markdown hands CSI sequences straight to the terminal, so a generated
    # tip could clear the screen or hide text. This is the one path where the
    # passthrough is not broken up by anything else.
    buffer = _capture(monkeypatch, force_terminal=True, highlight=False)
    _ai_menu(monkeypatch, ask='Pasta', tips='Boil \x1b[2J water')

    ai_chef.ai_cooking_tips_menu()

    output = buffer.getvalue()
    assert '\x1b[2J' not in output
    assert 'water' in output


def test_cooking_tips_panel_title_survives_a_hostile_recipe_name(monkeypatch):
    buffer = _capture(monkeypatch)
    _ai_menu(monkeypatch, ask='Pasta [/cyan]', tips='Tip')

    # Used to raise MarkupError out of the Panel title.
    ai_chef.ai_cooking_tips_menu()

    assert 'Tips for Pasta [/cyan]' in buffer.getvalue()
