"""
AI-powered recipe generation using OpenAI API Infrastructure.
"""

import base64
import json
import os
import re
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
# Initialize client as None, will be created when needed
client = None

# Modern default; gpt-3.5-turbo is a deprecated legacy model.
DEFAULT_MODEL = 'gpt-4o-mini'


def resolve_settings(api_key=None, base_url=None, model=None):
    """Resolve the key, endpoint and model the client should use.

    ``base_url`` is optional and keeps the default OpenAI endpoint when it is
    unset. Setting it points every call at any OpenAI-compatible server, such as
    a local Ollama. Those servers ignore auth, but the client still refuses to
    start without a key, so a placeholder is supplied only when a base URL is
    configured.

    Raises ValueError when the base URL is not an http(s) URL, so a typo comes
    back as one readable line instead of a traceback from inside the client.
    """
    base = (base_url or '').strip() or None
    if base is not None:
        parsed = urlparse(base)
        if parsed.scheme not in ('http', 'https') or not parsed.netloc:
            raise ValueError(
                'OPENAI_BASE_URL must be an http(s) URL such as '
                f'http://localhost:11434/v1, got {base_url!r}'
            )

    return {
        'api_key': (api_key or '').strip() or ('not-needed' if base else None),
        'base_url': base,
        'model': (model or '').strip() or DEFAULT_MODEL,
    }


def _resolve_from_env():
    """Read the endpoint settings from the environment."""
    return resolve_settings(
        api_key=os.getenv('OPENAI_API_KEY'),
        base_url=os.getenv('OPENAI_BASE_URL'),
        model=os.getenv('OPENAI_MODEL'),
    )


def _get_client():
    """Get or create OpenAI client."""
    global client
    if client is None:
        settings = _resolve_from_env()
        if settings['api_key']:
            if settings['base_url']:
                client = OpenAI(
                    api_key=settings['api_key'],
                    base_url=settings['base_url'],
                    timeout=60.0,
                )
            else:
                client = OpenAI(api_key=settings['api_key'], timeout=60.0)
    return client


def _get_model():
    """Resolve the model to use: OPENAI_MODEL env override, else DEFAULT_MODEL."""
    return _resolve_from_env()['model']


def generate_recipe_with_ai(  # noqa: C901
    ingredients=None,
    dietary_preference=None,
    cuisine_type=None,
    cook_time=None,
    difficulty=None,
    description=None,
):
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
    prompt_parts = ['Create a detailed recipe']

    if description:
        prompt_parts.append(f'for: {description}')

    if ingredients:
        prompt_parts.append(f'using these ingredients: {", ".join(ingredients)}')

    if dietary_preference:
        prompt_parts.append(f'that is {dietary_preference}')

    if cuisine_type:
        prompt_parts.append(f'in {cuisine_type} style')

    if cook_time:
        prompt_parts.append(f'that takes no more than {cook_time} minutes to cook')

    if difficulty:
        prompt_parts.append(f'with {difficulty} difficulty level')

    prompt = ' '.join(prompt_parts) + '.'
    prompt += '\n\nReturn ONLY valid JSON with this exact schema:\n'
    prompt += (
        '{"name": string, "servings": int, "cook_time": int, '
        '"difficulty": "easy|medium|hard", "ingredients": [string], '
        '"instructions": [string], "cuisine": string, "dietary": [string]}'
    )

    try:
        client_instance = _get_client()
        if not client_instance:
            return {
                'error': 'OpenAI client not initialized',
                'suggestion': 'Make sure your OPENAI_API_KEY is set correctly in the .env file',
            }

        last_parse_error = None
        for attempt in range(2):
            response = client_instance.chat.completions.create(
                model=_get_model(),
                messages=[
                    {
                        'role': 'system',
                        'content': (
                            'You are a professional chef who creates delicious, '
                            'easy-to-follow recipes tailored to user preferences. '
                            'Output must be valid JSON only.'
                        ),
                    },
                    {
                        'role': 'user',
                        'content': prompt
                        if attempt == 0
                        else (
                            f'Your previous output was not parseable ({last_parse_error}). '
                            f'Return only valid JSON in the exact schema.'
                        ),
                    },
                ],
                temperature=0.7,
                max_tokens=1500,
            )

            recipe_text = (response.choices[0].message.content or '').strip()
            parsed = parse_ai_recipe(recipe_text)
            if 'error' not in parsed:
                return parsed

            last_parse_error = parsed.get('error', 'Unknown parsing error')

        return {
            'error': f'Failed to parse recipe response: {last_parse_error}',
            'suggestion': 'Try being more specific with ingredients, cuisine, and cooking time.',
        }

    except Exception as e:  # noqa: BLE001 - surface any API error to the user
        return {
            'error': f'Failed to generate recipe: {e!s}',
            'suggestion': 'Make sure your OPENAI_API_KEY is set correctly in the .env file',
        }


