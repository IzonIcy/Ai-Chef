"""
AI-powered recipe generation using OpenAI API Infrastructure.
"""

import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# Initialize client as None, will be created when needed
client = None


def _get_client():
    """Get or create OpenAI client."""
    global client
    if client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            client = OpenAI(api_key=api_key)
    return client


def generate_recipe_with_ai(ingredients=None, dietary_preference=None, cuisine_type=None, 
                           cook_time=None, difficulty=None, description=None):
    """
    Generate a custom recipe using AI based on user preferences.
    
    Args:
        ingredients (list): List of ingredients to use
        dietary_preference (str): Dietary restrictions (vegetarian, vegan, etc.)
        cuisine_type (str): Desired cuisine type
        cook_time (int): Maximum cooking time in minutes
        difficulty (str): Difficulty level
        description (str): Free-form description of what user wants
        
    Returns:
        dict: Generated recipe with name, ingredients, and instructions
    """
    # Build the prompt based on provided parameters
    prompt_parts = ["Create a detailed recipe"]
    
    if description:
        prompt_parts.append(f"for: {description}")
    
    if ingredients:
        prompt_parts.append(f"using these ingredients: {', '.join(ingredients)}")
    
    if dietary_preference:
        prompt_parts.append(f"that is {dietary_preference}")
    
    if cuisine_type:
        prompt_parts.append(f"in {cuisine_type} style")
    
    if cook_time:
        prompt_parts.append(f"that takes no more than {cook_time} minutes to cook")
    
    if difficulty:
        prompt_parts.append(f"with {difficulty} difficulty level")
    
    prompt = " ".join(prompt_parts) + "."
    prompt += "\n\nReturn ONLY valid JSON with this exact schema:\n"
    prompt += "{\"name\": string, \"servings\": int, \"cook_time\": int, \"difficulty\": \"easy|medium|hard\", \"ingredients\": [string], \"instructions\": [string], \"cuisine\": string, \"dietary\": [string]}"
    
    try:
        client_instance = _get_client()
        if not client_instance:
            return {
                "error": "OpenAI client not initialized",
                "suggestion": "Make sure your OPENAI_API_KEY is set correctly in the .env file"
            }
        
        last_parse_error = None
        for attempt in range(2):
            response = client_instance.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional chef who creates delicious, easy-to-follow recipes tailored to user preferences. Output must be valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt if attempt == 0 else f"Your previous output was not parseable ({last_parse_error}). Return only valid JSON in the exact schema."
                    }
                ],
                temperature=0.7,
                max_tokens=1500
            )

            recipe_text = (response.choices[0].message.content or "").strip()
            parsed = parse_ai_recipe(recipe_text)
            if "error" not in parsed:
                return parsed

            last_parse_error = parsed.get("error", "Unknown parsing error")

        return {
            "error": f"Failed to parse recipe response: {last_parse_error}",
            "suggestion": "Try being more specific with ingredients, cuisine, and cooking time."
        }
    
    except Exception as e:
        return {
            "error": f"Failed to generate recipe: {str(e)}",
            "suggestion": "Make sure your OPENAI_API_KEY is set correctly in the .env file"
        }


def parse_ai_recipe(recipe_text):
    """
    Parse the AI-generated recipe text into structured format.
    
    Args:
        recipe_text (str): Raw text from AI
        
    Returns:
        dict: Structured recipe data
    """
    parsed_json = _try_parse_json_recipe(recipe_text)
    if parsed_json:
        return _normalize_recipe(parsed_json)

    lines = recipe_text.strip().split('\n')
    recipe = {
        "name": "",
        "servings": 2,
        "cook_time": 30,
        "difficulty": "medium",
        "ingredients": [],
        "instructions": [],
        "cuisine": "Custom",
        "dietary": []
    }
    
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith("Recipe Name:"):
            recipe["name"] = line.replace("Recipe Name:", "").strip()
        elif line.startswith("Servings:"):
            recipe["servings"] = line.replace("Servings:", "").strip()
        elif line.startswith("Cook Time:"):
            recipe["cook_time"] = line.replace("Cook Time:", "").strip()
        elif line.startswith("Difficulty:"):
            recipe["difficulty"] = line.replace("Difficulty:", "").strip()
        elif line.startswith("Ingredients:"):
            current_section = "ingredients"
        elif line.startswith("Instructions:"):
            current_section = "instructions"
        elif current_section == "ingredients" and (line.startswith("-") or line.startswith("•")):
            ingredient = line[1:].strip()
            if ingredient:
                recipe["ingredients"].append(ingredient)
        elif current_section == "instructions" and line and line[0].isdigit():
            # Remove the number and period at the start
            instruction = line.split(".", 1)[1].strip() if "." in line else line
            if instruction:
                recipe["instructions"].append(instruction)

    return _normalize_recipe(recipe)


