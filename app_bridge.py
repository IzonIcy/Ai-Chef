"""
Python bridge for AI Chef macOS app
Provides functions that the SwiftUI app can call via subprocess
"""

import json
import sys
import os
from pathlib import Path

# Add project root to path so we can import recipes, ai_generator, meal_planner
sys.path.insert(0, str(Path(__file__).resolve().parent))

from recipes import find_recipes_by_ingredients, RECIPE_DATABASE
from ai_generator import generate_recipe_with_ai, get_cooking_tips
from meal_planner import MealPlanner, SavedRecipes


def find_recipes_by_ingredients_api(ingredients: list) -> dict:
    """
    Find recipes by ingredients
    
    Args:
        ingredients: List of ingredient strings
        
    Returns:
        Dictionary with recipes and metadata
    """
    try:
        recipes = find_recipes_by_ingredients(ingredients)
        return {
            "status": "success",
            "recipes": recipes,
            "count": len(recipes)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "recipes": []
        }


def generate_recipe_api(prompt: str = None, ingredients: list = None, dietary_preference: str = None, 
                        cuisine_type: str = None, cook_time: int = None, difficulty: str = None) -> dict:
    """
    Generate a recipe using AI
    
    Args:
        prompt: Free-form description of desired recipe
        ingredients: List of ingredients to use
        dietary_preference: Dietary restrictions/preferences
        cuisine_type: Desired cuisine style
        cook_time: Maximum cooking time in minutes
        difficulty: Desired difficulty level
        
    Returns:
        Dictionary with generated recipe
    """
    try:
        recipe = generate_recipe_with_ai(
            ingredients=ingredients,
            dietary_preference=dietary_preference,
            cuisine_type=cuisine_type,
            cook_time=cook_time,
            difficulty=difficulty,
            description=prompt
        )
        return {
            "status": "success",
            "recipe": recipe
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "recipe": None
        }


def get_cooking_tips_api(recipe_name: str) -> dict:
    """
    Get cooking tips for a recipe
    
    Args:
        recipe_name: Name of the recipe
        
    Returns:
        Dictionary with tips
    """
    try:
        tips = get_cooking_tips(recipe_name)
        return {
            "status": "success",
            "tips": tips
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "tips": []
        }


def get_all_recipes_api() -> dict:
    """
    Get all available recipes in the database
    
    Returns:
        Dictionary with all recipes
    """
    try:
        return {
            "status": "success",
            "recipes": RECIPE_DATABASE,
            "count": len(RECIPE_DATABASE)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "recipes": []
        }


def main():
    """Handle command line arguments from the macOS app"""
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "No command provided"}))
        return
    
    command = sys.argv[1]
    
    try:
        if command == "find_recipes":
            ingredients = json.loads(sys.argv[2]) if len(sys.argv) > 2 else []
            result = find_recipes_by_ingredients_api(ingredients)
            
        elif command == "generate_recipe":
            prompt = sys.argv[2] if len(sys.argv) > 2 else ""
            result = generate_recipe_api(prompt)
            
        elif command == "get_tips":
            recipe_name = sys.argv[2] if len(sys.argv) > 2 else ""
            result = get_cooking_tips_api(recipe_name)
            
        elif command == "get_all_recipes":
            result = get_all_recipes_api()
            
        else:
            result = {"status": "error", "message": f"Unknown command: {command}"}
        
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))


if __name__ == "__main__":
    main()
