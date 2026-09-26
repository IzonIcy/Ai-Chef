"""
Recipe database with ingredient-based search functionality
"""

import re

from data_dir import get_data_dir
from json_store import load_json, save_json_atomic


def _user_recipes_path():
    return get_data_dir() / 'user_recipes.json'


def load_user_recipes():
    """Load user-defined recipes from the data directory."""
    path = _user_recipes_path()
    data = load_json(path, [])
    if not isinstance(data, list):
        return []
    return [recipe for recipe in data if isinstance(recipe, dict)]


def save_user_recipes(recipes):
    """Persist user-defined recipes to the data directory."""
    save_json_atomic(_user_recipes_path(), recipes)


def add_user_recipe(recipe):
    """Add a user recipe, rejecting duplicate names. Returns True on success."""
    name = (recipe.get('name') or '').strip().lower()
    if not name:
        raise ValueError('recipe must have a name')
    for existing in load_user_recipes():
        if existing.get('name', '').strip().lower() == name:
            return False
    recipes = load_user_recipes()
    recipes.append(recipe)
    save_user_recipes(recipes)
    return True


def remove_user_recipe(name):
    """Remove a user recipe by exact name. Returns True if removed."""
    recipes = load_user_recipes()
    remaining = [r for r in recipes if r.get('name', '').strip().lower() != name.strip().lower()]
    if len(remaining) == len(recipes):
        return False
    save_user_recipes(remaining)
    return True


def all_recipes():
    """Built-in recipes plus any user-defined ones."""
    return RECIPE_DATABASE + load_user_recipes()


_LEADING_AMOUNT_RE = re.compile(r'^(\d+(?:\.\d+)?)(?:\s*/\s*(\d+))?(?=\s|$)')


def _format_amount(value):
    rounded = round(value, 2)
    if abs(rounded - round(rounded)) < 1e-9:
        return str(round(rounded))
    return f'{rounded:g}'


# Units we know how to singularise. An explicit map rather than a "drop the
# trailing s" rule, which would turn "pint" into "pin" and "couscous" into
# "couscou". Anything not listed is passed through untouched.
_PLURAL_UNITS = {
    'bunches': 'bunch',
    'cans': 'can',
    'cloves': 'clove',
    'cups': 'cup',
    'eggs': 'egg',
    'fillets': 'fillet',
    'handfuls': 'handful',
    'heads': 'head',
    'lbs': 'lb',
    'slices': 'slice',
    'sprigs': 'sprig',
    'tortillas': 'tortilla',
}


def _render_quantity(amount, unit_text):
    """Render an amount with its unit, singularised when the count is one.

    "4 cups" at half scale is "2 cups", but "2 cups" at quarter scale is
    "1 cup" rather than "1 cups".
    """
    number = _format_amount(amount)
    unit_text = unit_text.strip()
    if number == '1' and unit_text:
        head, _, tail = unit_text.partition(' ')
        singular = _PLURAL_UNITS.get(head.lower())
        if singular:
            unit_text = f'{singular} {tail}'.strip() if tail else singular
    return f'{number} {unit_text}'.strip() if unit_text else number


def scale_recipe(recipe, factor):
    """Return a copy of the recipe scaled by ``factor``.

    Servings are multiplied. Quantities are scaled too, taken from the recipe's
    ``amounts`` sidecar when present (the built-in recipes use one so that
    ``ingredients`` can stay bare names for matching) and otherwise parsed from
    a leading amount in the ingredient string itself ("2 cups rice").

    The returned ``ingredients`` are display strings such as "3 lbs chicken".
    """
    factor = float(factor)
    if factor <= 0:
        raise ValueError('scale factor must be positive')

    scaled = dict(recipe)
    servings = recipe.get('servings', 1)
    try:
        scaled['servings'] = max(1, round(float(servings) * factor))
    except (TypeError, ValueError):
        scaled['servings'] = servings

    amounts = recipe.get('amounts') or {}

    def scale_quantity(quantity):
        """Scale the leading number of a quantity string, keeping the unit."""
        match = _LEADING_AMOUNT_RE.match(quantity.strip())
        if not match:
            return quantity
        amount = float(match.group(1))
        denominator = match.group(2)
        if denominator:
            amount /= float(denominator)
        rest = quantity.strip()[match.end() :].strip()
        return _render_quantity(amount * factor, rest)

    def render(ingredient):
        quantity = amounts.get(ingredient)
        if quantity is not None:
            return f'{scale_quantity(quantity)} {ingredient}'.strip()
        # No sidecar: fall back to a leading amount in the string itself.
        match = _LEADING_AMOUNT_RE.match(ingredient.strip())
        if not match:
            return ingredient
        amount = float(match.group(1))
        denominator = match.group(2)
        if denominator:
            amount /= float(denominator)
        rest = ingredient.strip()[match.end() :].strip()
        return _render_quantity(amount * factor, rest)

    scaled['ingredients'] = [render(i) for i in recipe.get('ingredients', [])]
    return scaled


