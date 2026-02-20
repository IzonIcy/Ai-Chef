"""
Meal planning and grocery list generation
"""

import json
import os
import re
from datetime import datetime
from recipes import RECIPE_DATABASE, filter_recipes


def _normalize_ingredient_name(ingredient):
    """Normalize ingredient text for grouping and matching."""
    cleaned = ingredient.strip().lower()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def _to_title_case(text):
    return " ".join(word.capitalize() for word in text.split())


class MealPlanner:
    """Handle meal planning and grocery list generation."""
    
    def __init__(self, filename="meal_plans.json"):
        self.filename = filename
        self.meal_plan = self.load_meal_plan()
    
    def load_meal_plan(self):
        """Load existing meal plan from file."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def save_meal_plan(self):
        """Save meal plan to file."""
        with open(self.filename, 'w') as f:
            json.dump(self.meal_plan, f, indent=2)
    
    def create_weekly_plan(self, dietary_preference=None, max_cook_time=None):
        """
        Create a balanced weekly meal plan.
        
        Args:
            dietary_preference (str): Dietary restriction to consider
            max_cook_time (int): Maximum cooking time per meal
            
        Returns:
            dict: Weekly meal plan with recipes for each day
        """
        # Filter recipes based on preferences
        available_recipes = filter_recipes(
            cook_time=max_cook_time,
            dietary=dietary_preference
        )
        
        if len(available_recipes) < 7:
            available_recipes = RECIPE_DATABASE  # Fall back to all recipes
        
        # Create a balanced plan - try to vary cuisines
        week_plan = {}
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        used_recipes = set()
        
        for day in days:
            # Try to pick recipes with different cuisines
            available_for_day = [r for r in available_recipes if r["name"] not in used_recipes]
            
            if not available_for_day:
                available_for_day = available_recipes  # Reset if we run out
                used_recipes.clear()
            
            # Pick a recipe
            recipe = available_for_day[len(used_recipes) % len(available_for_day)]
            week_plan[day] = {
                "recipe": recipe["name"],
                "cook_time": recipe["cook_time"],
                "servings": recipe["servings"]
            }
            used_recipes.add(recipe["name"])
        
        # Save the plan
        plan_date = datetime.now().strftime("%Y-%m-%d")
        self.meal_plan[plan_date] = week_plan
        self.save_meal_plan()
        
        return week_plan
    
    def add_meal_to_plan(self, day, recipe_name):
        """Add a specific meal to a specific day."""
        plan_date = datetime.now().strftime("%Y-%m-%d")
        if plan_date not in self.meal_plan:
            self.meal_plan[plan_date] = {}
        
        # Find the recipe
        recipe = None
        for r in RECIPE_DATABASE:
            if r["name"].lower() == recipe_name.lower():
                recipe = r
                break
        
        if recipe:
            self.meal_plan[plan_date][day] = {
                "recipe": recipe["name"],
                "cook_time": recipe["cook_time"],
                "servings": recipe["servings"]
            }
            self.save_meal_plan()
            return True
        return False
    
    def get_current_plan(self):
        """Get the current week's meal plan."""
        plan_date = datetime.now().strftime("%Y-%m-%d")
        return self.meal_plan.get(plan_date, {})
    
    def generate_grocery_list(self, week_plan=None):
        """
        Generate a grocery list from the meal plan.
        
        Args:
            week_plan (dict): Meal plan to generate list from
            
        Returns:
            dict: Organized grocery list by category
        """
        if week_plan is None:
            week_plan = self.get_current_plan()
        
        if not week_plan:
            return {}
        
        # Collect and count all ingredients across planned meals
        ingredient_counts = {}
        for day, meal_info in week_plan.items():
            recipe_name = meal_info["recipe"]
            # Find the recipe in database
            for recipe in RECIPE_DATABASE:
                if recipe["name"] == recipe_name:
                    for ingredient in recipe["ingredients"]:
                        key = _normalize_ingredient_name(ingredient)
                        if key not in ingredient_counts:
                            ingredient_counts[key] = {
                                "item": _to_title_case(key),
                                "quantity": 0,
                                "unit": "recipe-use"
                            }
                        ingredient_counts[key]["quantity"] += 1
                    break
        
        # Categorize ingredients (simple categorization)
        categories = {
            "Proteins": ["chicken", "beef", "salmon", "shrimp", "ground beef", "chickpeas"],
            "Vegetables": ["broccoli", "bell pepper", "zucchini", "tomato", "lettuce", "onion", 
                          "kale", "sweet potato", "tomatoes", "romaine lettuce", "avocado"],
            "Grains & Pasta": ["rice", "pasta", "tortillas"],
            "Dairy": ["cheese", "butter", "cream", "sour cream", "parmesan"],
            "Pantry": ["soy sauce", "garlic", "ginger", "oil", "olive oil", "taco seasoning",
                      "chicken broth", "vegetable broth", "tahini", "caesar dressing"],
            "Herbs & Seasonings": ["thyme", "basil", "parsley"],
            "Other": []
        }
        
        grocery_list = {cat: [] for cat in categories.keys()}
        
        for normalized_ingredient, ingredient_data in ingredient_counts.items():
            categorized = False
            for category, items in categories.items():
                if category != "Other" and normalized_ingredient in items:
                    grocery_list[category].append(ingredient_data)
                    categorized = True
                    break
            if not categorized:
                grocery_list["Other"].append(ingredient_data)
        
        # Remove empty categories
        grocery_list = {k: v for k, v in grocery_list.items() if v}
        
        return grocery_list


