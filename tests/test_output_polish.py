"""Regressions for two output warts found after the search and scaling work.

Scaling a recipe down to a single unit rendered "1 cups broccoli", and short
search terms matched inside unrelated words, so "asi" hit any instruction
containing "roasting". Both are user-visible, so both are pinned here.
"""

from recipes import RECIPE_DATABASE, scale_recipe, search_recipes

_RECIPE = {
    'name': 'Test',
    'servings': 4,
    'ingredients': ['chicken', 'broccoli', 'garlic'],
    'amounts': {'chicken': '2 lbs', 'broccoli': '4 cups', 'garlic': '2 cloves'},
    'instructions': [],
}


# Scaling: singular units


def test_scaling_to_one_singularises_the_unit():
    scaled = scale_recipe(_RECIPE, 0.25)
    assert scaled['ingredients'][0] == '0.5 lbs chicken'
    assert scaled['ingredients'][1] == '1 cup broccoli'
    # 0.5 is not 1, so the plural unit stays: "0.5 cloves", not "0.5 clove".
    assert scaled['ingredients'][2] == '0.5 cloves garlic'


def test_scaling_to_one_keeps_plural_when_the_count_is_not_one():
    scaled = scale_recipe(_RECIPE, 0.5)
    assert scaled['ingredients'][1] == '2 cups broccoli'


def test_singularised_unit_keeps_the_remainder():
    recipe = {
        'name': 'T',
        'servings': 2,
        'ingredients': ['broccoli'],
        'amounts': {'broccoli': '2 cups florets'},
        'instructions': [],
    }
    assert scale_recipe(recipe, 0.5)['ingredients'] == ['1 cup florets broccoli']


def test_unknown_units_are_left_alone():
    recipe = {
        'name': 'T',
        'servings': 2,
        'ingredients': ['water'],
        'amounts': {'water': '2 pints'},
        'instructions': [],
    }
    # Not in the known-plural map, so it is passed through rather than mangled.
    assert scale_recipe(recipe, 0.5)['ingredients'] == ['1 pints water']


def test_no_builtin_recipe_renders_a_singular_count_with_a_plural_unit():
    for recipe in RECIPE_DATABASE:
        for factor in (0.25, 0.5, 1, 2):
            for rendered in scale_recipe(recipe, factor)['ingredients']:
                assert not rendered.startswith('1 cups '), f'{recipe["name"]}: {rendered}'
                assert not rendered.startswith('1 cloves '), f'{recipe["name"]}: {rendered}'
                assert not rendered.startswith('1 lbs '), f'{recipe["name"]}: {rendered}'


# Search: word boundaries


def test_short_term_does_not_match_inside_an_unrelated_word():
    # "asi" is a prefix of "asian" but not of "roasting".
    names = [r['name'] for r in search_recipes('asi')]
    assert names, 'asian cuisine should still match'
    assert 'Creamy Tomato Soup' not in names


def test_prefix_match_still_works():
    assert 'Garlic Chicken and Rice' in [r['name'] for r in search_recipes('chick')]


def test_infix_search_no_longer_matches():
    # "icken" is inside "chicken" but is not a word prefix.
    assert search_recipes('icken') == []


def test_hyphenated_terms_still_match():
    assert 'Chicken Stir-Fry with Broccoli' in [r['name'] for r in search_recipes('stir-fry')]


def test_word_matches_inside_a_longer_word():
    # "cream" should find "sour cream" and "Creamy Tomato Soup".
    assert len(search_recipes('cream')) >= 2


def test_every_builtin_remains_reachable_by_name():
    for recipe in RECIPE_DATABASE:
        # The first word of the name is a prefix of the name.
        first_word = recipe['name'].split()[0]
        assert recipe['name'] in [r['name'] for r in search_recipes(first_word)]
