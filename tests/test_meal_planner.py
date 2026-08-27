"""Behavioral tests for meal_planner.py — weekly plans, groceries, pantry, saves."""

import json

import pytest

from meal_planner import MealPlanner, PantryManager, SavedRecipes
from recipes import RECIPE_DATABASE

RECIPE_NAMES = {r["name"] for r in RECIPE_DATABASE}


# ---------------------------------------------------------------------------
# MealPlanner.create_weekly_plan
# ---------------------------------------------------------------------------


def test_create_weekly_plan_returns_plan_for_all_seven_days(tmp_path, clock):
    planner = MealPlanner(filename=str(tmp_path / "plan.json"))

    plan = planner.create_weekly_plan()

    assert list(plan.keys()) == [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    for day_info in plan.values():
        assert {"recipe", "cook_time", "servings"} <= set(day_info)
        assert day_info["recipe"] in RECIPE_NAMES


def test_create_weekly_plan_uses_distinct_recipes_per_day(tmp_path, clock):
    planner = MealPlanner(filename=str(tmp_path / "plan.json"))

    plan = planner.create_weekly_plan()

    recipes_used = [day_info["recipe"] for day_info in plan.values()]
    assert len(set(recipes_used)) == 7


def test_create_weekly_plan_is_deterministic(tmp_path, clock):
    p1 = MealPlanner(filename=str(tmp_path / "p1.json"))
    p2 = MealPlanner(filename=str(tmp_path / "p2.json"))

    assert p1.create_weekly_plan() == p2.create_weekly_plan()


def test_create_weekly_plan_persists_plan_for_today(tmp_path, clock):
    planner = MealPlanner(filename=str(tmp_path / "plan.json"))

    plan = planner.create_weekly_plan()

    assert planner.meal_plan[clock.today_str()] == plan
    saved = json.loads((tmp_path / "plan.json").read_text())
    assert saved[clock.today_str()] == plan


def test_create_weekly_plan_repeats_matches_instead_of_violating_diet(tmp_path, clock):
    # Only one vegan recipe exists (< 7). The plan must repeat it across
    # the week rather than silently pulling in non-vegan recipes.
    planner = MealPlanner(filename=str(tmp_path / "plan.json"))

    plan = planner.create_weekly_plan(dietary_preference="vegan")

    assert len(plan) == 7
    assert all(day_info["recipe"] != "Beef Tacos" for day_info in plan.values())


def test_create_weekly_plan_respects_cook_time_cap_with_repetition(tmp_path, clock):
    # Only 4 recipes fit in 20 minutes (< 7): repeat them instead of
    # slipping slower recipes into the plan.
    planner = MealPlanner(filename=str(tmp_path / "plan.json"))

    plan = planner.create_weekly_plan(max_cook_time=20)

    assert len(plan) == 7
    assert all(day_info["cook_time"] <= 20 for day_info in plan.values())




def test_export_grocery_list_csv_format(tmp_path):
    planner = MealPlanner(filename=str(tmp_path / "plan.json"))
    plan = planner.create_weekly_plan()
    grocery_list = planner.generate_grocery_list(plan)

    csv_path = tmp_path / "grocery-test.csv"
    MealPlanner.export_grocery_list(grocery_list, csv_path.with_suffix(""))

    import csv
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) > 0
    assert "category" in rows[0]
    assert "item" in rows[0]
    assert "quantity" in rows[0]
    assert "unit" in rows[0]

def test_export_grocery_list_markdown_format(tmp_path):
    planner = MealPlanner(filename=str(tmp_path / "plan.json"))
    plan = planner.create_weekly_plan()
    grocery_list = planner.generate_grocery_list(plan)

    md_path = tmp_path / "groccery-test.md"
    MealPlanner.export_grocery_list(grocery_list, md_path.with_suffix(""))

    md_content = md_path.read_text()
    assert "- [ ] " in md_content
    assert "## " in md_content

# ---------------------------------------------------------------------------
# MealPlanner.add_meal_to_plan / get_current_plan
# ---------------------------------------------------------------------------