def _try_parse_json_recipe(recipe_text):
    """Try to parse strict JSON recipe from model output."""
    if not recipe_text:
        return None

    try:
        return json.loads(recipe_text)
    except json.JSONDecodeError:
        pass

    json_match = re.search(r"\{[\s\S]*\}", recipe_text)
    if not json_match:
        return None

    try:
        return json.loads(json_match.group(0))
    except json.JSONDecodeError:
        return None


def _normalize_recipe(recipe):
    """Normalize and validate parsed recipe content."""
    normalized = {
        "name": str(recipe.get("name") or recipe.get("recipe_name") or "AI Recipe").strip(),
        "servings": _safe_int(recipe.get("servings"), default=2),
        "cook_time": _safe_int(recipe.get("cook_time"), default=30),
        "difficulty": str(recipe.get("difficulty") or "medium").strip().lower(),
        "ingredients": _normalize_list_field(recipe.get("ingredients")),
        "instructions": _normalize_list_field(recipe.get("instructions")),
        "cuisine": str(recipe.get("cuisine") or "Custom").strip(),
        "dietary": _normalize_list_field(recipe.get("dietary"))
    }

    if normalized["difficulty"] not in {"easy", "medium", "hard"}:
        normalized["difficulty"] = "medium"

    if not normalized["ingredients"] or not normalized["instructions"]:
        return {
            "error": "Incomplete AI recipe output",
            "suggestion": "The model response missed ingredients or instructions. Please retry."
        }

    return normalized


def _normalize_list_field(value):
    """Normalize ingredient/instruction style fields into list[str]."""
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        parts = [segment.strip(" -•\t") for segment in value.split("\n")]
        return [segment for segment in parts if segment]
    return []


def _safe_int(value, default=0):
    """Extract integer value from mixed input."""
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        match = re.search(r"\d+", value)
        if match:
            return int(match.group(0))
    return default


def get_cooking_tips(recipe_name, dietary_preferences=None):
    """
    Get AI-generated cooking tips for a specific recipe.
    
    Args:
        recipe_name (str): Name of the recipe
        dietary_preferences (str): Any dietary preferences to consider
        
    Returns:
        str: Cooking tips and suggestions
    """
    prompt = f"Provide 3-5 helpful cooking tips for making {recipe_name}"
    if dietary_preferences:
        prompt += f" with {dietary_preferences} modifications"
    
    try:
        client_instance = _get_client()
        if not client_instance:
            return "Unable to generate tips: OpenAI API key not set"
        
        response = client_instance.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful cooking assistant providing practical tips."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Unable to generate tips: {str(e)}"


def suggest_substitutions(ingredient):
    """
    Suggest ingredient substitutions using AI.
    
    Args:
        ingredient (str): Ingredient to find substitutions for
        
    Returns:
        str: List of possible substitutions
    """
    prompt = f"What are good substitutions for {ingredient} in cooking? Provide 3-4 options with brief explanations."
    
    try:
        client_instance = _get_client()
        if not client_instance:
            return "Unable to suggest substitutions: OpenAI API key not set"
        
        response = client_instance.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a knowledgeable chef helping with ingredient substitutions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Unable to suggest substitutions: {str(e)}"
