"""Tests for the ``amounts`` sidecar used when scaling built-in recipes.

Built-in recipes list ingredients as bare names ("chicken", "rice") so that
``find_recipes_by_ingredients`` and the grocery categoriser can match on them.
That leaves nowhere to put a quantity, which used to mean scaling a built-in
doubled the servings while leaving every ingredient untouched.

``amounts`` maps an ingredient name to a quantity string. Scaling reads it,
scales the number, and renders "2 lbs chicken" for display. Ingredient *names*
stay untouched so matching keeps working.
"""

from recipes import RECIPE_DATABASE, all_recipes, scale_recipe

# Every built-in recipe must carry a quantity for each of its ingredients,
# otherwise scaling it silently does nothing.
RECIPES = RECIPE_DATABASE


def test_every_builtin_recipe_declares_amounts():
    for recipe in RECIPES:
        assert 'amounts' in recipe, f'{recipe["name"]} has no amounts'


def test_every_builtin_amount_has_an_entry_per_ingredient():
    for recipe in RECIPES:
        missing = set(recipe['ingredients']) - set(recipe['amounts'])
        assert not missing, f'{recipe["name"]} missing amounts for {sorted(missing)}'


def test_every_builtin_amount_starts_with_a_number():
    for recipe in RECIPES:
        for name, amount in recipe['amounts'].items():
            assert amount[0].isdigit(), f'{recipe["name"]}: {name} -> {amount!r}'


def test_scaling_a_builtin_actually_changes_its_ingredients():
    recipe = RECIPES[0]
    scaled = scale_recipe(recipe, 2)
    assert scaled['ingredients'] != recipe['ingredients']
    assert scaled['servings'] == recipe['servings'] * 2


def test_scaled_builtin_ingredients_carry_scaled_quantities():
    recipe = RECIPES[0]
    scaled = scale_recipe(recipe, 2)
    # "1.5 lbs chicken" -> "3 lbs chicken"
    assert any(ing.startswith('3 lbs chicken') for ing in scaled['ingredients'])


def test_scaling_down_a_builtin_halves_quantities():
    recipe = RECIPES[0]
    scaled = scale_recipe(recipe, 0.5)
    # "1.5 lbs chicken" -> "0.75 lbs chicken"
    assert any(ing.startswith('0.75 lbs chicken') for ing in scaled['ingredients'])


def test_scaling_does_not_mutate_the_source_amounts():
    recipe = RECIPES[0]
    before = dict(recipe['amounts'])
    scale_recipe(recipe, 3)
    assert recipe['amounts'] == before


def test_ingredient_names_are_preserved_for_matching():
    """The scaled copy is for display; the name must still be findable."""
    recipe = RECIPES[0]
    scaled = scale_recipe(recipe, 2)
    for original, rendered in zip(recipe['ingredients'], scaled['ingredients'], strict=True):
        assert original in rendered


def test_builtin_without_amounts_still_scales_inline_numbers():
    # A user recipe typed as "2 cups rice" has no amounts sidecar.
    scaled = scale_recipe({'name': 'Y', 'servings': 2, 'ingredients': ['2 cups rice']}, 2)
    assert scaled['ingredients'] == ['4 cups rice']


def test_every_builtin_scales_without_error():
    for factor in (0.5, 1, 2, 3):
        for recipe in all_recipes():
            scaled = scale_recipe(recipe, factor)
            assert len(scaled['ingredients']) == len(recipe['ingredients'])
            assert all(isinstance(i, str) and i for i in scaled['ingredients'])
