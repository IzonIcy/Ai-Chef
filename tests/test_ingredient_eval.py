"""Tests for the ingredient eval: label loading and the scoring maths.

The functions come from ``scripts/eval_ingredients.py`` itself, so the numbers
these tests pin are the numbers the eval prints.
"""

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest

import ai_generator

_SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'eval_ingredients.py'
_spec = importlib.util.spec_from_file_location('eval_ingredients', _SCRIPT)
assert _spec is not None and _spec.loader is not None
eval_ingredients = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(eval_ingredients)

HEADER = 'case_id\tdescription\texpected\n'


def _write_cases(tmp_path, *rows):
    path = tmp_path / 'cases.tsv'
    path.write_text(HEADER + ''.join(f'{row}\n' for row in rows), encoding='utf-8')
    return path


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
# score_case — precision, recall and exact set match
# ---------------------------------------------------------------------------


def test_score_case_gives_full_marks_for_a_perfect_match():
    case = eval_ingredients.Case('basics', 'a counter', frozenset({'chicken', 'rice'}))

    score = eval_ingredients.score_case(case, ['rice', 'chicken'])

    assert score.precision == 1.0
    assert score.recall == 1.0
    assert score.exact is True
    assert score.missing == frozenset()
    assert score.extra == frozenset()


def test_score_case_scores_a_partial_overlap_by_set():
    case = eval_ingredients.Case(
        'partial',
        'a counter',
        frozenset({'chicken', 'rice', 'broccoli', 'garlic'}),
    )

    score = eval_ingredients.score_case(case, ['chicken', 'rice', 'tofu'])

    assert score.precision == pytest.approx(2 / 3)
    assert score.recall == pytest.approx(2 / 4)
    assert score.exact is False
    assert score.missing == frozenset({'broccoli', 'garlic'})
    assert score.extra == frozenset({'tofu'})


def test_score_case_counts_an_empty_prediction_as_zero():
    case = eval_ingredients.Case('empty', 'a counter', frozenset({'chicken'}))

    score = eval_ingredients.score_case(case, [])

    assert score.precision == 0.0
    assert score.recall == 0.0
    assert score.exact is False


def test_score_case_folds_case_and_whitespace_on_both_sides():
    case = eval_ingredients.Case(
        'messy',
        'a counter',
        eval_ingredients.parse_expected(' Chicken , RICE '),
    )

    score = eval_ingredients.score_case(case, ['  chicken', 'Rice\t', ' '])

    assert score.exact is True
    assert score.precision == 1.0
    assert score.recall == 1.0


def test_summarise_averages_precision_recall_and_exact_matches():
    perfect = eval_ingredients.Score('a', 1.0, 1.0, True, frozenset(), frozenset())
    half = eval_ingredients.Score('b', 0.5, 0.5, False, frozenset({'rice'}), frozenset())

    precision, recall, exact = eval_ingredients.summarise([perfect, half])

    assert precision == pytest.approx(0.75)
    assert recall == pytest.approx(0.75)
    assert exact == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# load_cases — the labels file
# ---------------------------------------------------------------------------


def test_load_cases_reads_the_repository_labels():
    cases = eval_ingredients.load_cases(eval_ingredients.CASES_PATH)

    assert len(cases) == 20
    assert len({case.case_id for case in cases}) == 20
    assert all(case.expected for case in cases)


def test_load_cases_reads_a_row_into_names(tmp_path):
    path = _write_cases(tmp_path, 'shelf\ta fridge shelf\teggs, Cheese')

    (case,) = eval_ingredients.load_cases(path)

    assert case.case_id == 'shelf'
    assert case.description == 'a fridge shelf'
    assert case.expected == frozenset({'eggs', 'cheese'})


@pytest.mark.parametrize(
    ('rows', 'line', 'message'),
    [
        (('only\ttwo fields',), 2, 'expected 3 tab-separated fields, got 2'),
        (('no-desc\t\trice',), 2, 'description is empty'),
        (('no-names\ta scene\t  ',), 2, 'expected names are empty'),
        (
            ('dup\tscene\trice', 'dup\tother scene\tpasta'),
            3,
            "duplicate case_id 'dup'",
        ),
    ],
)
def test_load_cases_rejects_a_malformed_row(tmp_path, rows, line, message):
    path = _write_cases(tmp_path, *rows)

    with pytest.raises(ValueError) as excinfo:
        eval_ingredients.load_cases(path)

    assert f'{path}:{line}:' in str(excinfo.value)
    assert message in str(excinfo.value)


def test_load_cases_rejects_a_bad_header(tmp_path):
    path = tmp_path / 'cases.tsv'
    path.write_text('id\tdesc\texpected\n', encoding='utf-8')

    with pytest.raises(ValueError, match='header must be case_id, description, expected'):
        eval_ingredients.load_cases(path)


# ---------------------------------------------------------------------------
# the scene path the eval calls
# ---------------------------------------------------------------------------


def test_extract_from_a_scene_sends_the_description_and_no_image(monkeypatch):
    client = _FakeClient('chicken, rice')
    monkeypatch.setattr(ai_generator, '_get_client', lambda: client)

    result = ai_generator.extract_ingredients_from_photo(scene='a counter with chicken and rice')

    assert result == {'ingredients': ['chicken', 'rice']}
    parts = client.calls[0]['messages'][1]['content']
    assert parts[0] == {'type': 'text', 'text': ai_generator.PHOTO_PROMPT}
    assert 'a counter with chicken and rice' in parts[1]['text']
    assert [part['type'] for part in parts] == ['text', 'text']


def test_extract_without_a_photo_or_a_scene_reports_the_missing_input():
    result = ai_generator.extract_ingredients_from_photo()

    assert result == {'error': 'Pass a photo path or a scene description.'}
