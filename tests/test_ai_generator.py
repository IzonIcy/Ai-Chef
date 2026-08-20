"""Tests for ai_generator.py — fallback/error paths only, never network calls.

Every test guarantees the OpenAI client stays uninitialized, so the pure
parse/normalize helpers and the no-API-key error paths are exercised without
touching the network.
"""

import json

import pytest

import ai_generator
from ai_generator import (
    _get_client,
    _normalize_list_field,
    _safe_int,
    generate_recipe_with_ai,
    get_cooking_tips,
    parse_ai_recipe,
    suggest_substitutions,
)


@pytest.fixture(autouse=True)
def no_api_key(monkeypatch):
    """Guarantee the OpenAI client is never initialized in tests."""
    monkeypatch.setattr(ai_generator, "client", None)
    # Force _get_client() to see no key regardless of any .env on disk
    monkeypatch.setattr(ai_generator.os, "getenv", lambda name, default=None: default)


# ---------------------------------------------------------------------------
# No-API-key fallback paths (no network)
# ---------------------------------------------------------------------------


def test_get_client_returns_none_without_api_key(no_api_key):
    assert _get_client() is None


def test_generate_recipe_without_api_key_returns_error(no_api_key):
    result = generate_recipe_with_ai(ingredients=["chicken", "rice"])

    assert result["error"] == "OpenAI client not initialized"
    assert "OPENAI_API_KEY" in result["suggestion"]


def test_generate_recipe_error_returned_regardless_of_preferences(no_api_key):
    result = generate_recipe_with_ai(
        ingredients=["chicken"],
        dietary_preference="gluten-free",
        cuisine_type="Asian",
        cook_time=30,
        difficulty="easy",
        description="quick weeknight dinner",
    )

    assert result["error"] == "OpenAI client not initialized"


def test_get_cooking_tips_without_api_key_returns_message(no_api_key):
    assert (
        get_cooking_tips("Chicken Stir-Fry")
        == "Unable to generate tips: OpenAI API key not set"
    )


def test_suggest_substitutions_without_api_key_returns_message(no_api_key):
    assert (
        suggest_substitutions("soy sauce")
        == "Unable to suggest substitutions: OpenAI API key not set"
    )


# ---------------------------------------------------------------------------
# parse_ai_recipe — JSON input
# ---------------------------------------------------------------------------


def test_parse_ai_recipe_parses_valid_json():
    text = json.dumps(
        {
            "name": "Garlic Butter Pasta",
            "servings": 4,
            "cook_time": 25,
            "difficulty": "easy",
            "ingredients": ["pasta", "garlic", "butter"],
            "instructions": ["Boil pasta", "Melt butter"],
            "cuisine": "Italian",
            "dietary": ["vegetarian"],
        }
    )

    result = parse_ai_recipe(text)

    assert "error" not in result
    assert result["name"] == "Garlic Butter Pasta"
    assert result["servings"] == 4
    assert result["cook_time"] == 25
    assert result["difficulty"] == "easy"
    assert result["ingredients"] == ["pasta", "garlic", "butter"]
    assert result["instructions"] == ["Boil pasta", "Melt butter"]
    assert result["cuisine"] == "Italian"
    assert result["dietary"] == ["vegetarian"]


def test_parse_ai_recipe_normalizes_alias_fields_and_string_numbers():
    text = json.dumps(
        {
            "recipe_name": "Slow Cooker Chili",
            "servings": "6",
            "cook_time": "about 8 hours",
            "difficulty": "Easy",
            "ingredients": ["beans", "beef"],
            "instructions": ["Brown beef", "Simmer"],
        }
    )

    result = parse_ai_recipe(text)

    assert result["name"] == "Slow Cooker Chili"
    assert result["servings"] == 6
    assert result["cook_time"] == 8
    assert result["difficulty"] == "easy"
    assert result["cuisine"] == "Custom"  # defaults when absent
    assert result["dietary"] == []


def test_parse_ai_recipe_defaults_unknown_difficulty_to_medium():
    text = json.dumps(
        {
            "name": "Mystery Dish",
            "servings": 2,
            "cook_time": 20,
            "difficulty": "expert",
            "ingredients": ["a"],
            "instructions": ["b"],
        }
    )

    assert parse_ai_recipe(text)["difficulty"] == "medium"


def test_parse_ai_recipe_returns_error_when_ingredients_missing():
    text = json.dumps({"name": "Incomplete", "instructions": ["Boil water"]})

    result = parse_ai_recipe(text)

    assert result["error"] == "Incomplete AI recipe output"
    assert "ingredients" in result["suggestion"].lower()


def test_parse_ai_recipe_returns_error_when_ingredient_list_empty():
    text = json.dumps({"name": "Empty", "ingredients": [], "instructions": ["x"]})

    assert parse_ai_recipe(text)["error"] == "Incomplete AI recipe output"


def test_parse_ai_recipe_extracts_json_embedded_in_markdown():
    text = (
        "Here is your recipe:\n"
        "```json\n"
        '{"name": "Embedded Dish", "servings": 2, "cook_time": 10, '
        '"difficulty": "hard", "ingredients": ["egg"], '
        '"instructions": ["Fry egg"], "cuisine": "American", "dietary": []}\n'
        "```\n"
    )

    result = parse_ai_recipe(text)

    assert result["name"] == "Embedded Dish"
    assert result["difficulty"] == "hard"


# ---------------------------------------------------------------------------
# parse_ai_recipe — labeled text format
# ---------------------------------------------------------------------------


def test_parse_ai_recipe_parses_labeled_text_format():
    text = (
        "Recipe Name: Quick Pasta\n"
        "Servings: 2\n"
        "Cook Time: 15\n"
        "Difficulty: easy\n"
        "Ingredients:\n"
        "- pasta\n"
        "- tomato\n"
        "Instructions:\n"
        "1. Boil the pasta\n"
        "2. Add tomato sauce\n"
    )

    result = parse_ai_recipe(text)

    assert result["name"] == "Quick Pasta"
    assert result["servings"] == 2
    assert result["cook_time"] == 15
    assert result["difficulty"] == "easy"
    assert result["ingredients"] == ["pasta", "tomato"]
    assert result["instructions"] == ["Boil the pasta", "Add tomato sauce"]
    assert result["cuisine"] == "Custom"


def test_parse_ai_recipe_empty_text_returns_incomplete_error():
    result = parse_ai_recipe("")

    assert result["error"] == "Incomplete AI recipe output"


# ---------------------------------------------------------------------------
# normalization helpers
# ---------------------------------------------------------------------------


def test_normalize_list_field_splits_newline_strings_and_strips_markers():
    assert _normalize_list_field("chicken\nrice\nbeans") == [
        "chicken",
        "rice",
        "beans",
    ]
    assert _normalize_list_field("  - soy sauce\n• fish sauce ") == [
        "soy sauce",
        "fish sauce",
    ]


def test_normalize_list_field_filters_blank_entries():
    assert _normalize_list_field(["", "pasta", "  "]) == ["pasta"]
    assert _normalize_list_field(None) == []
    assert _normalize_list_field(42) == []


def test_safe_int_extracts_first_number_from_string():
    assert _safe_int("30 minutes") == 30
    assert _safe_int("about 45") == 45
    assert _safe_int(12) == 12
    assert _safe_int("none") == 0
    assert _safe_int(None) == 0
