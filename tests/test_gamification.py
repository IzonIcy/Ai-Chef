"""Behavioral tests for gamification.py — streaks, achievements, challenges."""

import json

import pytest

from gamification import (
    AchievementTracker,
    CookingStreak,
    GamificationManager,
    WeeklyChallenges,
)


@pytest.fixture
def manager(tmp_path, monkeypatch, clock):
    """A GamificationManager whose default JSON files live in tmp_path."""
    monkeypatch.chdir(tmp_path)
    return GamificationManager()


# ---------------------------------------------------------------------------
# CookingStreak
# ---------------------------------------------------------------------------


def test_first_meal_starts_streak_at_one(tmp_path, clock):
    streak = CookingStreak(filename=str(tmp_path / "streak.json"))

    streak.record_meal_cooked()

    assert streak.get_streak_info() == {
        "current_streak": 1,
        "longest_streak": 1,
        "total_meals": 1,
    }
    assert streak.data["last_cooked_date"] == clock.today_str()


def test_same_day_meals_do_not_increment_streak(tmp_path, clock):
    streak = CookingStreak(filename=str(tmp_path / "streak.json"))

    streak.record_meal_cooked()
    streak.record_meal_cooked()

    info = streak.get_streak_info()
    assert info["current_streak"] == 1
    assert info["total_meals"] == 2


def test_consecutive_day_meals_increment_streak(tmp_path, clock):
    streak = CookingStreak(filename=str(tmp_path / "streak.json"))

    streak.record_meal_cooked()  # day 1
    clock.advance(days=1)
    streak.record_meal_cooked()  # day 2
    clock.advance(days=1)
    streak.record_meal_cooked()  # day 3

    info = streak.get_streak_info()
    assert info["current_streak"] == 3
    assert info["longest_streak"] == 3


def test_gap_in_days_resets_streak(tmp_path, clock):
    streak = CookingStreak(filename=str(tmp_path / "streak.json"))

    streak.record_meal_cooked()  # day 1
    clock.advance(days=3)
    streak.record_meal_cooked()  # day 4 -> gap breaks the streak

    info = streak.get_streak_info()
    assert info["current_streak"] == 1
    assert info["longest_streak"] == 1
    assert info["total_meals"] == 2


def test_quick_meal_counts_meals_at_or_under_thirty_minutes(tmp_path, clock):
    streak = CookingStreak(filename=str(tmp_path / "streak.json"))

    streak.record_meal_cooked(cooking_time=30)
    streak.record_meal_cooked(cooking_time=15)
    streak.record_meal_cooked(cooking_time=31)  # not quick

    assert streak.data["quick_meals"] == 2


def test_zero_cooking_time_is_not_counted_as_quick_meal(tmp_path, clock):
    # cooking_time=0 is falsy in the source, so it is skipped.
    streak = CookingStreak(filename=str(tmp_path / "streak.json"))

    streak.record_meal_cooked(cooking_time=0)

    assert streak.data["quick_meals"] == 0


def test_dietary_meal_counters_increment(tmp_path, clock):
    streak = CookingStreak(filename=str(tmp_path / "streak.json"))

    streak.record_meal_cooked(is_vegetarian=True)
    streak.record_meal_cooked(is_vegan=True)
    streak.record_meal_cooked(is_vegetarian=True, is_vegan=True)

    assert streak.data["vegetarian_meals"] == 2
    assert streak.data["vegan_meals"] == 2


def test_cuisine_counts_are_normalized_to_lowercase(tmp_path, clock):
    streak = CookingStreak(filename=str(tmp_path / "streak.json"))

    streak.record_meal_cooked(cuisine=" Italian ")

    assert streak.data["cuisine_counts"] == {"italian": 1}


def test_streak_loads_defaults_for_corrupt_file(tmp_path):
    streak_file = tmp_path / "streak.json"
    streak_file.write_text("not json")

    streak = CookingStreak(filename=str(streak_file))

    assert streak.get_streak_info() == {
        "current_streak": 0,
        "longest_streak": 0,
        "total_meals": 0,
    }


