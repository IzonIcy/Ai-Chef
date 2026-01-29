"""
AI-powered recipe generation using OpenAI API
"""

import os
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
    prompt += "\n\nProvide the recipe in the following format:\n"
    prompt += "Recipe Name: [name]\n"
    prompt += "Servings: [number]\n"
    prompt += "Cook Time: [minutes]\n"
    prompt += "Difficulty: [easy/medium/hard]\n"
    prompt += "Ingredients:\n- [ingredient 1]\n- [ingredient 2]\n...\n"
    prompt += "Instructions:\n1. [step 1]\n2. [step 2]\n..."
    
    try:
        client_instance = _get_client()
        if not client_instance:
            return {
                "error": "OpenAI client not initialized",
                "suggestion": "Make sure your OPENAI_API_KEY is set correctly in the .env file"
            }
        
        response = client_instance.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional chef who creates delicious, easy-to-follow recipes tailored to user preferences."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=1000
        )
        
        recipe_text = response.choices[0].message.content
        return parse_ai_recipe(recipe_text)
    
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
    lines = recipe_text.strip().split('\n')
    recipe = {
        "name": "",
        "servings": "",
        "cook_time": "",
        "difficulty": "",
        "ingredients": [],
        "instructions": []
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
        elif current_section == "instructions" and line[0].isdigit():
            # Remove the number and period at the start
            instruction = line.split(".", 1)[1].strip() if "." in line else line
            if instruction:
                recipe["instructions"].append(instruction)
    
    return recipe


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
