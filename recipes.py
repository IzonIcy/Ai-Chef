"""
Recipe database with ingredient-based search functionality
"""

RECIPE_DATABASE = [
    {
        "name": "Chicken Stir-Fry with Broccoli",
        "ingredients": ["chicken", "broccoli", "soy sauce", "garlic", "ginger", "oil"],
        "cook_time": 20,
        "difficulty": "easy",
        "cuisine": "Asian",
        "dietary": ["gluten-free-option"],
        "servings": 4,
        "instructions": [
            "Cut chicken into bite-sized pieces",
            "Heat oil in a large wok or pan over high heat",
            "Add minced garlic and ginger, stir for 30 seconds",
            "Add chicken and cook until golden brown, about 5-7 minutes",
            "Add broccoli florets and stir-fry for 3-4 minutes",
            "Add soy sauce and toss everything together",
            "Serve hot over rice"
        ]
    },
    {
        "name": "Garlic Chicken and Rice",
        "ingredients": ["chicken", "rice", "garlic", "butter", "chicken broth", "thyme"],
        "cook_time": 35,
        "difficulty": "easy",
        "cuisine": "American",
        "dietary": ["gluten-free"],
        "servings": 4,
        "instructions": [
            "Season chicken breasts with salt and pepper",
            "Melt butter in a large skillet over medium-high heat",
            "Add chicken and cook until golden, 4-5 minutes per side",
            "Remove chicken and set aside",
            "In the same pan, add minced garlic and rice, toast for 1 minute",
            "Add chicken broth and thyme, bring to a boil",
            "Return chicken to pan, cover and simmer for 20 minutes",
            "Let rest 5 minutes before serving"
        ]
    },
    {
        "name": "One-Pan Chicken Broccoli Rice",
        "ingredients": ["chicken", "rice", "broccoli", "onion", "garlic", "chicken broth", "cheese"],
        "cook_time": 40,
        "difficulty": "easy",
        "cuisine": "American",
        "dietary": ["gluten-free"],
        "servings": 6,
        "instructions": [
            "Preheat oven to 375°F (190°C)",
            "In a large oven-safe pan, combine rice, chicken broth, diced chicken, and diced onion",
            "Add minced garlic and season with salt and pepper",
            "Cover tightly with foil and bake for 25 minutes",
            "Remove from oven, add broccoli florets, cover and bake for another 10 minutes",
            "Sprinkle cheese on top and return to oven uncovered for 5 minutes",
            "Let stand for 5 minutes before serving"
        ]
    },
    {
        "name": "Vegetarian Pasta Primavera",
        "ingredients": ["pasta", "broccoli", "bell pepper", "zucchini", "garlic", "olive oil", "parmesan"],
        "cook_time": 25,
        "difficulty": "easy",
        "cuisine": "Italian",
        "dietary": ["vegetarian"],
        "servings": 4,
        "instructions": [
            "Cook pasta according to package directions",
            "Meanwhile, heat olive oil in a large pan",
            "Add garlic and sauté for 1 minute",
            "Add broccoli, bell pepper, and zucchini, cook for 5-7 minutes",
            "Drain pasta and add to vegetables",
            "Toss everything together with parmesan cheese",
            "Season with salt, pepper, and red pepper flakes"
        ]
    },
    {
        "name": "Beef Tacos",
        "ingredients": ["ground beef", "taco seasoning", "tortillas", "lettuce", "tomato", "cheese", "sour cream"],
        "cook_time": 20,
        "difficulty": "easy",
        "cuisine": "Mexican",
        "dietary": [],
        "servings": 4,
        "instructions": [
            "Brown ground beef in a large skillet over medium-high heat",
            "Drain excess fat",
            "Add taco seasoning and water according to package directions",
            "Simmer for 5 minutes until thickened",
            "Warm tortillas in microwave or on stovetop",
            "Assemble tacos with beef and your favorite toppings",
            "Serve with sour cream on the side"
        ]
    },
    {
        "name": "Salmon with Roasted Vegetables",
        "ingredients": ["salmon", "broccoli", "bell pepper", "olive oil", "lemon", "garlic"],
        "cook_time": 25,
        "difficulty": "medium",
        "cuisine": "Mediterranean",
        "dietary": ["gluten-free", "pescatarian"],
        "servings": 2,
        "instructions": [
            "Preheat oven to 400°F (200°C)",
            "Place salmon fillets on a baking sheet",
            "Arrange broccoli and bell peppers around salmon",
            "Drizzle everything with olive oil and minced garlic",
            "Season with salt, pepper, and lemon juice",
            "Roast for 15-20 minutes until salmon flakes easily",
            "Serve with lemon wedges"
        ]
    },
    {
        "name": "Creamy Tomato Soup",
        "ingredients": ["tomatoes", "onion", "garlic", "vegetable broth", "cream", "basil"],
        "cook_time": 30,
        "difficulty": "easy",
        "cuisine": "American",
        "dietary": ["vegetarian"],
        "servings": 4,
        "instructions": [
            "Sauté diced onion and garlic in a large pot until soft",
            "Add canned or fresh tomatoes and vegetable broth",
            "Bring to a boil, then reduce heat and simmer for 15 minutes",
            "Use an immersion blender to puree the soup until smooth",
            "Stir in cream and fresh basil",
            "Season with salt and pepper to taste",
            "Serve hot with crusty bread"
        ]
    },
    {
        "name": "Veggie Buddha Bowl",
        "ingredients": ["rice", "chickpeas", "sweet potato", "kale", "avocado", "tahini"],
        "cook_time": 35,
        "difficulty": "medium",
        "cuisine": "International",
        "dietary": ["vegan", "gluten-free"],
        "servings": 2,
        "instructions": [
            "Cook rice according to package directions",
            "Roast cubed sweet potato at 425°F for 25 minutes",
            "Rinse and drain chickpeas, roast with sweet potato for last 15 minutes",
            "Massage kale with a bit of olive oil and lemon juice",
            "Assemble bowls with rice as base",
            "Top with roasted vegetables, kale, and sliced avocado",
            "Drizzle with tahini dressing"
        ]
    },
    {
        "name": "Classic Caesar Salad",
        "ingredients": ["romaine lettuce", "parmesan", "croutons", "caesar dressing", "lemon"],
        "cook_time": 10,
        "difficulty": "easy",
        "cuisine": "Italian",
        "dietary": ["vegetarian"],
        "servings": 4,
        "instructions": [
            "Wash and chop romaine lettuce into bite-sized pieces",
            "In a large bowl, toss lettuce with Caesar dressing",
            "Add freshly grated parmesan cheese",
            "Top with croutons",
            "Add a squeeze of fresh lemon juice",
            "Toss gently to combine",
            "Serve immediately"
        ]
    },
    {
        "name": "Shrimp Scampi",
        "ingredients": ["shrimp", "pasta", "garlic", "butter", "white wine", "lemon", "parsley"],
        "cook_time": 20,
        "difficulty": "medium",
        "cuisine": "Italian",
        "dietary": ["pescatarian"],
        "servings": 4,
        "instructions": [
            "Cook pasta according to package directions",
            "Melt butter in a large skillet over medium heat",
            "Add minced garlic and cook for 1 minute",
            "Add shrimp and cook until pink, about 3 minutes per side",
            "Add white wine and lemon juice, simmer for 2 minutes",
            "Toss in cooked pasta and chopped parsley",
            "Season with salt, pepper, and red pepper flakes"
        ]
    }
]


