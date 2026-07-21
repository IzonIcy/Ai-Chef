# AI Chef

A terminal app that helps you figure out what to cook based on ingredients you already have.

I built this because I kept buying groceries without a plan, letting food go bad, and then ordering takeout. Turns out the problem wasn't lack of recipes — it was that looking through cookbooks for "what can I make with chicken, rice, and broccoli" takes forever. So I made something that does it instantly.

## What it does

- **Recipe finder** — tell it what ingredients you have, it tells you what you can make and what else you'd need
- **AI recipe generator** — describe a craving, GPT writes you a custom recipe (optional, needs an API key)
- **Meal planner** — generates a weekly plan + grocery list based on your dietary preferences
- **Filters** — by cook time, difficulty, dietary restrictions, cuisine

## Running it

```bash
pip install -r requirements.txt
python ai_chef.py
```

If you want AI generation, create a `.env` file:

```
OPENAI_API_KEY=sk-your-key-here
```

The recipe finder works without it. The AI generation is the fun part though.

## Tech

Python 3.8+, OpenAI API, Rich for the terminal UI. Recipes live in a JSON file because SQLite felt like overkill for something I can edit by hand.

## What I learned

This was my first project working with LLM APIs. The most interesting part was prompt engineering for recipe generation — getting the model to output structured, parsable recipes instead of prose paragraphs took some iteration. The fallback path (no API key) forced me to make the core recipe matching solid on its own, which was a good constraint.

## Maybe later

- Save AI recipes to the database
- Nutritional info
- Export shopping lists
- More built-in recipes