RECIPE_DATABASE = [
    {
        'name': 'Chicken Stir-Fry with Broccoli',
        'ingredients': ['chicken', 'broccoli', 'soy sauce', 'garlic', 'ginger', 'oil'],
        'amounts': {
            'chicken': '1.5 lbs',
            'broccoli': '2 cups',
            'soy sauce': '3 tbsp',
            'garlic': '3 cloves',
            'ginger': '1 tbsp',
            'oil': '2 tbsp',
        },
        'cook_time': 20,
        'difficulty': 'easy',
        'cuisine': 'Asian',
        'dietary': ['gluten-free-option'],
        'servings': 4,
        'instructions': [
            'Cut chicken into bite-sized pieces',
            'Heat oil in a large wok or pan over high heat',
            'Add minced garlic and ginger, stir for 30 seconds',
            'Add chicken and cook until golden brown, about 5-7 minutes',
            'Add broccoli florets and stir-fry for 3-4 minutes',
            'Add soy sauce and toss everything together',
            'Serve hot over rice',
        ],
    },
    {
        'name': 'Garlic Chicken and Rice',
        'ingredients': [
            'chicken',
            'rice',
            'garlic',
            'butter',
            'chicken broth',
            'thyme',
        ],
        'amounts': {
            'chicken': '4 breasts',
            'rice': '1.5 cups',
            'garlic': '4 cloves',
            'butter': '2 tbsp',
            'chicken broth': '3 cups',
            'thyme': '2 sprigs',
        },
        'cook_time': 35,
        'difficulty': 'easy',
        'cuisine': 'American',
        'dietary': ['gluten-free'],
        'servings': 4,
        'instructions': [
            'Season chicken breasts with salt and pepper',
            'Melt butter in a large skillet over medium-high heat',
            'Add chicken and cook until golden, 4-5 minutes per side',
            'Remove chicken and set aside',
            'In the same pan, add minced garlic and rice, toast for 1 minute',
            'Add chicken broth and thyme, bring to a boil',
            'Return chicken to pan, cover and simmer for 20 minutes',
            'Let rest 5 minutes before serving',
        ],
    },
    {
        'name': 'One-Pan Chicken Broccoli Rice',
        'ingredients': [
            'chicken',
            'rice',
            'broccoli',
            'onion',
            'garlic',
            'chicken broth',
            'cheese',
        ],
        'amounts': {
            'chicken': '1.5 lbs',
            'rice': '2 cups',
            'broccoli': '3 cups',
            'onion': '1',
            'garlic': '4 cloves',
            'chicken broth': '4 cups',
            'cheese': '1 cup',
        },
        'cook_time': 40,
        'difficulty': 'easy',
        'cuisine': 'American',
        'dietary': ['gluten-free'],
        'servings': 6,
        'instructions': [
            'Preheat oven to 375°F (190°C)',
            'In a large oven-safe pan, combine rice, chicken broth, diced chicken, and diced onion',
            'Add minced garlic and season with salt and pepper',
            'Cover tightly with foil and bake for 25 minutes',
            'Remove from oven, add broccoli florets, cover and bake for another 10 minutes',
            'Sprinkle cheese on top and return to oven uncovered for 5 minutes',
            'Let stand for 5 minutes before serving',
        ],
    },
    {
        'name': 'Vegetarian Pasta Primavera',
        'ingredients': [
            'pasta',
            'broccoli',
            'bell pepper',
            'zucchini',
            'garlic',
            'olive oil',
            'parmesan',
        ],
        'amounts': {
            'pasta': '12 oz',
            'broccoli': '2 cups',
            'bell pepper': '2',
            'zucchini': '2',
            'garlic': '3 cloves',
            'olive oil': '3 tbsp',
            'parmesan': '0.5 cup',
        },
        'cook_time': 25,
        'difficulty': 'easy',
        'cuisine': 'Italian',
        'dietary': ['vegetarian'],
        'servings': 4,
        'instructions': [
            'Cook pasta according to package directions',
            'Meanwhile, heat olive oil in a large pan',
            'Add garlic and sauté for 1 minute',
            'Add broccoli, bell pepper, and zucchini, cook for 5-7 minutes',
            'Drain pasta and add to vegetables',
            'Toss everything together with parmesan cheese',
            'Season with salt, pepper, and red pepper flakes',
        ],
    },
    {
        'name': 'Beef Tacos',
        'ingredients': [
            'ground beef',
            'taco seasoning',
            'tortillas',
            'lettuce',
            'tomato',
            'cheese',
            'sour cream',
        ],
        'amounts': {
            'ground beef': '1 lb',
            'taco seasoning': '3 tbsp',
            'tortillas': '8',
            'lettuce': '2 cups',
            'tomato': '2',
            'cheese': '1 cup',
            'sour cream': '0.5 cup',
        },
        'cook_time': 20,
        'difficulty': 'easy',
        'cuisine': 'Mexican',
        'dietary': [],
        'servings': 4,
        'instructions': [
            'Brown ground beef in a large skillet over medium-high heat',
            'Drain excess fat',
            'Add taco seasoning and water according to package directions',
            'Simmer for 5 minutes until thickened',
            'Warm tortillas in microwave or on stovetop',
            'Assemble tacos with beef and your favorite toppings',
            'Serve with sour cream on the side',
        ],
    },
    {
        'name': 'Salmon with Roasted Vegetables',
        'ingredients': [
            'salmon',
            'broccoli',
            'bell pepper',
            'olive oil',
            'lemon',
            'garlic',
        ],
        'amounts': {
            'salmon': '2 fillets',
            'broccoli': '3 cups',
            'bell pepper': '2',
            'olive oil': '2 tbsp',
            'lemon': '1',
            'garlic': '3 cloves',
        },
        'cook_time': 25,
        'difficulty': 'medium',
        'cuisine': 'Mediterranean',
        'dietary': ['gluten-free', 'pescatarian'],
        'servings': 2,
        'instructions': [
            'Preheat oven to 400°F (200°C)',
            'Place salmon fillets on a baking sheet',
            'Arrange broccoli and bell peppers around salmon',
            'Drizzle everything with olive oil and minced garlic',
            'Season with salt, pepper, and lemon juice',
            'Roast for 15-20 minutes until salmon flakes easily',
            'Serve with lemon wedges',
        ],
    },
    {
        'name': 'Creamy Tomato Soup',
        'ingredients': [
            'tomatoes',
            'onion',
            'garlic',
            'vegetable broth',
            'cream',
            'basil',
        ],
        'amounts': {
            'tomatoes': '2 lbs',
            'onion': '1',
            'garlic': '4 cloves',
            'vegetable broth': '4 cups',
            'cream': '0.5 cup',
            'basil': '1 handful',
        },
        'cook_time': 30,
        'difficulty': 'easy',
        'cuisine': 'American',
        'dietary': ['vegetarian'],
        'servings': 4,
        'instructions': [
            'Sauté diced onion and garlic in a large pot until soft',
            'Add canned or fresh tomatoes and vegetable broth',
            'Bring to a boil, then reduce heat and simmer for 15 minutes',
            'Use an immersion blender to puree the soup until smooth',
            'Stir in cream and fresh basil',
            'Season with salt and pepper to taste',
            'Serve hot with crusty bread',
        ],
    },
    {
        'name': 'Veggie Buddha Bowl',
        'ingredients': [
            'rice',
            'chickpeas',
            'sweet potato',
            'kale',
            'avocado',
            'tahini',
        ],
        'amounts': {
            'rice': '1 cup',
            'chickpeas': '1 can',
            'sweet potato': '2',
            'kale': '4 cups',
            'avocado': '1',
            'tahini': '0.25 cup',
        },
        'cook_time': 35,
        'difficulty': 'medium',
        'cuisine': 'International',
        'dietary': ['vegan', 'gluten-free'],
        'servings': 2,
        'instructions': [
            'Cook rice according to package directions',
            'Roast cubed sweet potato at 425°F for 25 minutes',
            'Rinse and drain chickpeas, roast with sweet potato for last 15 minutes',
            'Massage kale with a bit of olive oil and lemon juice',
            'Assemble bowls with rice as base',
            'Top with roasted vegetables, kale, and sliced avocado',
            'Drizzle with tahini dressing',
        ],
    },
    {
        'name': 'Classic Caesar Salad',
        'ingredients': [
            'romaine lettuce',
            'parmesan',
            'croutons',
            'caesar dressing',
            'lemon',
        ],
        'amounts': {
            'romaine lettuce': '2 heads',
            'parmesan': '1 cup',
            'croutons': '2 cups',
            'caesar dressing': '0.5 cup',
            'lemon': '1',
        },
        'cook_time': 10,
        'difficulty': 'easy',
        'cuisine': 'Italian',
        'dietary': ['vegetarian'],
        'servings': 4,
        'instructions': [
            'Wash and chop romaine lettuce into bite-sized pieces',
            'In a large bowl, toss lettuce with Caesar dressing',
            'Add freshly grated parmesan cheese',
            'Top with croutons',
            'Add a squeeze of fresh lemon juice',
            'Toss gently to combine',
            'Serve immediately',
        ],
    },
    {
        'name': 'Shrimp Scampi',
        'ingredients': [
            'shrimp',
            'pasta',
            'garlic',
            'butter',
            'white wine',
            'lemon',
            'parsley',
        ],
        'amounts': {
            'shrimp': '1 lb',
            'pasta': '12 oz',
            'garlic': '5 cloves',
            'butter': '4 tbsp',
            'white wine': '0.5 cup',
            'lemon': '1',
            'parsley': '0.25 cup',
        },
        'cook_time': 20,
        'difficulty': 'medium',
        'cuisine': 'Italian',
        'dietary': ['pescatarian'],
        'servings': 4,
        'instructions': [
            'Cook pasta according to package directions',
            'Melt butter in a large skillet over medium heat',
            'Add minced garlic and cook for 1 minute',
            'Add shrimp and cook until pink, about 3 minutes per side',
            'Add white wine and lemon juice, simmer for 2 minutes',
            'Toss in cooked pasta and chopped parsley',
            'Season with salt, pepper, and red pepper flakes',
        ],
    },
    {
        'name': 'Thai Peanut Chicken Noodles',
        'ingredients': [
            'chicken',
            'noodles',
            'peanut butter',
            'soy sauce',
            'lime',
            'garlic',
            'carrot',
        ],
        'amounts': {
            'chicken': '1 lb',
            'noodles': '8 oz',
            'peanut butter': '0.33 cup',
            'soy sauce': '3 tbsp',
            'lime': '2',
            'garlic': '3 cloves',
            'carrot': '2',
        },
        'cook_time': 25,
        'difficulty': 'easy',
        'cuisine': 'Thai',
        'dietary': [],
        'servings': 4,
        'instructions': [
            'Cook the noodles according to package directions, then drain and rinse',
            'Whisk peanut butter, soy sauce, and lime juice with 3 tbsp of warm water',
            'Slice the chicken thinly and julienne the carrots',
            'Sear the chicken in a hot pan until cooked through, about 6 minutes',
            'Add garlic and carrots, stir-fry for 2 minutes',
            'Add the noodles and peanut sauce, toss until every strand is coated',
            'Finish with lime juice and extra peanuts',
        ],
    },
    {
        'name': 'Chickpea and Spinach Curry',
        'ingredients': [
            'chickpeas',
            'spinach',
            'onion',
            'garlic',
            'ginger',
            'coconut milk',
            'curry powder',
            'rice',
        ],
        'amounts': {
            'chickpeas': '2 cans',
            'spinach': '4 cups',
            'onion': '1',
            'garlic': '4 cloves',
            'ginger': '1 tbsp',
            'coconut milk': '1 can',
            'curry powder': '2 tbsp',
            'rice': '1.5 cups',
        },
        'cook_time': 30,
        'difficulty': 'easy',
        'cuisine': 'Indian',
        'dietary': ['vegan', 'gluten-free', 'dairy-free'],
        'servings': 4,
        'instructions': [
            'Cook the rice according to package directions',
            'Sauté diced onion, garlic, and ginger in a large pot for 5 minutes',
            'Add curry powder and toast for 1 minute until fragrant',
            'Add chickpeas, coconut milk, and 1 cup of water',
            'Simmer for 15 minutes until the sauce thickens',
            'Stir in the spinach and let it wilt, about 2 minutes',
            'Season with salt and serve over rice',
        ],
    },
    {
        'name': 'Chicken Tikka Masala',
        'ingredients': [
            'chicken',
            'yogurt',
            'tomato',
            'onion',
            'garlic',
            'garam masala',
            'cream',
            'rice',
        ],
        'amounts': {
            'chicken': '1.5 lbs',
            'yogurt': '0.5 cup',
            'tomato': '2',
            'onion': '1',
            'garlic': '4 cloves',
            'garam masala': '2 tbsp',
            'cream': '0.5 cup',
            'rice': '1.5 cups',
        },
        'cook_time': 45,
        'difficulty': 'medium',
        'cuisine': 'Indian',
        'dietary': ['gluten-free'],
        'servings': 4,
        'instructions': [
            'Marinate the cubed chicken in yogurt and half the garam masala for 30 minutes',
            'Cook the rice according to package directions',
            'Sear the marinated chicken in a hot pan until browned, then set aside',
            'Soften the onion and garlic, then add the remaining garam masala',
            'Add chopped tomatoes and cook down for 10 minutes into a thick sauce',
            'Return the chicken and stir in cream, simmer for 10 minutes',
            'Serve over rice with extra cream',
        ],
    },
    {
        'name': 'Teriyaki Salmon Rice Bowl',
        'ingredients': [
            'salmon',
            'rice',
            'soy sauce',
            'honey',
            'broccoli',
            'ginger',
            'sesame seeds',
        ],
        'amounts': {
            'salmon': '2 fillets',
            'rice': '1.5 cups',
            'soy sauce': '0.25 cup',
            'honey': '2 tbsp',
            'broccoli': '3 cups',
            'ginger': '1 tbsp',
            'sesame seeds': '1 tbsp',
        },
        'cook_time': 30,
        'difficulty': 'easy',
        'cuisine': 'Japanese',
        'dietary': ['pescatarian'],
        'servings': 2,
        'instructions': [
            'Cook the rice according to package directions',
            'Whisk soy sauce, honey, and grated ginger into a teriyaki glaze',
            'Steam the broccoli for 4 minutes until bright green',
            'Sear the salmon skin-side down for 4 minutes, then flip for 2 more',
            'Pour the glaze into the pan and let it thicken and coat the salmon',
            'Serve over rice with broccoli and sesame seeds',
        ],
    },
    {
        'name': 'Black Bean Tacos',
        'ingredients': [
            'black beans',
            'tortillas',
            'avocado',
            'lime',
            'cumin',
            'onion',
            'cilantro',
        ],
        'amounts': {
            'black beans': '2 cans',
            'tortillas': '8',
            'avocado': '2',
            'lime': '1',
            'cumin': '2 tsp',
            'onion': '1',
            'cilantro': '0.5 cup',
        },
        'cook_time': 15,
        'difficulty': 'easy',
        'cuisine': 'Mexican',
        'dietary': ['vegan', 'gluten-free-option', 'dairy-free'],
        'servings': 4,
        'instructions': [
            'Warm the black beans with cumin and a splash of water, mashing lightly',
            'Dice the onion and avocado, and chop the cilantro',
            'Warm the tortillas in a dry skillet or microwave',
            'Fill each tortilla with beans, onion, and avocado',
            'Top with cilantro and a squeeze of lime',
            'Serve with extra lime wedges',
        ],
    },
    {
        'name': 'Greek Yogurt Berry Bowl',
        'ingredients': [
            'greek yogurt',
            'berries',
            'granola',
            'honey',
            'banana',
        ],
        'amounts': {
            'greek yogurt': '2 cups',
            'berries': '2 cups',
            'granola': '1 cup',
            'honey': '2 tbsp',
            'banana': '1',
        },
        'cook_time': 5,
        'difficulty': 'easy',
        'cuisine': 'Greek',
        'dietary': ['vegetarian'],
        'servings': 2,
        'instructions': [
            'Spoon the yogurt into two bowls',
            'Top with the berries and sliced banana',
            'Scatter the granola over the top',
            'Drizzle with honey and serve immediately',
        ],
    },
    {
        'name': 'Falafel Mezze Platter',
        'ingredients': [
            'chickpeas',
            'parsley',
            'garlic',
            'cumin',
            'tahini',
            'lemon',
            'cucumber',
        ],
        'amounts': {
            'chickpeas': '2 cans',
            'parsley': '1 cup',
            'garlic': '6 cloves',
            'cumin': '2 tsp',
            'tahini': '0.5 cup',
            'lemon': '1',
            'cucumber': '2',
        },
        'cook_time': 30,
        'difficulty': 'medium',
        'cuisine': 'Mediterranean',
        'dietary': ['vegan', 'dairy-free'],
        'servings': 4,
        'instructions': [
            'Soak dried chickpeas overnight, then drain well',
            'Blend chickpeas, parsley, garlic, cumin, and salt into a coarse paste',
            'Chill the mixture for 30 minutes so it holds together',
            'Shape into balls and fry or bake until golden, about 15 minutes',
            'Whisk tahini with lemon juice and water into a pourable sauce',
            'Serve the falafel with sliced cucumber and the tahini sauce',
        ],
    },
    {
        'name': 'Tofu Vegetable Stir-Fry',
        'ingredients': [
            'tofu',
            'broccoli',
            'bell pepper',
            'carrot',
            'soy sauce',
            'ginger',
            'garlic',
            'sesame seeds',
        ],
        'amounts': {
            'tofu': '14 oz',
            'broccoli': '3 cups',
            'bell pepper': '2',
            'carrot': '2',
            'soy sauce': '3 tbsp',
            'ginger': '1 tbsp',
            'garlic': '3 cloves',
            'sesame seeds': '1 tbsp',
        },
        'cook_time': 20,
        'difficulty': 'easy',
        'cuisine': 'Asian',
        'dietary': ['vegan', 'dairy-free'],
        'servings': 4,
        'instructions': [
            'Press the tofu for 10 minutes, then cube it and pat dry',
            'Mix soy sauce, grated ginger, and garlic into a sauce',
            'Sear the tofu in a hot wok until golden on all sides, about 8 minutes',
            'Add the broccoli, pepper, and carrot, stir-frying until crisp-tender',
            'Pour in the sauce and toss to coat, adding a splash of water',
            'Finish with sesame seeds and serve over rice',
        ],
    },
    {
        'name': 'French Onion Soup',
        'ingredients': [
            'onion',
            'beef broth',
            'butter',
            'thyme',
            'baguette',
            'gruyere',
            'white wine',
        ],
        'amounts': {
            'onion': '6',
            'beef broth': '6 cups',
            'butter': '3 tbsp',
            'thyme': '4 sprigs',
            'baguette': '8 slices',
            'gruyere': '2 cups',
            'white wine': '0.5 cup',
        },
        'cook_time': 70,
        'difficulty': 'hard',
        'cuisine': 'French',
        'dietary': [],
        'servings': 6,
        'instructions': [
            'Melt butter in a large heavy pot and add thinly sliced onions',
            'Cook over low heat for 40 minutes, stirring often, until deep golden',
            'Deglaze with white wine, scraping the bottom of the pot',
            'Add beef broth and thyme, then simmer for 20 minutes',
            'Toast the baguette slices until dry all the way through',
            'Ladle soup into oven-safe bowls and float the toast on top',
            'Pile on gruyere and broil until the cheese bubbles and browns',
        ],
    },
]