def parse_ai_recipe(recipe_text):  # noqa: C901
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
    ingredients: list[str] = []
    instructions: list[str] = []
    recipe = {
        'name': '',
        'servings': 2,
        'cook_time': 30,
        'difficulty': 'medium',
        'ingredients': ingredients,
        'instructions': instructions,
        'cuisine': 'Custom',
        'dietary': [],
    }

    current_section = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith('Recipe Name:'):
            recipe['name'] = line.replace('Recipe Name:', '').strip()
        elif line.startswith('Servings:'):
            recipe['servings'] = line.replace('Servings:', '').strip()
        elif line.startswith('Cook Time:'):
            recipe['cook_time'] = line.replace('Cook Time:', '').strip()
        elif line.startswith('Difficulty:'):
            recipe['difficulty'] = line.replace('Difficulty:', '').strip()
        elif line.startswith('Ingredients:'):
            current_section = 'ingredients'
        elif line.startswith('Instructions:'):
            current_section = 'instructions'
        elif current_section == 'ingredients' and line.startswith(('-', '•')):
            ingredient = line[1:].strip()
            if ingredient:
                ingredients.append(ingredient)
        elif current_section == 'instructions' and line and line[0].isdigit():
            # Remove the number and period at the start
            instruction = line.split('.', 1)[1].strip() if '.' in line else line
            if instruction:
                instructions.append(instruction)

    return _normalize_recipe(recipe)


def _try_parse_json_recipe(recipe_text):
    """Try to parse strict JSON recipe from model output."""
    if not recipe_text:
        return None

    try:
        return json.loads(recipe_text)
    except json.JSONDecodeError:
        pass

    json_match = re.search(r'\{[\s\S]*\}', recipe_text)
    if not json_match:
        return None

    try:
        return json.loads(json_match.group(0))
    except json.JSONDecodeError:
        return None


def _normalize_recipe(recipe):
    """Normalize and validate parsed recipe content."""
    normalized = {
        'name': str(recipe.get('name') or recipe.get('recipe_name') or 'AI Recipe').strip(),
        'servings': _safe_int(recipe.get('servings'), default=2),
        'cook_time': _safe_int(recipe.get('cook_time'), default=30),
        'difficulty': str(recipe.get('difficulty') or 'medium').strip().lower(),
        'ingredients': _normalize_list_field(recipe.get('ingredients')),
        'instructions': _normalize_list_field(recipe.get('instructions')),
        'cuisine': str(recipe.get('cuisine') or 'Custom').strip(),
        'dietary': _normalize_list_field(recipe.get('dietary')),
    }

    if normalized['difficulty'] not in {'easy', 'medium', 'hard'}:
        normalized['difficulty'] = 'medium'

    if not normalized['ingredients'] or not normalized['instructions']:
        return {
            'error': 'Incomplete AI recipe output',
            'suggestion': 'The model response missed ingredients or instructions. Please retry.',
        }

    return normalized


def _normalize_list_field(value):
    """Normalize ingredient/instruction style fields into list[str]."""
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        parts = [segment.strip(' -•\t') for segment in value.split('\n')]
        return [segment for segment in parts if segment]
    return []


def _safe_int(value, default=0):
    """Extract integer value from mixed input."""
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        match = re.search(r'\d+', value)
        if match:
            return int(match.group(0))
    return default


SUPPORTED_IMAGE_TYPES = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.webp': 'image/webp',
}

NO_ENDPOINT_MESSAGE = 'No AI endpoint set. Set OPENAI_API_KEY or OPENAI_BASE_URL (for Ollama).'

PHOTO_PROMPT = (
    'List the food ingredients you can see in this photo of a fridge shelf or a counter. '
    'Reply with one line of comma-separated ingredient names, lowercase, no quantities, '
    'no brands, no commentary. Reply with exactly "none" if you see no food.'
)

_BULLET_PREFIX = re.compile(r'^\s*(?:[-*•]|\d+[.)])\s*')
_INGREDIENT_LABEL = re.compile(r'^\s*ingredients?\s*:\s*', re.IGNORECASE)
_EMPTY_ANSWERS = {'none', 'nothing', 'n/a', 'no ingredients', 'none visible'}


