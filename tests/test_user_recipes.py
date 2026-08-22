"""Tests for user-defined recipes."""

import pytest

import recipes
from recipes import (
    add_user_recipe,
    all_recipes,
    filter_recipes,
    get_recipe_by_name,
    load_user_recipes,
    remove_user_recipe,
)


@pytest.fixture
def data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("AI_CHEF_DATA_DIR", str(tmp_path / "data"))
    return tmp_path / "data"


def _sample(name="My Secret Chili"):
    return {
        "name": name,
        "ingredients": ["beans", "chili powder"],
        "cook_time": 45,
        "difficulty": "medium",
        "cuisine": "Tex-Mex",
        "dietary": ["vegetarian"],
        "servings": 4,
        "instructions": ["Brown it all", "Simmer 30 minutes"],
    }


def test_load_returns_empty_when_missing(data_dir):
    assert load_user_recipes() == []


def test_roundtrip_and_merge_into_all_recipes(data_dir):
    add_user_recipe(_sample())
    assert [r["name"] for r in load_user_recipes()] == ["My Secret Chili"]
    assert "My Secret Chili" in [r["name"] for r in all_recipes()]
    assert len(all_recipes()) == len(recipes.RECIPE_DATABASE) + 1


def test_duplicate_names_rejected_case_insensitively(data_dir):
    assert add_user_recipe(_sample()) is True
    assert add_user_recipe(_sample(name="my secret chili")) is False
    assert len(load_user_recipes()) == 1


def test_nameless_recipe_rejected(data_dir):
    with pytest.raises(ValueError):
        add_user_recipe({"ingredients": ["air"]})


def test_lookup_and_filter_include_user_recipes(data_dir):
    add_user_recipe(_sample())

    found = get_recipe_by_name("my secret chili")
    assert found and found["cuisine"] == "Tex-Mex"

    veg = filter_recipes(dietary="vegetarian")
    assert any(r["name"] == "My Secret Chili" for r in veg)

    matches = recipes.find_recipes_by_ingredients(["beans"])
    assert any(m["recipe"]["name"] == "My Secret Chili" for m in matches)


def test_remove_user_recipe(data_dir):
    add_user_recipe(_sample())
    assert remove_user_recipe("MY SECRET CHILI") is True
    assert load_user_recipes() == []
    assert get_recipe_by_name("my secret chili") is None
    assert remove_user_recipe("nope") is False