class PantryManager:
    """Manage pantry inventory with quantities and expiry dates."""

    def __init__(self, filename="pantry_inventory.json"):
        self.filename = filename
        self.items = self.load_items()

    def load_items(self):
        """Load pantry items from file."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def save_items(self):
        """Save pantry items to file."""
        with open(self.filename, 'w') as f:
            json.dump(self.items, f, indent=2)

    def add_item(self, name, quantity=1, unit="item", expires_on=None):
        """Add or update a pantry item."""
        normalized_name = _normalize_ingredient_name(name)
        for item in self.items:
            if _normalize_ingredient_name(item.get("name", "")) == normalized_name:
                item["quantity"] = item.get("quantity", 0) + quantity
                item["unit"] = unit or item.get("unit", "item")
                if expires_on:
                    item["expires_on"] = expires_on
                self.save_items()
                return True

        self.items.append({
            "name": _to_title_case(normalized_name),
            "quantity": quantity,
            "unit": unit or "item",
            "expires_on": expires_on,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        self.save_items()
        return True

    def remove_item(self, name):
        """Remove a pantry item by name."""
        normalized_name = _normalize_ingredient_name(name)
        before = len(self.items)
        self.items = [
            item for item in self.items
            if _normalize_ingredient_name(item.get("name", "")) != normalized_name
        ]
        changed = len(self.items) < before
        if changed:
            self.save_items()
        return changed

    def get_all_items(self):
        """Return pantry items."""
        return self.items

    def get_pantry_ingredients(self):
        """Return normalized pantry ingredient names for matching."""
        return [_normalize_ingredient_name(item.get("name", "")) for item in self.items]

    def get_expiring_items(self, within_days=3):
        """Return pantry items that expire within N days."""
        expiring = []
        today = datetime.now().date()
        for item in self.items:
            expires_on = item.get("expires_on")
            if not expires_on:
                continue
            try:
                expires_date = datetime.strptime(expires_on, "%Y-%m-%d").date()
            except ValueError:
                continue

            days_left = (expires_date - today).days
            if days_left <= within_days:
                item_with_days = dict(item)
                item_with_days["days_left"] = days_left
                expiring.append(item_with_days)

        expiring.sort(key=lambda entry: entry.get("days_left", 9999))
        return expiring


class SavedRecipes:
    """Manage user's saved favorite recipes."""
    
    def __init__(self, filename="saved_recipes.json"):
        self.filename = filename
        self.saved = self.load_saved()
    
    def load_saved(self):
        """Load saved recipes from file."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    def save_to_file(self):
        """Save recipes to file."""
        with open(self.filename, 'w') as f:
            json.dump(self.saved, f, indent=2)
    
    def add_recipe(self, recipe):
        """Add a recipe to saved favorites."""
        # Check if already saved
        for saved_recipe in self.saved:
            if saved_recipe.get("name") == recipe.get("name"):
                return False  # Already saved
        
        # Add timestamp
        recipe["saved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.saved.append(recipe)
        self.save_to_file()
        return True
    
    def remove_recipe(self, recipe_name):
        """Remove a recipe from saved favorites."""
        initial_length = len(self.saved)
        self.saved = [r for r in self.saved if r.get("name") != recipe_name]
        
        if len(self.saved) < initial_length:
            self.save_to_file()
            return True
        return False
    
    def get_all_saved(self):
        """Get all saved recipes."""
        return self.saved
    
    def search_saved(self, query):
        """Search saved recipes by name."""
        query_lower = query.lower()
        return [r for r in self.saved if query_lower in r.get("name", "").lower()]
