"""
Meal planning and grocery list generation
"""

import json
import os
from datetime import datetime, timedelta
from recipes import RECIPE_DATABASE, filter_recipes


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
        
        # Collect all ingredients
        all_ingredients = []
        for day, meal_info in week_plan.items():
            recipe_name = meal_info["recipe"]
            # Find the recipe in database
            for recipe in RECIPE_DATABASE:
                if recipe["name"] == recipe_name:
                    all_ingredients.extend(recipe["ingredients"])
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
        
        for ingredient in set(all_ingredients):  # Remove duplicates
            categorized = False
            for category, items in categories.items():
                if category != "Other" and ingredient.lower() in items:
                    grocery_list[category].append(ingredient)
                    categorized = True
                    break
            if not categorized:
                grocery_list["Other"].append(ingredient)
        
        # Remove empty categories
        grocery_list = {k: v for k, v in grocery_list.items() if v}
        
        return grocery_list


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