def find_recipes_by_ingredients(available_ingredients):
    """
    Find recipes that can be made with the available ingredients.

    Args:
        available_ingredients (list): List of ingredient names

    Returns:
        list: Recipes sorted by number of matching ingredients
    """
    available_set = {ingredient.lower().strip() for ingredient in available_ingredients}
    matches = []

    for recipe in all_recipes():
        recipe_ingredients = {ingredient.lower() for ingredient in recipe['ingredients']}
        matching = recipe_ingredients.intersection(available_set)
        missing = recipe_ingredients - available_set

        if matching:  # At least one ingredient matches
            match_percentage = len(matching) / len(recipe_ingredients)
            matches.append(
                {
                    'recipe': recipe,
                    'matching_count': len(matching),
                    'missing_count': len(missing),
                    'match_percentage': match_percentage,
                    'missing_ingredients': list(missing),
                }
            )

    # Sort by match percentage, then by number of matching ingredients
    matches.sort(key=lambda x: (x['match_percentage'], x['matching_count']), reverse=True)
    return matches


_SEARCH_FIELDS = ('name', 'cuisine', 'ingredients', 'instructions')

# Relevance weights. A term in the title matters far more than the same term
# buried in the method, so "chicken" should surface "Garlic Chicken and Rice"
# above a recipe that merely uses chicken.
_SEARCH_WEIGHTS = {
    'name': 100,
    'cuisine': 40,
    'ingredients': 30,
    'instructions': 5,
}


