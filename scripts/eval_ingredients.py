#!/usr/bin/env python3
"""Score the --photo ingredient path against labelled kitchen scenes.

The --photo path reads a picture, and this repository ships no photo set. Each
case is therefore a written description of a scene standing in for the picture,
plus the ingredient names a person reading that scene would list. Extraction
still runs through the same function --photo uses, so the prompt, the endpoint
and the reply parsing are the ones users get.

With no endpoint configured the script prints one line and exits non-zero.
With ``--dry-run`` it only validates the labels file.

    python scripts/eval_ingredients.py --dry-run
    python scripts/eval_ingredients.py
"""

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path

# Running this file directly puts scripts/ on sys.path, not the repository root,
# so the app modules resolve only when the project has been installed.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import ai_generator  # noqa: E402 - the path fix has to run before this import

CASES_PATH = Path(__file__).resolve().parents[1] / 'eval' / 'ingredient_cases.tsv'
FIELDS = ('case_id', 'description', 'expected')


@dataclass(frozen=True)
class Case:
    """One labelled scene: what is visible, and the bare names it holds."""

    case_id: str
    description: str
    expected: frozenset[str]


@dataclass(frozen=True)
class Score:
    """How one extraction compared with the labels for its case."""

    case_id: str
    precision: float
    recall: float
    exact: bool
    missing: frozenset[str]
    extra: frozenset[str]


def normalise_names(names):
    """Lowercase, collapse inner whitespace and drop blanks.

    The app stores ingredient names as bare lowercase words, so both the labels
    and the model's reply go through this before they are compared.
    """
    normalised = {' '.join(name.split()).lower() for name in names}
    normalised.discard('')
    return frozenset(normalised)


def parse_expected(value):
    """Read the labels column into bare names."""
    return normalise_names(value.split(','))


def load_cases(path):  # noqa: C901 - one pass of row checks, each with its own message
    """Read the labels file, rejecting a malformed row with its line number."""
    try:
        text = Path(path).read_text(encoding='utf-8')
    except OSError as e:
        raise ValueError(f'{path}: {e.strerror or e}') from e

    rows = csv.reader(text.splitlines(), delimiter='\t')
    header = next(rows, None)
    if header is None or tuple(cell.strip().lower() for cell in header) != FIELDS:
        raise ValueError(f'{path}:1: header must be {", ".join(FIELDS)}')

    cases = []
    seen = set()
    for line_number, row in enumerate(rows, start=2):
        if not any(cell.strip() for cell in row):
            continue
        if len(row) != len(FIELDS):
            raise ValueError(
                f'{path}:{line_number}: expected {len(FIELDS)} tab-separated fields, got {len(row)}'
            )
        case_id, description, expected = (cell.strip() for cell in row)
        if not case_id:
            raise ValueError(f'{path}:{line_number}: case_id is empty')
        if case_id in seen:
            raise ValueError(f'{path}:{line_number}: duplicate case_id {case_id!r}')
        if not description:
            raise ValueError(f'{path}:{line_number}: description is empty')
        names = parse_expected(expected)
        if not names:
            raise ValueError(f'{path}:{line_number}: expected names are empty')
        seen.add(case_id)
        cases.append(Case(case_id, description, names))

    if not cases:
        raise ValueError(f'{path}: no cases found')
    return cases


def score_case(case, predicted):
    """Score one case: set overlap for precision and recall, equality for exact.

    Precision is the share of predicted names that are labelled, recall is the
    share of labelled names that were predicted, and exact is true only when the
    two sets are equal. An empty prediction scores zero on both, since an
    extraction that finds nothing has not read the scene.
    """
    predicted = normalise_names(predicted)
    hits = case.expected & predicted
    precision = len(hits) / len(predicted) if predicted else 0.0
    recall = len(hits) / len(case.expected)
    return Score(
        case_id=case.case_id,
        precision=precision,
        recall=recall,
        exact=predicted == case.expected,
        missing=case.expected - predicted,
        extra=predicted - case.expected,
    )


def summarise(scores):
    """Mean precision, mean recall and the share of exact set matches."""
    if not scores:
        return 0.0, 0.0, 0.0
    count = len(scores)
    precision = sum(score.precision for score in scores) / count
    recall = sum(score.recall for score in scores) / count
    exact = sum(1 for score in scores if score.exact) / count
    return precision, recall, exact


def endpoint_problem():
    """Return one line on why no model can be called, or None when one can."""
    try:
        client = ai_generator._get_client()
    except ValueError as e:
        return f'Could not use the configured endpoint: {e}'
    if client is None:
        return ai_generator.NO_ENDPOINT_MESSAGE
    return None


def print_report(scores, model):
    """Print the per-case table, the misses and the overall accuracy."""
    width = max(len(score.case_id) for score in scores)
    print(f'{len(scores)} cases')
    print(f'model {model}')
    print()
    print(f'{"case".ljust(width)}  precision  recall  exact')
    for score in scores:
        exact = 'yes' if score.exact else 'no'
        print(f'{score.case_id.ljust(width)}  {score.precision:9.2f}  {score.recall:6.2f}  {exact}')

    misses = [score for score in scores if not score.exact]
    if misses:
        print()
        print('misses')
        for score in misses:
            missing = ', '.join(sorted(score.missing)) or 'none'
            extra = ', '.join(sorted(score.extra)) or 'none'
            print(f'  {score.case_id}: missing {missing}; extra {extra}')

    precision, recall, exact = summarise(scores)
    matched = sum(1 for score in scores if score.exact)
    print()
    print(
        f'overall precision {precision:.2f}  recall {recall:.2f}  '
        f'exact set match {exact:.2f} ({matched}/{len(scores)})'
    )


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog='eval_ingredients.py',
        description='Score the --photo ingredient path against labelled kitchen scenes.',
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='validate the labels file and report the case count without calling a model',
    )
    parser.add_argument(
        '--model',
        metavar='MODEL',
        help='vision model to use (defaults to OPENAI_MODEL)',
    )
    return parser.parse_args(argv)


def main(argv=None):
    """Run every case and report accuracy. Returns the process exit code."""
    args = parse_args(argv)

    try:
        cases = load_cases(CASES_PATH)
    except ValueError as e:
        print(e)
        return 1

    if args.dry_run:
        print(f'{len(cases)} cases in {CASES_PATH.relative_to(CASES_PATH.parents[1])}')
        return 0

    problem = endpoint_problem()
    if problem:
        print(problem)
        return 1

    scores = []
    errors = 0
    for case in cases:
        result = ai_generator.extract_ingredients_from_photo(
            scene=case.description, model=args.model
        )
        if 'error' in result:
            errors += 1
            print(f'{case.case_id}: {result["error"]}')
            scores.append(score_case(case, []))
            continue
        scores.append(score_case(case, result['ingredients']))

    print_report(scores, args.model or ai_generator._get_model())
    if errors:
        print(f'{errors} case(s) could not be run; the scores above count them as empty.')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
