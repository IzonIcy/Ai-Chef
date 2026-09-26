"""Tests for free-text recipe search and the cuisine/difficulty vocabularies.

Search exists because the other two entry points are too strict to be useful
for exploring: ``find_recipes_by_ingredients`` needs exact ingredient matches and
``filter_recipes`` needs an exact cuisine or difficulty. Neither answers
"show me anything with noodles" or "what Mexican food is there".
"""

import pytest

from recipes import (
    RECIPE_DATABASE,
    add_user_recipe,
    all_cuisines,
    search_recipes,
)

# Minimal recipe shape for user-recipe fixtures.
_USER_RECIPE = {
    'name': 'Grandma Casserole',
    'ingredients': ['chicken', 'rice', 'gochujang'],
    'cook_time': 50,
    'difficulty': 'easy',
    'cuisine': 'Comfort',
    'dietary': [],
    'servings': 4,
    'instructions': ['Bake until golden'],
}

# A second user recipe that uses chicken only as an ingredient, never in its
# name, so ranking can be observed.
_CHICKEN_SIDE_RECIPE = {
    'name': 'Weeknight Rice Bowl',
    'ingredients': ['chicken', 'rice', 'ketchup'],
    'cook_time': 15,
    'difficulty': 'easy',
    'cuisine': 'American',
    'dietary': [],
    'servings': 2,
    'instructions': ['Microwave until hot'],
}


# search_recipes: matching


def test_search_matches_on_recipe_name():
    names = [r['name'] for r in search_recipes('stir-fry')]
    assert names == ['Chicken Stir-Fry with Broccoli']


def test_search_is_case_insensitive():
    assert [r['name'] for r in search_recipes('BROCCOLI')] == [
        r['name'] for r in search_recipes('broccoli')
    ]


def test_search_matches_on_cuisine():
    assert 'Chicken Stir-Fry with Broccoli' in [r['name'] for r in search_recipes('asian')]


def test_search_matches_on_ingredient():
    results = search_recipes('ginger')
    assert results
    assert all('ginger' in r['ingredients'] or 'Ginger' in str(r) for r in results)


def test_search_matches_partial_words():
    # "chick" should find "chicken" without requiring an exact token.
    results = search_recipes('chick')
    assert 'Garlic Chicken and Rice' in [r['name'] for r in results]


def test_search_matches_on_instruction_text():
    results = search_recipes('wok')
    assert 'Chicken Stir-Fry with Broccoli' in [r['name'] for r in results]


# search_recipes: multi-term behaviour


def test_search_requires_every_term_to_match():
    # "chicken" and "cactus" have no recipe containing both.
    assert search_recipes('chicken cactus') == []


def test_search_combines_terms_across_different_fields():
    # "caesar" is a name/dietary hit, "chicken" an ingredient hit.
    results = search_recipes('caesar chicken')
    assert results == []  # no single recipe has both

    results = search_recipes('chicken broccoli')
    assert 'Chicken Stir-Fry with Broccoli' in [r['name'] for r in results]


def test_search_ignores_extra_whitespace():
    assert search_recipes('   stir-fry  ') == search_recipes('stir-fry')


# search_recipes: ranking and empty cases


def test_search_ranks_name_matches_above_ingredient_matches(tmp_path, monkeypatch):
    monkeypatch.setenv('AI_CHEF_DATA_DIR', str(tmp_path / 'data'))
    add_user_recipe(dict(_CHICKEN_SIDE_RECIPE))

    names = [r['name'] for r in search_recipes('chicken')]

    # "Grandma Casserole" has chicken only as an ingredient, so it must rank
    # below every built-in whose name contains "chicken".
    assert names.index('Weeknight Rice Bowl') > names.index('Garlic Chicken and Rice')


def test_search_with_no_match_returns_empty_list():
    assert search_recipes('zzzzznotarecipe') == []


def test_search_with_empty_query_returns_everything_sorted_by_name():
    results = search_recipes('')
    assert len(results) == len(RECIPE_DATABASE)
    assert [r['name'] for r in results] == sorted(r['name'] for r in RECIPE_DATABASE)


def test_search_with_whitespace_only_query_returns_everything():
    assert len(search_recipes('   ')) == len(RECIPE_DATABASE)


def test_search_does_not_mutate_the_database():
    before = [dict(r) for r in RECIPE_DATABASE]
    search_recipes('chicken')
    assert before == RECIPE_DATABASE


# search_recipes: user recipes are included


def test_search_includes_user_defined_recipes(tmp_path, monkeypatch):
    monkeypatch.setenv('AI_CHEF_DATA_DIR', str(tmp_path / 'data'))
    assert add_user_recipe(dict(_USER_RECIPE)) is True

    results = search_recipes('casserole')
    assert [r['name'] for r in results] == ['Grandma Casserole']


def test_search_finds_user_recipe_by_a_term_the_builtins_lack(tmp_path, monkeypatch):
    monkeypatch.setenv('AI_CHEF_DATA_DIR', str(tmp_path / 'data'))

    # Premise check: no built-in recipe mentions gochujang.
    assert search_recipes('gochujang') == []

    add_user_recipe(dict(_USER_RECIPE))
    assert [r['name'] for r in search_recipes('gochujang')] == ['Grandma Casserole']


# all_cuisines


def test_all_cuisines_lists_every_cuisine_sorted_and_deduplicated():
    cuisines = all_cuisines()
    assert cuisines == sorted(set(cuisines))
    assert 'Italian' in cuisines


def test_all_cuisines_includes_user_recipe_cuisines(tmp_path, monkeypatch):
    monkeypatch.setenv('AI_CHEF_DATA_DIR', str(tmp_path / 'data'))
    add_user_recipe(dict(_USER_RECIPE))
    assert 'Comfort' in all_cuisines()


def test_all_cuisines_is_empty_when_there_are_no_recipes(monkeypatch):
    monkeypatch.setattr('recipes.RECIPE_DATABASE', [])
    monkeypatch.setattr('recipes.load_user_recipes', lambda: [])
    assert all_cuisines() == []


@pytest.mark.parametrize(
    'query,expected',
    [
        ('asian', 'Chicken Stir-Fry with Broccoli'),
        ('ASIAN', 'Chicken Stir-Fry with Broccoli'),
        ('asi', 'Chicken Stir-Fry with Broccoli'),
    ],
)
def test_cuisine_search_accepts_prefixes(query, expected):
    assert expected in [r['name'] for r in search_recipes(query)]