def _searchable_text(recipe, field):
    """Return the lowercased text of ``field`` for a recipe."""
    value = recipe.get(field)
    if isinstance(value, list):
        return ' '.join(str(item) for item in value).lower()
    return str(value or '').lower()


# Words keep internal hyphens and apostrophes so "stir-fry" and "chef's" stay
# whole tokens rather than splitting into fragments.
_WORD_RE = re.compile(r"[a-z0-9]+(?:[-'][a-z0-9]+)*")


def _term_matches(text, term):
    """True when any word in ``text`` starts with ``term``.

    Prefix matching, not substring: "asi" finds "Asian" but not "roasting",
    and "chick" still finds "chicken". Substring matching made short queries
    return whatever happened to contain the letters.
    """
    return any(word.startswith(term) for word in _WORD_RE.findall(text))


def _score_recipe(recipe, terms):
    """Sum the weights of every (term, field) hit. ``None`` if a term is missing."""
    total = 0
    for term in terms:
        best = 0
        for field in _SEARCH_FIELDS:
            if _term_matches(_searchable_text(recipe, field), term):
                best = max(best, _SEARCH_WEIGHTS[field])
        if best == 0:
            return None
        total += best
    return total


def search_recipes(query):
    """Free-text search across built-in and user recipes.

    Every whitespace-separated term must appear somewhere in the recipe, which
    keeps results precise: "chicken rice" finds the one-pan recipe, not every
    chicken dish. An empty query browses everything, sorted by name.

    Args:
        query (str): Free text, e.g. "thai", "noodles", "chicken rice"

    Returns:
        list: Matching recipes, most relevant first.
    """
    terms = query.lower().split()
    candidates = all_recipes()

    if not terms:
        return sorted(candidates, key=lambda r: r['name'].lower())

    scored = []
    for recipe in candidates:
        score = _score_recipe(recipe, terms)
        if score is not None:
            scored.append((score, recipe))

    scored.sort(key=lambda pair: (-pair[0], pair[1]['name'].lower()))
    return [recipe for _, recipe in scored]


