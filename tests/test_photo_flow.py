"""Tests for the local-endpoint settings and the --photo flow.

No test reaches a network. The OpenAI client is either never built or replaced
with a stand-in that records what it was asked for.
"""

import base64
from io import StringIO
from types import SimpleNamespace

import pytest
from rich.console import Console

import ai_chef
import ai_generator
from ai_generator import (
    PHOTO_PROMPT,
    _get_client,
    extract_ingredients_from_photo,
    parse_ingredient_list,
    resolve_settings,
)

_PNG_BYTES = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='
)


@pytest.fixture(autouse=True)
def clean_endpoint_env(monkeypatch):
    """Drop any endpoint settings a .env may have loaded into the process."""
    for name in ('OPENAI_API_KEY', 'OPENAI_BASE_URL', 'OPENAI_MODEL'):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(ai_generator, 'client', None)


def _capture_output(monkeypatch):
    buffer = StringIO()
    monkeypatch.setattr(ai_chef, 'console', Console(file=buffer, width=200, no_color=True))
    return buffer


class _FakeOpenAI:
    """Stand-in for the OpenAI client that records constructor arguments."""

    instances: list[dict] = []

    def __init__(self, **kwargs):
        _FakeOpenAI.instances.append(kwargs)


class _FakeResponse:
    def __init__(self, content):
        self.choices = [SimpleNamespace(message=SimpleNamespace(content=content))]


class _FakeCompletions:
    def __init__(self, reply, calls):
        self.reply = reply
        self.calls = calls

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return _FakeResponse(self.reply)


class _FakeClient:
    def __init__(self, reply):
        self.calls: list[dict] = []
        self.chat = SimpleNamespace(completions=_FakeCompletions(reply, self.calls))


# ---------------------------------------------------------------------------
# resolve_settings — endpoint and model resolution
# ---------------------------------------------------------------------------


def test_resolve_settings_keeps_the_default_endpoint_when_no_base_url():
    settings = resolve_settings(api_key='sk-test')

    assert settings['base_url'] is None
    assert settings['api_key'] == 'sk-test'
    assert settings['model'] == ai_generator.DEFAULT_MODEL


def test_resolve_settings_uses_the_base_url_and_a_placeholder_key():
    settings = resolve_settings(base_url='http://localhost:11434/v1')

    assert settings['base_url'] == 'http://localhost:11434/v1'
    assert settings['api_key'] == 'not-needed'


def test_resolve_settings_prefers_the_model_argument_over_the_default():
    settings = resolve_settings(model='llava')

    assert settings['model'] == 'llava'
    assert resolve_settings(model='')['model'] == ai_generator.DEFAULT_MODEL


def test_resolve_settings_rejects_a_malformed_base_url():
    with pytest.raises(ValueError) as excinfo:
        resolve_settings(base_url='localhost:11434/v1')

    assert 'OPENAI_BASE_URL' in str(excinfo.value)
    assert 'http://localhost:11434/v1' in str(excinfo.value)


def test_get_client_passes_the_base_url_and_model_from_the_environment(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'sk-test')
    monkeypatch.setenv('OPENAI_BASE_URL', 'http://localhost:11434/v1')
    monkeypatch.setenv('OPENAI_MODEL', 'llava')
    monkeypatch.setattr(ai_generator, 'OpenAI', _FakeOpenAI)
    _FakeOpenAI.instances = []

    assert _get_client() is not None

    assert _FakeOpenAI.instances == [
        {'api_key': 'sk-test', 'base_url': 'http://localhost:11434/v1', 'timeout': 60.0}
    ]
    assert ai_generator._get_model() == 'llava'


def test_get_client_keeps_the_default_endpoint_when_no_base_url(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'sk-test')
    monkeypatch.setattr(ai_generator, 'OpenAI', _FakeOpenAI)
    _FakeOpenAI.instances = []

    built_client = _get_client()

    assert built_client is not None
    assert _FakeOpenAI.instances == [{'api_key': 'sk-test', 'timeout': 60.0}]


# ---------------------------------------------------------------------------
# parse_ingredient_list — untrusted model output
# ---------------------------------------------------------------------------


def test_parse_ingredient_list_reads_a_clean_comma_list():
    assert parse_ingredient_list('eggs, milk, Cheddar cheese') == [
        'eggs',
        'milk',
        'cheddar cheese',
    ]