def extract_ingredients_from_photo(image_path, model=None):
    """Read the food ingredients visible in an image.

    Returns ``{'ingredients': [...]}`` on success and ``{'error': ...}`` for a
    file that cannot be used or an endpoint that answers with nothing usable.
    Nothing raises at the caller, so the CLI can print one line and exit.
    """
    path = Path(image_path)
    mime_type = SUPPORTED_IMAGE_TYPES.get(path.suffix.lower(), 'image/jpeg')
    image_bytes = path.read_bytes()

    client_instance = _get_client()
    if not client_instance:
        return {'error': NO_ENDPOINT_MESSAGE}

    encoded = base64.b64encode(image_bytes).decode('ascii')
    response = client_instance.chat.completions.create(
        model=model or _get_model(),
        messages=[
            {
                'role': 'system',
                'content': 'You identify food ingredients in photos. Reply with the list only.',
            },
            {
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': PHOTO_PROMPT},
                    {
                        'type': 'image_url',
                        'image_url': {'url': f'data:{mime_type};base64,{encoded}'},
                    },
                ],
            },
        ],
        temperature=0.2,
        max_tokens=300,
    )

    reply = response.choices[0].message.content or ''
    return {'ingredients': parse_ingredient_list(reply)}


def parse_ingredient_list(text):
    """Parse bare ingredient names out of a model's reply.

    Model output is untrusted, so this accepts a JSON list, a bulleted list, or
    a comma list wrapped in prose, then keeps only short lowercase names that
    can match a recipe ingredient.
    """
    if not text or not text.strip():
        return []

    items = _try_parse_json_ingredients(text)
    if items is None:
        items = []
        for line in text.strip().splitlines():
            line = _BULLET_PREFIX.sub('', line.strip())
            line = _INGREDIENT_LABEL.sub('', line)
            items.extend(line.split(','))

    ingredients: list[str] = []
    for item in items:
        name = str(item).strip().strip('`\'"').strip().lower()
        if name.startswith(('and ', 'or ')):
            name = name.split(' ', 1)[1].strip()
        if not name or name in _EMPTY_ANSWERS or len(name.split()) > 4:
            continue
        if name.endswith(('.', ':', '!', '?')):
            continue
        if name not in ingredients:
            ingredients.append(name)
    return ingredients


def _try_parse_json_ingredients(text):
    """Return a list from JSON model output, or None when there is no JSON."""
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r'\[[\s\S]*\]', text)
        if not match:
            return None
        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError:
            return None

    if isinstance(parsed, dict):
        parsed = parsed.get('ingredients')
        return parsed if isinstance(parsed, list) else []
    return parsed if isinstance(parsed, list) else None


def get_cooking_tips(recipe_name, dietary_preferences=None):
    """
    Get AI-generated cooking tips for a specific recipe.

    Args:
        recipe_name (str): Name of the recipe
        dietary_preferences (str): Any dietary preferences to consider

    Returns:
        str: Cooking tips and suggestions
    """
    prompt = f'Provide 3-5 helpful cooking tips for making {recipe_name}'
    if dietary_preferences:
        prompt += f' with {dietary_preferences} modifications'

    try:
        client_instance = _get_client()
        if not client_instance:
            return 'Unable to generate tips: OpenAI API key not set'

        response = client_instance.chat.completions.create(
            model=_get_model(),
            messages=[
                {
                    'role': 'system',
                    'content': 'You are a helpful cooking assistant providing practical tips.',
                },
                {'role': 'user', 'content': prompt},
            ],
            temperature=0.7,
            max_tokens=300,
        )

        return response.choices[0].message.content

    except Exception as e:  # noqa: BLE001 - surface any API error to the user
        return f'Unable to generate tips: {e!s}'


def suggest_substitutions(ingredient):
    """
    Suggest ingredient substitutions using AI.

    Args:
        ingredient (str): Ingredient to find substitutions for

    Returns:
        str: List of possible substitutions
    """
    prompt = (
        f'What are good substitutions for {ingredient} in cooking? '
        f'Provide 3-4 options with brief explanations.'
    )

    try:
        client_instance = _get_client()
        if not client_instance:
            return 'Unable to suggest substitutions: OpenAI API key not set'

        response = client_instance.chat.completions.create(
            model=_get_model(),
            messages=[
                {
                    'role': 'system',
                    'content': (
                        'You are a knowledgeable chef helping with ingredient substitutions.'
                    ),
                },
                {'role': 'user', 'content': prompt},
            ],
            temperature=0.7,
            max_tokens=200,
        )

        return response.choices[0].message.content

    except Exception as e:  # noqa: BLE001 - surface any API error to the user
        return f'Unable to suggest substitutions: {e!s}'
