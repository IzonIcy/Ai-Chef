"""Tests for recipe scaling."""

import pytest

from recipes import RECIPE_DATABASE, scale_recipe


def test_scales_leading_whole_numbers():
    scaled = scale_recipe(
        {"name": "X", "servings": 2, "ingredients": ["2 cups rice", "salt"]}, 2
    )
    assert scaled["ingredients"][0] == "4 cups rice"
    assert scaled["ingredients"][1] == "salt"  # no amount -> unchanged
    assert scaled["servings"] == 4


def test_scales_decimals_and_fractions():
    scaled = scale_recipe(
        {
            "name": "Y",
            "servings": 2,
            "ingredients": ["1.5 tbsp oil", "1/2 cup milk", "0.25 tsp salt"],
        },
        2,
    )
    assert scaled["ingredients"][0] == "3 tbsp oil"
    assert scaled["ingredients"][1] == "1 cup milk"
    assert scaled["ingredients"][2] == "0.5 tsp salt"


def test_fraction_result_rounds_to_two_decimals():
    scaled = scale_recipe(
        {"name": "Z", "servings": 3, "ingredients": ["1/3 cup honey"]}, 0.5
    )
    # 1/6 * 0.5... actually (1/3)*0.5 = 0.1666.. -> 0.17
    assert scaled["ingredients"][0].startswith("0.17 ")
    assert scaled["servings"] == 2  # 3 * 0.5 = 1.5 -> round() -> 2


def test_original_recipe_not_mutated():
    original = RECIPE_DATABASE[0]
    before = list(original["ingredients"])
    scale_recipe(original, 3)
    assert original["ingredients"] == before
    assert original["servings"] >= 1


def test_invalid_factor_raises():
    with pytest.raises(ValueError):
        scale_recipe({"name": "x", "ingredients": []}, 0)
    with pytest.raises(ValueError):
        scale_recipe({"name": "x", "ingredients": []}, -2)
