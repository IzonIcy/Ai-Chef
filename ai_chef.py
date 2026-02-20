#!/usr/bin/env python3
"""
AI Chef - Smart Cooking Assistant
A command-line application to help you discover recipes, plan meals, and cook smarter.
"""

import os
try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        pass
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich.prompt import Confirm
from rich import box

from recipes import (
    find_recipes_by_ingredients, 
    filter_recipes, 
    get_recipe_by_name,
    RECIPE_DATABASE
)
from ai_generator import (
    generate_recipe_with_ai,
    get_cooking_tips,
    suggest_substitutions
)
from meal_planner import MealPlanner, SavedRecipes, PantryManager
from gamification import GamificationManager

console = Console()
gamification = GamificationManager()


def parse_optional_int(value):
    """Safely parse optional integer input."""
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def display_banner():
    """Display welcome banner."""
    banner = """
    ╔═══════════════════════════════════════╗
    ║          🍳  AI CHEF  🍳              ║
    ║    Your Smart Cooking Assistant       ║
    ╚═══════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def display_gamification_status():
    """Display current gamification status."""
    status = gamification.get_gamification_status()
    streak = status["streak"]
    achievements = status["achievements"]
    challenges = status["challenges"]
    
    # Display streak
    console.print(f"\n[bold yellow]🔥 Your Streak: {streak['current_streak']} days[/bold yellow]")
    console.print(f"[dim]Longest streak: {streak['longest_streak']} days | Total meals: {streak['total_meals']}[/dim]")
    
    # Display achievements
    if achievements["unlocked"]:
        console.print(f"\n[bold green]🏆 Achievements Unlocked ({len(achievements['unlocked'])}):[/bold green]")
        for achievement in achievements["unlocked"]:
            console.print(f"  {achievement['icon']} {achievement['name']} - {achievement['description']}")
    
    # Display weekly challenges
    console.print(f"\n[bold cyan]🎯 This Week's Challenges:[/bold cyan]")
    for challenge in challenges:
        progress = challenge["progress"]
        target = challenge["target"]
        percent = int((min(progress, target) / target) * 100)
        bar_filled = int(percent / 10)
        bar = "█" * bar_filled + "░" * (10 - bar_filled)
        
        status_icon = "✓" if challenge["completed"] else " "
        console.print(f"  [{status_icon}] {challenge['name']}")
        console.print(f"      [{bar}] {progress}/{target} - {challenge['reward']}")


def display_achievements_menu():
    """Display achievements and badges."""
    console.print("\n[bold yellow]🏆 Achievements & Badges[/bold yellow]\n")
    
    status = gamification.get_gamification_status()
    achievements = status["achievements"]
    unlocked = achievements["unlocked"]
    locked = achievements["locked"]
    
    # Display unlocked achievements
    if unlocked:
        console.print(f"[bold green]Unlocked ({len(unlocked)})[/bold green]\n")
        table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
        table.add_column("Icon", style="yellow", width=5)
        table.add_column("Achievement")
        table.add_column("Date Unlocked", style="dim")
        
        for achievement in unlocked:
            table.add_row(
                achievement['icon'],
                f"{achievement['name']}\n{achievement['description']}",
                achievement.get('unlock_date', 'N/A')[:10]
            )
        console.print(table)
    
    # Display locked achievements
    if locked:
        console.print(f"\n[bold cyan]Locked ({len(locked)})[/bold cyan]\n")
        table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
        table.add_column("Icon", style="dim", width=5)
        table.add_column("Achievement", style="dim")
        
        for achievement in locked:
            table.add_row(
                achievement['icon'],
                f"{achievement['name']}\n{achievement['description']}"
            )
        console.print(table)
    
    console.print("\n[dim]Keep cooking to unlock more achievements![/dim]")


def display_recipe(recipe):
    """Display a recipe in a nice format."""
    console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
    console.print(f"[bold yellow]{recipe['name']}[/bold yellow]")
    console.print(f"[bold cyan]{'='*60}[/bold cyan]\n")
    # Info table
    info_table = Table(show_header=False, box=box.SIMPLE)
    info_table.add_column("Property", style="cyan")
    info_table.add_column("Value", style="white")
    
    info_table.add_row("⏱️  Cook Time", f"{recipe.get('cook_time', 'N/A')} minutes")
    info_table.add_row("👨‍🍳 Difficulty", recipe.get('difficulty', 'N/A').title())
    info_table.add_row("🍽️  Servings", str(recipe.get('servings', 'N/A')))
    info_table.add_row("🌍 Cuisine", recipe.get('cuisine', 'N/A'))
    
    if recipe.get('dietary'):
        dietary_str = ", ".join(recipe['dietary'])
        info_table.add_row("🥗 Dietary", dietary_str.title())
    
    console.print(info_table)
    
    # Ingredients
    console.print("\n[bold green]Ingredients:[/bold green]")
    for ingredient in recipe.get('ingredients', []):
        console.print(f"  • {ingredient}")
    
    # Instructions
    console.print("\n[bold green]Instructions:[/bold green]")
    for i, instruction in enumerate(recipe.get('instructions', []), 1):
        console.print(f"  {i}. {instruction}")
    
    console.print(f"\n[bold cyan]{'='*60}[/bold cyan]\n")


def find_recipes_menu():
    """Menu for finding recipes by ingredients."""
    console.print("\n[bold yellow]🔍 Find Recipes by Ingredients[/bold yellow]\n")
    
    ingredients_input = Prompt.ask("Enter ingredients you have (comma-separated)")
    ingredients = [ing.strip() for ing in ingredients_input.split(',')]
    
    # Optional filters
    console.print("\n[dim]Optional filters (press Enter to skip):[/dim]")
    max_time = Prompt.ask("Maximum cook time (minutes)", default="")
    max_time_int = parse_optional_int(max_time)
    if max_time and max_time_int is None:
        console.print("[yellow]Invalid cook time entered. Skipping cook time filter.[/yellow]")

    difficulty = Prompt.ask("Difficulty level (easy/medium/hard)", default="")
    dietary = Prompt.ask("Dietary preference (vegetarian/vegan/gluten-free)", default="")
    
    # Find matching recipes
    matches = find_recipes_by_ingredients(ingredients)
    
    # Apply additional filters
    if max_time or difficulty or dietary:
        filtered_matches = []
        for match in matches:
            recipe = match["recipe"]
            passes = True
            
            if max_time_int is not None and recipe["cook_time"] > max_time_int:
                passes = False
            if difficulty and recipe["difficulty"].lower() != difficulty.lower():
                passes = False
            if dietary and dietary.lower() not in [d.lower() for d in recipe["dietary"]]:
                passes = False
            
            if passes:
                filtered_matches.append(match)
        matches = filtered_matches
    
    if not matches:
        console.print("\n[red]No recipes found matching your criteria.[/red]")
        return
    
    # Display results
    console.print(f"\n[bold green]Found {len(matches)} recipe(s):[/bold green]\n")
    
    results_table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
    results_table.add_column("#", style="dim", width=3)
    results_table.add_column("Recipe Name", style="yellow")
    results_table.add_column("Match %", justify="center")
    results_table.add_column("Cook Time", justify="center")
    results_table.add_column("Difficulty", justify="center")
    results_table.add_column("Missing", style="dim")
    
    for idx, match in enumerate(matches[:10], 1):  # Show top 10
        recipe = match["recipe"]
        match_pct = f"{match['match_percentage']*100:.0f}%"
        missing = f"{match['missing_count']} items"
        
        results_table.add_row(
            str(idx),
            recipe["name"],
            match_pct,
            f"{recipe['cook_time']} min",
            recipe["difficulty"],
            missing
        )
    
    console.print(results_table)
    
    # Let user view a recipe
    if Confirm.ask("\nWould you like to view a recipe in detail?"):
        choice = Prompt.ask("Enter recipe number")
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(matches):
                recipe = matches[idx]["recipe"]
                display_recipe(recipe)
                
                # Option to save
                if Confirm.ask("Save this recipe to favorites?"):
                    saved_recipes = SavedRecipes()
                    if saved_recipes.add_recipe(recipe):
                        console.print("[green]✓ Recipe saved![/green]")
                        # Record gamification
                        is_veg = "vegetarian" in [d.lower() for d in recipe.get("dietary", [])]
                        is_vegan = "vegan" in [d.lower() for d in recipe.get("dietary", [])]
                        gamification.record_recipe_cooked(
                            recipe_name=recipe["name"],
                            cuisine=recipe.get("cuisine"),
                            cooking_time=recipe.get("cook_time"),
                            is_vegetarian=is_veg,
                            is_vegan=is_vegan
                        )
                        console.print("[cyan]📈 Gamification updated![/cyan]")
                    else:
                        console.print("[yellow]Recipe already in favorites.[/yellow]")
        except ValueError:
            console.print("[red]Invalid selection.[/red]")


def ai_recipe_menu():
    """Menu for generating recipes with AI."""
    console.print("\n[bold yellow]🤖 Generate Custom Recipe with AI[/bold yellow]\n")
    
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]Error: OPENAI_API_KEY not found in environment.[/red]")
        console.print("[yellow]Please set your API key in a .env file or environment variable.[/yellow]")
        return
    
    console.print("[dim]Tell me what you'd like to cook (or press Enter for custom options):[/dim]")
    description = Prompt.ask("Recipe description", default="")
    
    ingredients = None
    dietary = None
    cuisine = None
    cook_time = None
    difficulty = None
    
    if not description or Confirm.ask("\nWould you like to specify more options?"):
        console.print("\n[dim]Optional parameters (press Enter to skip):[/dim]")
        
        ing_input = Prompt.ask("Ingredients to use (comma-separated)", default="")
        if ing_input:
            ingredients = [i.strip() for i in ing_input.split(',')]
        
        dietary = Prompt.ask("Dietary preference", default="")
        cuisine = Prompt.ask("Cuisine type", default="")
        time_input = Prompt.ask("Max cook time (minutes)", default="")
        parsed_time = parse_optional_int(time_input)
        if time_input and parsed_time is None:
            console.print("[yellow]Invalid cook time entered. Skipping cook time limit.[/yellow]")
        else:
            cook_time = parsed_time
        difficulty = Prompt.ask("Difficulty level", default="")
    
    console.print("\n[cyan]🧠 Generating your custom recipe with AI...[/cyan]\n")
    
    # Generate recipe
    recipe = generate_recipe_with_ai(
        ingredients=ingredients,
        dietary_preference=dietary,
        cuisine_type=cuisine,
        cook_time=cook_time,
        difficulty=difficulty,
        description=description
    )
    
    if "error" in recipe:
        console.print(f"[red]Error: {recipe['error']}[/red]")
        if "suggestion" in recipe:
            console.print(f"[yellow]{recipe['suggestion']}[/yellow]")
        return
    
    # Display the generated recipe
    display_recipe(recipe)
    
    # Option to save
    if Confirm.ask("Save this AI-generated recipe?"):
        saved_recipes = SavedRecipes()
        if saved_recipes.add_recipe(recipe):
            console.print("[green]✓ Recipe saved![/green]")
            # Record gamification
            is_veg = dietary and "vegetarian" in dietary.lower()
            is_vegan = dietary and "vegan" in dietary.lower()
            gamification.record_recipe_cooked(
                recipe_name=recipe.get("name", "AI Recipe"),
                cuisine=cuisine,
                cooking_time=cook_time,
                is_vegetarian=bool(is_veg),
                is_vegan=bool(is_vegan)
            )
            console.print("[cyan]📈 Gamification updated![/cyan]")


def ai_cooking_tips_menu():
    """Menu for AI cooking tips."""
    console.print("\n[bold yellow]💡 AI Cooking Tips[/bold yellow]\n")

    recipe_name = Prompt.ask("Enter recipe name")
    if not recipe_name.strip():
        console.print("[yellow]Please enter a recipe name.[/yellow]")
        return

    dietary_preferences = Prompt.ask("Dietary preferences (optional)", default="")
    dietary_value = dietary_preferences if dietary_preferences else None

    console.print("\n[cyan]Generating tips...[/cyan]\n")
    tips = get_cooking_tips(recipe_name, dietary_value)
    console.print(Panel(Markdown(tips), title=f"Tips for {recipe_name}", border_style="cyan"))


def ingredient_substitutions_menu():
    """Menu for ingredient substitutions."""
    console.print("\n[bold yellow]🔁 Ingredient Substitutions[/bold yellow]\n")

    ingredient = Prompt.ask("Enter ingredient to substitute")
    if not ingredient.strip():
        console.print("[yellow]Please enter an ingredient.[/yellow]")
        return

    console.print("\n[cyan]Finding substitutions...[/cyan]\n")
    substitutions = suggest_substitutions(ingredient)
    console.print(Panel(Markdown(substitutions), title=f"Substitutions for {ingredient}", border_style="green"))


def pantry_menu():
    """Menu for pantry inventory and expiry tracking."""
    console.print("\n[bold yellow]🥫 Pantry Manager[/bold yellow]\n")

    pantry = PantryManager()

    console.print("1. View pantry items")
    console.print("2. Add pantry item")
    console.print("3. Remove pantry item")
    console.print("4. View expiring soon")
    console.print("5. Suggest recipes using expiring items")

    choice = Prompt.ask("\nSelect an option", choices=["1", "2", "3", "4", "5"])

    if choice == "1":
        items = pantry.get_all_items()
        if not items:
            console.print("[yellow]Your pantry is empty.[/yellow]")
            return

        table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
        table.add_column("Item", style="yellow")
        table.add_column("Quantity", justify="center")
        table.add_column("Unit", justify="center")
        table.add_column("Expires", style="dim")

        for item in items:
            table.add_row(
                item.get("name", "Unknown"),
                str(item.get("quantity", 0)),
                item.get("unit", "item"),
                item.get("expires_on") or "-"
            )
        console.print(table)

    elif choice == "2":
        name = Prompt.ask("Ingredient name")
        quantity_input = Prompt.ask("Quantity", default="1")
        quantity = parse_optional_int(quantity_input)
        if quantity is None or quantity <= 0:
            console.print("[yellow]Invalid quantity. Using 1.[/yellow]")
            quantity = 1

        unit = Prompt.ask("Unit (item, cup, tbsp, etc.)", default="item")
        expires_on = Prompt.ask("Expiry date (YYYY-MM-DD, optional)", default="")
        expires_value = expires_on if expires_on else None

        pantry.add_item(name=name, quantity=quantity, unit=unit, expires_on=expires_value)
        console.print(f"[green]✓ Added {name} to pantry.[/green]")

    elif choice == "3":
        name = Prompt.ask("Ingredient name to remove")
        if pantry.remove_item(name):
            console.print(f"[green]✓ Removed {name} from pantry.[/green]")
        else:
            console.print("[yellow]Item not found.[/yellow]")

    elif choice == "4":
        expiring = pantry.get_expiring_items(within_days=3)
        if not expiring:
            console.print("[green]No items expiring in the next 3 days.[/green]")
            return

        table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
        table.add_column("Item", style="yellow")
        table.add_column("Days Left", justify="center")
        table.add_column("Expiry Date", style="dim")

        for item in expiring:
            days_left = item.get("days_left", 0)
            days_display = "Expired" if days_left < 0 else str(days_left)
            table.add_row(item.get("name", "Unknown"), days_display, item.get("expires_on", "-"))
        console.print(table)

    elif choice == "5":
        pantry_ingredients = pantry.get_pantry_ingredients()
        if not pantry_ingredients:
            console.print("[yellow]Your pantry is empty. Add ingredients first.[/yellow]")
            return

        expiring_items = pantry.get_expiring_items(within_days=3)
        expiring_names = {item.get("name", "").strip().lower() for item in expiring_items}

        matches = find_recipes_by_ingredients(pantry_ingredients)
        for match in matches:
            recipe_ingredients = {ingredient.lower() for ingredient in match["recipe"].get("ingredients", [])}
            match["use_soon_count"] = len(recipe_ingredients.intersection(expiring_names))

        matches.sort(key=lambda m: (m.get("use_soon_count", 0), m["match_percentage"]), reverse=True)

        if not matches:
            console.print("[yellow]No recipe suggestions found for current pantry items.[/yellow]")
            return

        table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
        table.add_column("#", style="dim", width=3)
        table.add_column("Recipe", style="yellow")
        table.add_column("Use-Soon Match", justify="center")
        table.add_column("Ingredient Match", justify="center")

        for idx, match in enumerate(matches[:10], 1):
            table.add_row(
                str(idx),
                match["recipe"]["name"],
                str(match.get("use_soon_count", 0)),
                f"{match['match_percentage']*100:.0f}%"
            )
        console.print(table)


def meal_planning_menu():
    """Menu for meal planning."""
    console.print("\n[bold yellow]📅 Meal Planning[/bold yellow]\n")
    
    planner = MealPlanner()
    
    console.print("1. Create weekly meal plan")
    console.print("2. View current meal plan")
    console.print("3. Generate grocery list")
    console.print("4. Add specific meal to plan")
    
    choice = Prompt.ask("\nSelect an option", choices=["1", "2", "3", "4"])
    
    if choice == "1":
        console.print("\n[dim]Optional preferences:[/dim]")
        dietary = Prompt.ask("Dietary preference", default="")
        max_time = Prompt.ask("Max cook time per meal (minutes)", default="")

        max_time_int = parse_optional_int(max_time)
        if max_time and max_time_int is None:
            console.print("[yellow]Invalid cook time entered. Skipping cook time filter.[/yellow]")

        dietary_pref = dietary if dietary else None
        
        console.print("\n[cyan]Creating your weekly meal plan...[/cyan]\n")
        week_plan = planner.create_weekly_plan(
            dietary_preference=dietary_pref,
            max_cook_time=max_time_int
        )
        
        # Display plan
        plan_table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
        plan_table.add_column("Day", style="yellow", width=12)
        plan_table.add_column("Recipe", style="white")
        plan_table.add_column("Cook Time", justify="center")
        plan_table.add_column("Servings", justify="center")
        
        for day, meal in week_plan.items():
            plan_table.add_row(
                day,
                meal["recipe"],
                f"{meal['cook_time']} min",
                str(meal["servings"])
            )
        
        console.print("\n[bold green]Your Weekly Meal Plan:[/bold green]\n")
        console.print(plan_table)
        console.print("\n[green]✓ Meal plan saved![/green]")
    
    elif choice == "2":
        current_plan = planner.get_current_plan()
        
        if not current_plan:
            console.print("\n[yellow]No meal plan found. Create one first![/yellow]")
            return
        
        # Display plan
        plan_table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
        plan_table.add_column("Day", style="yellow", width=12)
        plan_table.add_column("Recipe", style="white")
        plan_table.add_column("Cook Time", justify="center")
        plan_table.add_column("Servings", justify="center")
        
        for day, meal in current_plan.items():
            plan_table.add_row(
                day,
                meal["recipe"],
                f"{meal['cook_time']} min",
                str(meal["servings"])
            )
        
        console.print("\n[bold green]Your Current Meal Plan:[/bold green]\n")
        console.print(plan_table)
    
    elif choice == "3":
        current_plan = planner.get_current_plan()
        
        if not current_plan:
            console.print("\n[yellow]No meal plan found. Create one first![/yellow]")
            return
        
        grocery_list = planner.generate_grocery_list(current_plan)
        
        console.print("\n[bold green]🛒 Your Grocery List:[/bold green]\n")
        
        for category, items in grocery_list.items():
            console.print(f"\n[bold cyan]{category}:[/bold cyan]")
            for item in sorted(items, key=lambda x: x.get("item", "")):
                console.print(f"  □ {item.get('item', 'Unknown')} ({item.get('quantity', 1)} {item.get('unit', 'recipe-use')})")
    
    elif choice == "4":
        console.print("\nAvailable recipes:")
        for idx, recipe in enumerate(RECIPE_DATABASE[:10], 1):
            console.print(f"{idx}. {recipe['name']}")
        
        recipe_name = Prompt.ask("\nEnter recipe name")
        day = Prompt.ask("Enter day of week")
        
        if planner.add_meal_to_plan(day.title(), recipe_name):
            console.print(f"[green]✓ Added {recipe_name} to {day}![/green]")
        else:
            console.print("[red]Recipe not found.[/red]")


def saved_recipes_menu():
    """Menu for viewing saved recipes."""
    console.print("\n[bold yellow]💾 Saved Recipes[/bold yellow]\n")
    
    saved_recipes = SavedRecipes()
    saved = saved_recipes.get_all_saved()
    
    if not saved:
        console.print("[yellow]No saved recipes yet. Save some from the recipe finder or AI generator![/yellow]")
        return
    
    # Display saved recipes
    saved_table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
    saved_table.add_column("#", style="dim", width=3)
    saved_table.add_column("Recipe Name", style="yellow")
    saved_table.add_column("Saved At", style="dim")
    
    for idx, recipe in enumerate(saved, 1):
        saved_table.add_row(
            str(idx),
            recipe.get("name", "Unknown"),
            recipe.get("saved_at", "")
        )
    
    console.print(saved_table)
    
    # Options
    console.print("\n1. View recipe details")
    console.print("2. Remove from favorites")
    console.print("3. Go back")
    
    choice = Prompt.ask("\nSelect an option", choices=["1", "2", "3"])
    
    if choice == "1":
        recipe_num = Prompt.ask("Enter recipe number")
        try:
            idx = int(recipe_num) - 1
            if 0 <= idx < len(saved):
                display_recipe(saved[idx])
        except ValueError:
            console.print("[red]Invalid selection.[/red]")
    
    elif choice == "2":
        recipe_num = Prompt.ask("Enter recipe number to remove")
        try:
            idx = int(recipe_num) - 1
            if 0 <= idx < len(saved):
                recipe_name = saved[idx]["name"]
                if saved_recipes.remove_recipe(recipe_name):
                    console.print(f"[green]✓ Removed {recipe_name} from favorites.[/green]")
        except ValueError:
            console.print("[red]Invalid selection.[/red]")


def browse_all_recipes():
    """Browse all available recipes."""
    console.print("\n[bold yellow]📖 Browse All Recipes[/bold yellow]\n")
    
    # Apply filters
    console.print("[dim]Optional filters (press Enter to skip):[/dim]")
    max_time = Prompt.ask("Maximum cook time (minutes)", default="")
    max_time_int = parse_optional_int(max_time)
    if max_time and max_time_int is None:
        console.print("[yellow]Invalid cook time entered. Skipping cook time filter.[/yellow]")

    difficulty = Prompt.ask("Difficulty level (easy/medium/hard)", default="")
    dietary = Prompt.ask("Dietary preference", default="")
    cuisine = Prompt.ask("Cuisine type", default="")
    
    filtered = filter_recipes(
        cook_time=max_time_int,
        difficulty=difficulty if difficulty else None,
        dietary=dietary if dietary else None,
        cuisine=cuisine if cuisine else None
    )
    
    if not filtered:
        console.print("\n[red]No recipes match your filters.[/red]")
        return
    
    # Display recipes
    recipe_table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
    recipe_table.add_column("#", style="dim", width=3)
    recipe_table.add_column("Recipe Name", style="yellow")
    recipe_table.add_column("Cuisine", style="cyan")
    recipe_table.add_column("Cook Time", justify="center")
    recipe_table.add_column("Difficulty", justify="center")
    
    for idx, recipe in enumerate(filtered, 1):
        recipe_table.add_row(
            str(idx),
            recipe["name"],
            recipe["cuisine"],
            f"{recipe['cook_time']} min",
            recipe["difficulty"]
        )
    
    console.print(f"\n[bold green]Found {len(filtered)} recipes:[/bold green]\n")
    console.print(recipe_table)
    
    # View details
    if Confirm.ask("\nView recipe details?"):
        recipe_num = Prompt.ask("Enter recipe number")
        try:
            idx = int(recipe_num) - 1
            if 0 <= idx < len(filtered):
                display_recipe(filtered[idx])
                
                if Confirm.ask("Save this recipe?"):
                    saved_recipes = SavedRecipes()
                    if saved_recipes.add_recipe(filtered[idx]):
                        console.print("[green]✓ Recipe saved![/green]")
        except ValueError:
            console.print("[red]Invalid selection.[/red]")


def main_menu():
    """Display main menu and handle user choices."""
    while True:
        console.print("\n[bold cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold cyan]")
        console.print("[bold]What would you like to do?[/bold]\n")
        console.print("[cyan]1.[/cyan] 🔍 Find recipes by ingredients")
        console.print("[cyan]2.[/cyan] 🤖 Generate custom recipe with AI")
        console.print("[cyan]3.[/cyan] 📅 Meal planning")
        console.print("[cyan]4.[/cyan] 🥫 Pantry manager")
        console.print("[cyan]5.[/cyan] 💾 View saved recipes")
        console.print("[cyan]6.[/cyan] 📖 Browse all recipes")
        console.print("[cyan]7.[/cyan] 🏆 View achievements")
        console.print("[cyan]8.[/cyan] 📊 Gamification status")
        console.print("[cyan]9.[/cyan] 💡 AI cooking tips")
        console.print("[cyan]10.[/cyan] 🔁 Ingredient substitutions")
        console.print("[cyan]11.[/cyan] 🚪 Exit")
        console.print("[bold cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold cyan]")
        
        choice = Prompt.ask("\nSelect an option", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"])
        
        if choice == "1":
            find_recipes_menu()
        elif choice == "2":
            ai_recipe_menu()
        elif choice == "3":
            meal_planning_menu()
        elif choice == "4":
            pantry_menu()
        elif choice == "5":
            saved_recipes_menu()
        elif choice == "6":
            browse_all_recipes()
        elif choice == "7":
            display_achievements_menu()
        elif choice == "8":
            display_gamification_status()
        elif choice == "9":
            ai_cooking_tips_menu()
        elif choice == "10":
            ingredient_substitutions_menu()
        elif choice == "11":
            console.print("\n[bold cyan]Thanks for using AI Chef! Happy cooking! 👨‍🍳[/bold cyan]\n")
            break


def main():
    """Main application entry point."""
    display_banner()
    console.print("[dim]Making cooking easier, one recipe at a time...[/dim]\n")
    
    # Load environment variables
    load_dotenv()
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[yellow]⚠️  Note: OPENAI_API_KEY not found. AI features will be limited.[/yellow]")
        console.print("[dim]Set up your API key in a .env file to enable AI recipe generation.[/dim]\n")
    
    try:
        main_menu()
    except KeyboardInterrupt:
        console.print("\n\n[bold cyan]Goodbye! 👋[/bold cyan]\n")
    except Exception as e:
        console.print(f"\n[red]An error occurred: {str(e)}[/red]\n")


if __name__ == "__main__":
    main()
