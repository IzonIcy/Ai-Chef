"""Behavioral tests for recipes.py — ingredient matching and filtering."""

from recipes import (
    RECIPE_DATABASE,
    filter_recipes,
    find_recipes_by_ingredients,
    get_recipe_by_name,
)

# ---------------------------------------------------------------------------
# find_recipes_by_ingredients
# ---------------------------------------------------------------------------


def test_find_returns_recipes_sharing_at_least_one_ingredient():
    results = find_recipes_by_ingredients(['chicken'])

    names = {r['recipe']['name'] for r in results}
    assert 'Chicken Stir-Fry with Broccoli' in names
    assert 'Garlic Chicken and Rice' in names
    assert 'One-Pan Chicken Broccoli Rice' in names
    assert 'Beef Tacos' not in names  # no chicken in the beef recipe


def test_find_sorts_by_match_percentage_descending():
    # "broccoli" appears in 4 recipes with different pool sizes:
    # Stir-Fry (6 ingredients) and Salmon (6) beat One-Pan (7) and Pasta (7)
    results = find_recipes_by_ingredients(['broccoli'])

    order = [r['recipe']['name'] for r in results]
    assert order.index('Chicken Stir-Fry with Broccoli') < order.index(
        'One-Pan Chicken Broccoli Rice'
    )
    assert order.index('Salmon with Roasted Vegetables') < order.index('Vegetarian Pasta Primavera')
    percentages = [r['match_percentage'] for r in results]
    assert percentages == sorted(percentages, reverse=True)


def test_find_full_ingredient_match_reports_zero_missing():
    stir_fry = next(r for r in RECIPE_DATABASE if r['name'] == 'Chicken Stir-Fry with Broccoli')

    results = find_recipes_by_ingredients(stir_fry['ingredients'])
    match = next(r for r in results if r['recipe']['name'] == stir_fry['name'])

    assert match['matching_count'] == 6
    assert match['missing_count'] == 0
    assert match['missing_ingredients'] == []
    assert match['match_percentage'] == 1.0


def test_find_returns_empty_list_for_no_available_ingredients():
    assert find_recipes_by_ingredients([]) == []


def test_find_returns_empty_list_when_no_ingredients_match_any_recipe():
    assert find_recipes_by_ingredients(['unicorn meat', 'dragonfruit']) == []


def test_find_ignores_case_and_whitespace_in_ingredients():
    results = find_recipes_by_ingredients(['  CHICKEN ', 'Broccoli'])

    names = {r['recipe']['name'] for r in results}
    assert 'Chicken Stir-Fry with Broccoli' in names


def test_find_result_contains_expected_metadata_keys():
    results = find_recipes_by_ingredients(['garlic'])

    assert set(results[0].keys()) == {
        'recipe',
        'matching_count',
        'missing_count',
        'match_percentage',
        'missing_ingredients',
    }


# ---------------------------------------------------------------------------
# filter_recipes
# ---------------------------------------------------------------------------


def test_filter_with_no_criteria_returns_all_recipes():
    assert filter_recipes() == RECIPE_DATABASE


def test_filter_returns_a_copy_not_the_database_reference():
    result = filter_recipes()
    result.clear()

    assert RECIPE_DATABASE  # still populated


def test_filter_by_cook_time_returns_recipes_within_limit():
    results = filter_recipes(cook_time=20)

    assert results
    assert all(r['cook_time'] <= 20 for r in results)
    assert 'Chicken Stir-Fry with Broccoli' in {r['name'] for r in results}
    # A recipe over the limit must be excluded.
    assert 'One-Pan Chicken Broccoli Rice' not in {r['name'] for r in results}


def test_filter_by_difficulty_is_case_insensitive():
    results = filter_recipes(difficulty='MEDIUM')

    assert results
    assert all(r['difficulty'] == 'medium' for r in results)
    assert 'Shrimp Scampi' in {r['name'] for r in results}


def test_filter_by_dietary_restriction():
    results = filter_recipes(dietary='vegetarian')

    assert results
    assert all('vegetarian' in r['dietary'] for r in results)
    assert {'Vegetarian Pasta Primavera', 'Classic Caesar Salad'} <= {r['name'] for r in results}
    assert 'Chicken Stir-Fry with Broccoli' not in {r['name'] for r in results}


def test_filter_by_cuisine_is_case_insensitive():
    results = filter_recipes(cuisine='Italian')

    assert results
    assert all(r['cuisine'] == 'Italian' for r in results)
    assert {'Vegetarian Pasta Primavera', 'Classic Caesar Salad', 'Shrimp Scampi'} == {
        r['name'] for r in results
    }


def test_filter_by_cuisine_accepts_a_partial_name():
    results = filter_recipes(cuisine='asi')

    assert results
    assert all('asi' in r['cuisine'].lower() for r in results)


def test_filter_combines_multiple_criteria():
    results = filter_recipes(dietary='vegetarian', cook_time=25)

    assert all('vegetarian' in r['dietary'] for r in results)
    assert all(r['cook_time'] <= 25 for r in results)
    assert 'Classic Caesar Salad' in {r['name'] for r in results}


def test_filter_dietary_conflict_excludes_noncompliant_recipes():
    # A vegan filter must never return a recipe containing meat or fish.
    results = filter_recipes(dietary='vegan')

    assert results
    assert all('vegan' in r['dietary'] for r in results)
    forbidden = {'chicken', 'beef', 'salmon', 'shrimp', 'ground beef'}
    for recipe in results:
        assert not forbidden & {i.lower() for i in recipe['ingredients']}


def test_filter_pool_restricts_the_candidates():
    pool = [r for r in RECIPE_DATABASE if r['cuisine'] == 'Italian']
    results = filter_recipes(pool=pool)

    assert {r['name'] for r in results} == {r['name'] for r in pool}


def test_filter_unknown_cuisine_returns_empty_list():
    assert filter_recipes(cuisine='Sushi') == []


def test_filter_unknown_difficulty_returns_empty_list():
    assert filter_recipes(difficulty='expert') == []


def test_filter_unmatched_dietary_returns_empty_list():
    assert filter_recipes(dietary='keto') == []


def test_filter_zero_cook_time_is_treated_as_no_filter():
    # cook_time=0 is falsy in the source, so it does NOT restrict results.
    # This documents the current behavior.
    assert filter_recipes(cook_time=0) == RECIPE_DATABASE


# ---------------------------------------------------------------------------
# get_recipe_by_name
# ---------------------------------------------------------------------------


def test_get_recipe_by_name_matches_case_insensitively():
    recipe = get_recipe_by_name('beef tacos')

    assert recipe is not None
    assert recipe['name'] == 'Beef Tacos'


def test_get_recipe_by_name_returns_none_for_unknown_recipe():
    assert get_recipe_by_name('Ghost Toast') is None


def test_get_recipe_by_name_returns_none_for_empty_string():
    assert get_recipe_by_name('') is None