def test_parse_ingredient_list_reads_bullets_and_drops_prose():
    reply = 'Here is what I can see:\n- eggs\n- Cheddar cheese, milk\n* bread\nI hope that helps.'

    assert parse_ingredient_list(reply) == ['eggs', 'cheddar cheese', 'milk', 'bread']


def test_parse_ingredient_list_returns_nothing_for_an_empty_response():
    assert parse_ingredient_list('') == []
    assert parse_ingredient_list('   \n  ') == []
    assert parse_ingredient_list('none') == []


# ---------------------------------------------------------------------------
# extract_ingredients_from_photo — request shape and reply handling
# ---------------------------------------------------------------------------


def test_extract_ingredients_sends_the_image_and_parses_the_reply(tmp_path, monkeypatch):
    image = tmp_path / 'shelf.png'
    image.write_bytes(_PNG_BYTES)
    client = _FakeClient('eggs, milk')
    monkeypatch.setattr(ai_generator, '_get_client', lambda: client)

    result = extract_ingredients_from_photo(image, model='llava')

    assert result == {'ingredients': ['eggs', 'milk']}

    call = client.calls[0]
    assert call['model'] == 'llava'
    parts = call['messages'][1]['content']
    assert parts[0] == {'type': 'text', 'text': PHOTO_PROMPT}
    expected_prefix = 'data:image/png;base64,' + base64.b64encode(_PNG_BYTES).decode('ascii')
    assert parts[1]['image_url']['url'] == expected_prefix


def test_extract_ingredients_reports_an_empty_model_reply(tmp_path, monkeypatch):
    image = tmp_path / 'shelf.jpg'
    image.write_bytes(_PNG_BYTES)
    monkeypatch.setattr(ai_generator, '_get_client', lambda: _FakeClient('   '))

    result = extract_ingredients_from_photo(image)

    assert result['error'] == 'The model returned an empty response.'


def test_extract_ingredients_reports_a_reply_with_no_ingredients(tmp_path, monkeypatch):
    image = tmp_path / 'shelf.jpg'
    image.write_bytes(_PNG_BYTES)
    monkeypatch.setattr(ai_generator, '_get_client', lambda: _FakeClient('The shelf is empty.'))

    result = extract_ingredients_from_photo(image)

    assert 'did not contain any ingredient names' in result['error']


def test_extract_ingredients_rejects_an_unsupported_extension(tmp_path):
    image = tmp_path / 'shelf.heic'
    image.write_bytes(_PNG_BYTES)

    result = extract_ingredients_from_photo(image)

    assert result['error'].startswith("Unsupported image type '.heic'.")


def test_extract_ingredients_reports_a_missing_file(tmp_path):
    missing = tmp_path / 'missing.jpg'

    result = extract_ingredients_from_photo(missing)

    assert result['error'] == f'Could not read {missing}: No such file or directory'


# ---------------------------------------------------------------------------
# --photo without an endpoint — the rest of the app still works
# ---------------------------------------------------------------------------


def test_photo_flow_without_an_endpoint_prints_one_line(tmp_path, monkeypatch):
    image = tmp_path / 'shelf.png'
    image.write_bytes(_PNG_BYTES)
    buffer = _capture_output(monkeypatch)

    exit_code = ai_chef.run_photo_flow(str(image))

    output = buffer.getvalue()
    assert exit_code == 1
    assert 'No AI endpoint set. Set OPENAI_API_KEY or OPENAI_BASE_URL (for Ollama).' in output
    assert 'Traceback' not in output


def test_photo_flow_reports_an_unreadable_path(tmp_path, monkeypatch):
    buffer = _capture_output(monkeypatch)

    exit_code = ai_chef.run_photo_flow(str(tmp_path / 'missing.jpg'))

    output = buffer.getvalue()
    assert exit_code == 1
    assert 'Could not read' in output
    assert 'missing.jpg' in output
    assert 'Traceback' not in output


def test_photo_flow_prints_ingredients_before_the_matches(tmp_path, monkeypatch):
    image = tmp_path / 'shelf.png'
    image.write_bytes(_PNG_BYTES)
    monkeypatch.setattr(
        ai_chef,
        'extract_ingredients_from_photo',
        lambda path, model=None: {'ingredients': ['chicken', 'rice']},
    )
    buffer = _capture_output(monkeypatch)

    exit_code = ai_chef.run_photo_flow(str(image))

    output = buffer.getvalue()
    assert exit_code == 0
    assert 'Ingredients found: chicken, rice' in output
    assert output.index('Ingredients found') < output.index('Found ')