def test_add_meal_to_plan_adds_known_recipe_case_insensitively(tmp_path, clock):
    planner = MealPlanner(filename=str(tmp_path / "plan.json"))

    assert planner.add_meal_to_plan("Monday", "beef tacos") is True

    assert planner.get_current_plan()["Monday"] == {
        "recipe": "Beef Tacos",
        "cook_time": 20,
        "servings": 4,
    }


def test_add_meal_to_plan_returns_false_for_unknown_recipe(tmp_path, clock):
    planner = MealPlanner(filename=str(tmp_path / "plan.json"))

    assert planner.add_meal_to_plan("Monday", "Ghost Toast") is False
    assert planner.get_current_plan() == {}


def test_get_current_plan_empty_for_new_planner(tmp_path, clock):
    planner = MealPlanner(filename=str(tmp_path / "plan.json"))

    assert planner.get_current_plan() == {}


def test_load_meal_plan_reads_existing_plan_for_today(tmp_path, clock):
    plan_file = tmp_path / "plan.json"
    existing = {
        clock.today_str(): {
            "Monday": {"recipe": "Beef Tacos", "cook_time": 20, "servings": 4}
        }
    }
    plan_file.write_text(json.dumps(existing))

    planner = MealPlanner(filename=str(plan_file))

    assert planner.get_current_plan() == existing[clock.today_str()]


def test_load_meal_plan_returns_empty_for_corrupt_file(tmp_path):
    plan_file = tmp_path / "plan.json"
    plan_file.write_text("{not valid json")

    planner = MealPlanner(filename=str(plan_file))

    assert planner.meal_plan == {}


# ---------------------------------------------------------------------------
# MealPlanner.generate_grocery_list
# ---------------------------------------------------------------------------


def _meal_info(recipe_name):
    return {"recipe": recipe_name, "cook_time": 20, "servings": 4}


def test_generate_grocery_list_groups_ingredients_by_category(tmp_path, clock):
    planner = MealPlanner(filename=str(tmp_path / "plan.json"))
    plan = {"Monday": _meal_info("Chicken Stir-Fry with Broccoli")}

    grocery = planner.generate_grocery_list(plan)

    assert {i["item"] for i in grocery["Proteins"]} == {"Chicken"}
    assert {i["item"] for i in grocery["Vegetables"]} == {"Broccoli"}
    assert {"Soy Sauce", "Garlic", "Ginger", "Oil"} <= {
        i["item"] for i in grocery["Pantry"]
    }
    chicken = next(i for i in grocery["Proteins"] if i["item"] == "Chicken")
    assert chicken["quantity"] == 1
    assert chicken["unit"] == "recipe-use"


def test_generate_grocery_list_aggregates_repeated_meals(tmp_path, clock):
    planner = MealPlanner(filename=str(tmp_path / "plan.json"))
    meal = _meal_info("Chicken Stir-Fry with Broccoli")
    plan = {"Monday": meal, "Tuesday": meal}

    grocery = planner.generate_grocery_list(plan)

    chicken = next(i for i in grocery["Proteins"] if i["item"] == "Chicken")
    assert chicken["quantity"] == 2


def test_generate_grocery_list_puts_uncategorized_ingredients_in_other(tmp_path, clock):
    planner = MealPlanner(filename=str(tmp_path / "plan.json"))
    plan = {"Monday": _meal_info("Shrimp Scampi")}

    grocery = planner.generate_grocery_list(plan)

    # white wine and lemon are not in any category map
    assert {i["item"] for i in grocery["Other"]} == {"White Wine", "Lemon"}


def test_generate_grocery_list_empty_plan_returns_empty_dict(tmp_path, clock):
    planner = MealPlanner(filename=str(tmp_path / "plan.json"))

    assert planner.generate_grocery_list({}) == {}


def test_generate_grocery_list_defaults_to_current_plan(tmp_path, clock):
    planner = MealPlanner(filename=str(tmp_path / "plan.json"))
    planner.add_meal_to_plan("Monday", "Beef Tacos")

    grocery = planner.generate_grocery_list()

    assert {i["item"] for i in grocery["Proteins"]} == {"Ground Beef"}
    assert {i["item"] for i in grocery["Dairy"]} == {"Cheese", "Sour Cream"}


def test_generate_grocery_list_with_no_current_plan_returns_empty(tmp_path, clock):
    planner = MealPlanner(filename=str(tmp_path / "plan.json"))

    assert planner.generate_grocery_list() == {}