def find_recipes_by_ingredients(available_ingredients):
    """
    Find recipes that can be made with the available ingredients.
    
    Args:
        available_ingredients (list): List of ingredient names
        
    Returns:
        list: Recipes sorted by number of matching ingredients
    """
    available_set = set(ingredient.lower().strip() for ingredient in available_ingredients)
    matches = []
    
    for recipe in RECIPE_DATABASE:
        recipe_ingredients = set(ingredient.lower() for ingredient in recipe["ingredients"])
        matching = recipe_ingredients.intersection(available_set)
        missing = recipe_ingredients - available_set
        
        if matching:  # At least one ingredient matches
            match_percentage = len(matching) / len(recipe_ingredients)
            matches.append({
                "recipe": recipe,
                "matching_count": len(matching),
                "missing_count": len(missing),
                "match_percentage": match_percentage,
                "missing_ingredients": list(missing)
            })
    
    # Sort by match percentage, then by number of matching ingredients
    matches.sort(key=lambda x: (x["match_percentage"], x["matching_count"]), reverse=True)
    return matches


def filter_recipes(cook_time=None, difficulty=None, dietary=None, cuisine=None):
    """
    Filter recipes based on various criteria.
    
    Args:
        cook_time (int): Maximum cooking time in minutes
        difficulty (str): Difficulty level (easy, medium, hard)
        dietary (str): Dietary restriction (vegetarian, vegan, gluten-free, etc.)
        cuisine (str): Cuisine type
        
    Returns:
        list: Filtered recipes
    """
    filtered = RECIPE_DATABASE.copy()
    
    if cook_time:
        filtered = [r for r in filtered if r["cook_time"] <= cook_time]
    
    if difficulty:
        filtered = [r for r in filtered if r["difficulty"].lower() == difficulty.lower()]
    
    if dietary:
        filtered = [r for r in filtered if dietary.lower() in [d.lower() for d in r["dietary"]]]
    
    if cuisine:
        filtered = [r for r in filtered if r["cuisine"].lower() == cuisine.lower()]
    
    return filtered


def get_recipe_by_name(name):
    """Get a specific recipe by name."""
    for recipe in RECIPE_DATABASE:
        if recipe["name"].lower() == name.lower():
            return recipe
    return None