def all_cuisines():
    """Every cuisine present in the merged recipe set, sorted and deduplicated."""
    return sorted({r.get('cuisine', '') for r in all_recipes() if r.get('cuisine')})


def filter_recipes(cook_time=None, difficulty=None, dietary=None, cuisine=None, pool=None):
    """
    Filter recipes based on various criteria.

    Args:
        cook_time (int): Maximum cooking time in minutes
        difficulty (str): Difficulty level (easy, medium, hard)
        dietary (str): Dietary restriction (vegetarian, vegan, gluten-free, etc.)
        cuisine (str): Cuisine type. Partial names match, so "asi" finds "Asian".
        pool (list): Restrict filtering to these recipes instead of all of them.
            Used to narrow the results of a search.

    Returns:
        list: Filtered recipes
    """
    filtered = list(pool) if pool is not None else all_recipes()

    if cook_time:
        filtered = [r for r in filtered if r['cook_time'] <= cook_time]

    if difficulty:
        filtered = [r for r in filtered if r['difficulty'].lower() == difficulty.lower()]

    if dietary:
        filtered = [r for r in filtered if dietary.lower() in [d.lower() for d in r['dietary']]]

    if cuisine:
        # Substring, not equality: "asi" should find "Asian".
        needle = cuisine.lower().strip()
        filtered = [r for r in filtered if needle in r['cuisine'].lower()]

    return filtered


def get_recipe_by_name(name):
    """Get a specific recipe by name."""
    for recipe in all_recipes():
        if recipe['name'].lower() == name.lower():
            return recipe
    return None
