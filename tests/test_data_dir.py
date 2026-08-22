"""Tests for the central data directory."""

import json

from gamification import AchievementTracker, CookingStreak, WeeklyChallenges
from meal_planner import MealPlanner, PantryManager, SavedRecipes


def _expected_file(tmp_path, name):
    return tmp_path / "ai-chef" / name


def test_data_dir_env_override_used_by_all_classes(tmp_path, monkeypatch):
    monkeypatch.setenv("AI_CHEF_DATA_DIR", str(tmp_path / "ai-chef"))

    # Trigger a write through each class so every default file is created.
    streak = CookingStreak()
    streak.data["current_streak"] = 3
    streak.save_streak()

    AchievementTracker().save_achievements()
    WeeklyChallenges().save_challenges()

    planner = MealPlanner()
    planner.meal_plan["2026-01-05"] = {"Monday": {}}
    planner.save_meal_plan()

    PantryManager().save_items()
    SavedRecipes().save_to_file()

    for name in (
        "cooking_streak.json",
        "achievements.json",
        "weekly_challenges.json",
        "meal_plans.json",
        "pantry_inventory.json",
        "saved_recipes.json",
    ):
        assert _expected_file(tmp_path, name).exists(), f"missing {name}"

    reloaded = CookingStreak()
    assert reloaded.filename == streak.filename
    assert reloaded.data["current_streak"] == 3


def test_explicit_filename_still_wins(tmp_path, monkeypatch):
    monkeypatch.setenv("AI_CHEF_DATA_DIR", str(tmp_path / "data"))

    explicit = tmp_path / "elsewhere.json"
    planner = MealPlanner(filename=str(explicit))
    planner.save_meal_plan()
    assert explicit.exists()
    assert not _expected_file(tmp_path, "meal_plans.json").exists()


def test_xdg_data_home_respected(tmp_path, monkeypatch):
    monkeypatch.delenv("AI_CHEF_DATA_DIR", raising=False)
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "xdg"))
    monkeypatch.chdir(tmp_path)

    planner = MealPlanner()
    planner.save_meal_plan()

    xdg_file = tmp_path / "xdg" / "ai-chef" / "meal_plans.json"
    assert xdg_file.exists()
    assert isinstance(json.loads(xdg_file.read_text()), dict)
