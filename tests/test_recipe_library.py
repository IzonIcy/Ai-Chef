"""Integrity checks on the built-in recipe library.

Adding a recipe by hand is easy to get subtly wrong: a missing ``amounts``
entry, a difficulty string that no filter can match, a duplicate name that makes
``get_recipe_by_name`` ambiguous. These run on every commit so the library can't
rot the way the dependency manifests did.
"""

from recipes import RECIPE_DATABASE, all_cuisines, filter_recipes, get_recipe_by_name

REQUIRED_KEYS = {'name', 'ingredients', 'amounts', 'cook_time', 'difficulty', 'cuisine', 'servings'}
VALID_DIFFICULTIES = {'easy', 'medium', 'hard'}


def test_library_is_not_empty():
    assert len(RECIPE_DATABASE) >= 10


def test_every_recipe_has_the_required_keys():
    for recipe in RECIPE_DATABASE:
        missing = REQUIRED_KEYS - set(recipe)
        assert not missing, f'{recipe.get("name")}: missing {sorted(missing)}'


def test_recipe_names_are_unique():
    names = [r['name'] for r in RECIPE_DATABASE]
    duplicates = {n for n in names if names.count(n) > 1}
    assert not duplicates, f'duplicate recipe names: {sorted(duplicates)}'


def test_difficulty_values_are_filterable():
    for recipe in RECIPE_DATABASE:
        assert recipe['difficulty'] in VALID_DIFFICULTIES, recipe['name']


def test_every_recipe_is_reachable_by_difficulty_filter():
    for level in VALID_DIFFICULTIES:
        assert filter_recipes(difficulty=level), f'no recipes with difficulty {level}'


def test_cook_time_and_servings_are_positive_numbers():
    for recipe in RECIPE_DATABASE:
        assert isinstance(recipe['cook_time'], int) and recipe['cook_time'] > 0, recipe['name']
        assert isinstance(recipe['servings'], int) and recipe['servings'] > 0, recipe['name']


def test_ingredients_instructions_and_amounts_are_non_empty():
    for recipe in RECIPE_DATABASE:
        assert recipe['ingredients'], recipe['name']
        assert recipe['instructions'], recipe['name']
        assert recipe['amounts'], recipe['name']


def test_ingredients_are_lowercase_names_without_quantities():
    """Ingredients must stay bare names so matching and grocery grouping work."""
    for recipe in RECIPE_DATABASE:
        for ingredient in recipe['ingredients']:
            assert ingredient == ingredient.lower(), f'{recipe["name"]}: {ingredient}'
            assert not ingredient[0].isdigit(), f'{recipe["name"]}: {ingredient}'


def test_dietary_tags_are_known_values():
    known = {
        'vegan',
        'vegetarian',
        'pescatarian',
        'gluten-free',
        'gluten-free-option',
        'dairy-free',
    }
    for recipe in RECIPE_DATABASE:
        unknown = set(recipe['dietary']) - known
        assert not unknown, f'{recipe["name"]}: unknown dietary tags {sorted(unknown)}'


def test_cuisines_are_title_case_and_discoverable():
    for recipe in RECIPE_DATABASE:
        assert recipe['cuisine'] == recipe['cuisine'].title(), recipe['name']
    assert set(r['cuisine'] for r in RECIPE_DATABASE) == set(all_cuisines())


def test_every_recipe_is_findable_by_name():
    for recipe in RECIPE_DATABASE:
        assert get_recipe_by_name(recipe['name']) is not None, recipe['name']


def test_library_spans_multiple_cuisines():
    assert len(all_cuisines()) >= 5