# ---------------------------------------------------------------------------
# AchievementTracker
# ---------------------------------------------------------------------------


def test_default_achievements_all_start_locked(tmp_path):
    tracker = AchievementTracker(filename=str(tmp_path / "achievements.json"))

    assert len(tracker.achievements) == 11
    assert tracker.get_unlocked_achievements() == []
    assert len(tracker.get_locked_achievements()) == 11


def test_unlock_achievement_returns_true_once_and_persists(tmp_path):
    tracker = AchievementTracker(filename=str(tmp_path / "achievements.json"))

    assert tracker.unlock_achievement("first_recipe") is True
    assert tracker.unlock_achievement("first_recipe") is False  # already unlocked

    unlocked = tracker.get_unlocked_achievements()
    assert [a.id for a in unlocked] == ["first_recipe"]
    assert unlocked[0].unlock_date is not None

    reloaded = AchievementTracker(filename=str(tmp_path / "achievements.json"))
    assert [a.id for a in reloaded.get_unlocked_achievements()] == ["first_recipe"]


def test_unlock_unknown_achievement_returns_false(tmp_path):
    tracker = AchievementTracker(filename=str(tmp_path / "achievements.json"))

    assert tracker.unlock_achievement("not_real") is False
    assert tracker.get_unlocked_achievements() == []


# ---------------------------------------------------------------------------
# WeeklyChallenges
# ---------------------------------------------------------------------------


def test_default_challenges_start_at_zero_progress(tmp_path, clock):
    challenges = WeeklyChallenges(filename=str(tmp_path / "challenges.json"))

    active = challenges.get_active_challenges()

    assert len(active) == 3
    assert all(c["progress"] == 0 for c in active)
    assert all(c["completed"] is False for c in active)
    assert challenges.challenges["week_start"] == clock.week_start_str()


def test_update_challenge_progress_completes_at_target(tmp_path, clock):
    challenges = WeeklyChallenges(filename=str(tmp_path / "challenges.json"))

    for _ in range(5):
        challenges.update_challenge_progress("cook_five")

    active = {c["id"]: c for c in challenges.get_active_challenges()}
    assert active["cook_five"]["progress"] == 5
    assert active["cook_five"]["completed"] is True


def test_completed_challenge_ignores_further_updates(tmp_path, clock):
    challenges = WeeklyChallenges(filename=str(tmp_path / "challenges.json"))

    for _ in range(7):  # target is 5
        challenges.update_challenge_progress("cook_five")

    active = {c["id"]: c for c in challenges.get_active_challenges()}
    assert active["cook_five"]["progress"] == 5


def test_update_unknown_challenge_is_a_noop(tmp_path, clock):
    challenges = WeeklyChallenges(filename=str(tmp_path / "challenges.json"))

    challenges.update_challenge_progress("ghost_challenge")

    active = challenges.get_active_challenges()
    assert len(active) == 3
    assert all(c["progress"] == 0 for c in active)


def test_progress_percent_clamps_and_handles_unknown_ids(tmp_path, clock):
    challenges = WeeklyChallenges(filename=str(tmp_path / "challenges.json"))

    challenges.update_challenge_progress("healthy_week")  # 1 of 3
    assert challenges.get_progress_percent("healthy_week") == 33

    for _ in range(3):
        challenges.update_challenge_progress("cook_five")  # 3 of 5
    assert challenges.get_progress_percent("cook_five") == 60

    assert challenges.get_progress_percent("unknown") == 0


def test_week_reset_resets_stale_challenge_file(tmp_path, clock):
    challenge_file = tmp_path / "challenges.json"
    stale = {
        "week_start": "2020-01-01",
        "challenges": [
            {
                "id": "cook_five",
                "name": "x",
                "description": "x",
                "target": 5,
                "reward": "r",
                "progress": 5,
                "completed": True,
            }
        ],
    }
    challenge_file.write_text(json.dumps(stale))

    challenges = WeeklyChallenges(filename=str(challenge_file))
    active = challenges.get_active_challenges()

    assert challenges.challenges["week_start"] == clock.week_start_str()
    assert active[0]["progress"] == 0
    assert active[0]["completed"] is False