# ---------------------------------------------------------------------------
# PantryManager
# ---------------------------------------------------------------------------


def test_pantry_add_item_stores_normalized_title_case(tmp_path):
    pantry = PantryManager(filename=str(tmp_path / "pantry.json"))

    assert (
        pantry.add_item("  extra virgin olive oil ", quantity=2, unit="bottle") is True
    )

    items = pantry.get_all_items()
    assert len(items) == 1
    assert items[0]["name"] == "Extra Virgin Olive Oil"
    assert items[0]["quantity"] == 2
    assert items[0]["unit"] == "bottle"


def test_pantry_add_item_increments_existing_quantity(tmp_path):
    pantry = PantryManager(filename=str(tmp_path / "pantry.json"))
    pantry.add_item("chicken", quantity=1)

    assert pantry.add_item("Chicken", quantity=3) is True

    items = pantry.get_all_items()
    assert len(items) == 1
    assert items[0]["quantity"] == 4


def test_pantry_remove_item_returns_true_then_false(tmp_path):
    pantry = PantryManager(filename=str(tmp_path / "pantry.json"))
    pantry.add_item("chicken")

    assert pantry.remove_item("  CHICKEN ") is True
    assert pantry.get_all_items() == []
    assert pantry.remove_item("chicken") is False


def test_pantry_get_ingredients_returns_normalized_names(tmp_path):
    pantry = PantryManager(filename=str(tmp_path / "pantry.json"))
    pantry.add_item("Broccoli")

    assert pantry.get_pantry_ingredients() == ["broccoli"]


def test_pantry_expiring_items_sorted_by_days_left(tmp_path, clock):
    pantry = PantryManager(filename=str(tmp_path / "pantry.json"))
    # clock is frozen at 2026-01-05
    pantry.add_item("milk", expires_on="2026-01-07")  # 2 days left
    pantry.add_item("eggs", expires_on="2026-01-04")  # already expired (-1)
    pantry.add_item("flour", expires_on="2026-02-01")  # far outside window
    pantry.add_item("salt")  # no expiry at all

    expiring = pantry.get_expiring_items(within_days=3)

    assert [e["name"] for e in expiring] == ["Eggs", "Milk"]
    assert expiring[0]["days_left"] == -1
    assert expiring[1]["days_left"] == 2


def test_pantry_expiring_items_skips_malformed_dates(tmp_path, clock):
    pantry = PantryManager(filename=str(tmp_path / "pantry.json"))
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        pantry.add_item("milk", expires_on="not-a-date")

    # Malformed dates are rejected at add time, so nothing expires
    assert pantry.get_expiring_items() == []


# ---------------------------------------------------------------------------
# SavedRecipes
# ---------------------------------------------------------------------------


def test_saved_recipes_add_rejects_duplicates_and_searches(tmp_path, clock):
    saved = SavedRecipes(filename=str(tmp_path / "saved.json"))
    recipe = {"name": "Beef Tacos", "cook_time": 20}

    assert saved.add_recipe(dict(recipe)) is True
    assert saved.add_recipe(dict(recipe)) is False  # duplicate

    all_saved = saved.get_all_saved()
    assert len(all_saved) == 1
    assert "saved_at" in all_saved[0]

    assert [r["name"] for r in saved.search_saved("beef")] == ["Beef Tacos"]
    assert saved.search_saved("salmon") == []


def test_saved_recipes_remove_returns_true_then_false(tmp_path, clock):
    saved = SavedRecipes(filename=str(tmp_path / "saved.json"))
    saved.add_recipe({"name": "Beef Tacos"})

    assert saved.remove_recipe("Beef Tacos") is True
    assert saved.get_all_saved() == []
    assert saved.remove_recipe("Beef Tacos") is False


def test_saved_recipes_persist_across_reload(tmp_path, clock):
    saved_file = tmp_path / "saved.json"
    saved = SavedRecipes(filename=str(saved_file))
    saved.add_recipe({"name": "Beef Tacos"})

    reloaded = SavedRecipes(filename=str(saved_file))

    assert [r["name"] for r in reloaded.get_all_saved()] == ["Beef Tacos"]
