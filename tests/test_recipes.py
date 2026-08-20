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
    results = find_recipes_by_ingredients(["chicken"])

    names = {r["recipe"]["name"] for r in results}
    assert "Chicken Stir-Fry with Broccoli" in names
    assert "Garlic Chicken and Rice" in names
    assert "One-Pan Chicken Broccoli Rice" in names
    assert "Beef Tacos" not in names  # no chicken in the beef recipe


def test_find_sorts_by_match_percentage_descending():
    # "broccoli" appears in 4 recipes with different pool sizes:
    # Stir-Fry (6 ingredients) and Salmon (6) beat One-Pan (7) and Pasta (7)
    results = find_recipes_by_ingredients(["broccoli"])

    order = [r["recipe"]["name"] for r in results]
    assert order.index("Chicken Stir-Fry with Broccoli") < order.index(
        "One-Pan Chicken Broccoli Rice"
    )
    assert order.index("Salmon with Roasted Vegetables") < order.index(
        "Vegetarian Pasta Primavera"
    )
    percentages = [r["match_percentage"] for r in results]
    assert percentages == sorted(percentages, reverse=True)


def test_find_full_ingredient_match_reports_zero_missing():
    stir_fry = next(
        r for r in RECIPE_DATABASE if r["name"] == "Chicken Stir-Fry with Broccoli"
    )

    results = find_recipes_by_ingredients(stir_fry["ingredients"])
    match = next(r for r in results if r["recipe"]["name"] == stir_fry["name"])

    assert match["matching_count"] == 6
    assert match["missing_count"] == 0
    assert match["missing_ingredients"] == []
    assert match["match_percentage"] == 1.0


def test_find_returns_empty_list_for_no_available_ingredients():
    assert find_recipes_by_ingredients([]) == []


def test_find_returns_empty_list_when_no_ingredients_match_any_recipe():
    assert find_recipes_by_ingredients(["unicorn meat", "dragonfruit"]) == []


def test_find_ignores_case_and_whitespace_in_ingredients():
    results = find_recipes_by_ingredients(["  CHICKEN ", "Broccoli"])

    names = {r["recipe"]["name"] for r in results}
    assert "Chicken Stir-Fry with Broccoli" in names


def test_find_result_contains_expected_metadata_keys():
    results = find_recipes_by_ingredients(["garlic"])

    assert set(results[0].keys()) == {
        "recipe",
        "matching_count",
        "missing_count",
        "match_percentage",
        "missing_ingredients",
    }


# ---------------------------------------------------------------------------
# filter_recipes
# ---------------------------------------------------------------------------


def test_filter_with_no_criteria_returns_all_recipes():
    assert filter_recipes() == RECIPE_DATABASE


def test_filter_returns_a_copy_not_the_database_reference():
    result = filter_recipes()
    result.clear()

    assert len(RECIPE_DATABASE) == 10


def test_filter_by_cook_time_returns_recipes_within_limit():
    results = filter_recipes(cook_time=20)

    names = {r["name"] for r in results}
    assert names == {
        "Chicken Stir-Fry with Broccoli",
        "Beef Tacos",
        "Classic Caesar Salad",
        "Shrimp Scampi",
    }
    assert all(r["cook_time"] <= 20 for r in results)


def test_filter_by_difficulty_is_case_insensitive():
    results = filter_recipes(difficulty="MEDIUM")

    names = {r["name"] for r in results}
    assert names == {
        "Salmon with Roasted Vegetables",
        "Veggie Buddha Bowl",
        "Shrimp Scampi",
    }


def test_filter_by_dietary_restriction():
    results = filter_recipes(dietary="vegetarian")

    names = {r["name"] for r in results}
    assert names == {
        "Vegetarian Pasta Primavera",
        "Creamy Tomato Soup",
        "Classic Caesar Salad",
    }


def test_filter_by_cuisine_is_case_insensitive():
    results = filter_recipes(cuisine="Italian")

    names = {r["name"] for r in results}
    assert names == {
        "Vegetarian Pasta Primavera",
        "Classic Caesar Salad",
        "Shrimp Scampi",
    }


def test_filter_combines_multiple_criteria():
    results = filter_recipes(dietary="vegetarian", cook_time=25)

    names = {r["name"] for r in results}
    assert names == {"Vegetarian Pasta Primavera", "Classic Caesar Salad"}


def test_filter_dietary_conflict_excludes_noncompliant_recipes():
    # A vegan filter must never return chicken dishes
    results = filter_recipes(dietary="vegan")

    names = {r["name"] for r in results}
    assert names == {"Veggie Buddha Bowl"}
    assert "Chicken Stir-Fry with Broccoli" not in names
    assert "Beef Tacos" not in names


def test_filter_unknown_cuisine_returns_empty_list():
    assert filter_recipes(cuisine="Sushi") == []


def test_filter_unknown_difficulty_returns_empty_list():
    assert filter_recipes(difficulty="expert") == []


def test_filter_unmatched_dietary_returns_empty_list():
    assert filter_recipes(dietary="keto") == []


def test_filter_zero_cook_time_is_treated_as_no_filter():
    # cook_time=0 is falsy in the source, so it does NOT restrict results.
    # This documents the current behavior.
    assert filter_recipes(cook_time=0) == RECIPE_DATABASE


# ---------------------------------------------------------------------------
# get_recipe_by_name
# ---------------------------------------------------------------------------


def test_get_recipe_by_name_matches_case_insensitively():
    recipe = get_recipe_by_name("beef tacos")

    assert recipe is not None
    assert recipe["name"] == "Beef Tacos"


def test_get_recipe_by_name_returns_none_for_unknown_recipe():
    assert get_recipe_by_name("Ghost Toast") is None


def test_get_recipe_by_name_returns_none_for_empty_string():
    assert get_recipe_by_name("") is None