def test_get_completed_challenges_returns_only_completed(tmp_path, clock):
    challenges = WeeklyChallenges(filename=str(tmp_path / "challenges.json"))

    assert challenges.get_completed_challenges() == []

    for _ in range(5):
        challenges.update_challenge_progress("cook_five")

    assert [c["id"] for c in challenges.get_completed_challenges()] == ["cook_five"]


# ---------------------------------------------------------------------------
# GamificationManager (integration)
# ---------------------------------------------------------------------------


def test_first_meal_unlocks_first_recipe_achievement(manager):
    manager.record_recipe_cooked(recipe_name="Beef Tacos")

    unlocked = {a.id for a in manager.achievements.get_unlocked_achievements()}
    assert "first_recipe" in unlocked
    assert manager.streak.get_streak_info()["total_meals"] == 1


def test_cook_five_challenge_completes_after_five_meals(manager):
    for i in range(5):
        manager.record_recipe_cooked(recipe_name=f"Meal {i}")

    active = {c["id"]: c for c in manager.challenges.get_active_challenges()}
    assert active["cook_five"]["completed"] is True


def test_italian_explorer_unlocks_after_three_italian_meals(manager):
    for _ in range(3):
        manager.record_recipe_cooked(recipe_name="Pasta", cuisine="Italian")

    unlocked = {a.id for a in manager.achievements.get_unlocked_achievements()}
    assert "italian_explorer" in unlocked


def test_vegetarian_champion_unlocks_and_healthy_week_completes(manager):
    for _ in range(5):
        manager.record_recipe_cooked(recipe_name="Salad", is_vegetarian=True)

    unlocked = {a.id for a in manager.achievements.get_unlocked_achievements()}
    assert "vegetarian_champion" in unlocked

    active = {c["id"]: c for c in manager.challenges.get_active_challenges()}
    assert active["healthy_week"]["completed"] is True


def test_speed_cook_unlocks_after_five_quick_meals(manager):
    for _ in range(5):
        manager.record_recipe_cooked(recipe_name="Quick Dish", cooking_time=15)

    unlocked = {a.id for a in manager.achievements.get_unlocked_achievements()}
    assert "speed_cook" in unlocked


def test_week_warrior_unlocks_after_seven_day_streak(manager, clock):
    for _ in range(7):
        manager.record_recipe_cooked(recipe_name="Steady Dish")
        clock.advance(days=1)

    unlocked = {a.id for a in manager.achievements.get_unlocked_achievements()}
    assert "week_warrior" in unlocked
    assert manager.streak.get_streak_info()["current_streak"] == 7


def test_gourmet_chef_unlocks_after_ten_meals(manager):
    for i in range(10):
        manager.record_recipe_cooked(recipe_name=f"Meal {i}")

    unlocked = {a.id for a in manager.achievements.get_unlocked_achievements()}
    assert "gourmet_chef" in unlocked


def test_try_new_cuisine_challenge_progresses_once_per_cuisine(manager):
    manager.record_recipe_cooked(recipe_name="Tacos", cuisine="Mexican")
    manager.record_recipe_cooked(recipe_name="Burritos", cuisine="Mexican")

    active = {c["id"]: c for c in manager.challenges.get_active_challenges()}
    assert active["try_new_cuisine"]["progress"] == 1


def test_gamification_status_returns_expected_structure(manager):
    manager.record_recipe_cooked(recipe_name="Beef Tacos")

    status = manager.get_gamification_status()

    assert set(status.keys()) == {"streak", "achievements", "challenges"}
    assert set(status["streak"].keys()) == {
        "current_streak",
        "longest_streak",
        "total_meals",
    }
    assert set(status["achievements"].keys()) == {"unlocked", "locked"}
    assert len(status["challenges"]) == 3
