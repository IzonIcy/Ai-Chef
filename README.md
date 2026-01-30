# AI Chef 🍳

So basically I got tired of staring at my fridge wondering what to make for dinner, and thought - why not build something to help with that? AI Chef is my attempt at making a cooking assistant that actually helps you figure out what to cook based on what you already have.

The idea is pretty simple: you tell it what ingredients you've got, and it suggests recipes. Or if you're feeling adventurous, you can use AI to generate completely custom recipes. There's also meal planning stuff because I always forget to plan ahead.

## What it does

- Finds recipes based on whatever ingredients you have lying around
- Generates custom recipes with AI (when you want something specific)
- Helps you plan out your meals for the week
- Makes grocery lists so you don't forget half the stuff at the store
- Filters recipes by time, difficulty, dietary restrictions, etc.
- Lets you save your favorite recipes

## Why I made this

Honestly? I was wasting so much food and money because I'd buy ingredients without a plan. This helps me actually use what I have, try new things, and not spend 30 minutes every night deciding what to eat. Plus it was a fun way to learn more about working with AI APIs.

## Getting Started

You'll need Python 3.8 or newer installed. For the AI features, you'll also need an OpenAI API key (but the app still works without it - you just won't be able to generate custom recipes).

### Setup

Clone this repo:
```bash
git clone https://github.com/yourusername/Ai-Chef.git
cd Ai-Chef
```

Install the required packages:
```bash
pip install -r requirements.txt
```

If you want to use the AI recipe generator, create a `.env` file and add your OpenAI API key:
```
OPENAI_API_KEY=your-api-key-here
```

(You can also just export it as an environment variable if you prefer)

### Running it

Just run:
```bash
python ai_chef.py
```

The interface is pretty self-explanatory - it'll walk you through the options.

## How it looks

When you run it, you get a menu like this:

```
Welcome to AI Chef! 🍳

What would you like to do?
1. Find recipes by ingredients
2. Generate a custom recipe with AI
3. Plan my weekly meals
4. View saved recipes
5. Exit

> 1

Enter ingredients you have (comma-separated): chicken, rice, broccoli

Found 3 recipes matching your ingredients:
- Chicken Stir-Fry with Broccoli
- Garlic Chicken and Rice
- One-Pan Chicken Broccoli Rice
```

Pretty straightforward stuff.

## Tech used

- Python 3.8+
- OpenAI API (for the AI recipe generation)
- Rich library (makes the terminal output look nice)
- python-dotenv (for managing the API key)

## Features breakdown

**Recipe Finder** - Type in what ingredients you have and it'll match them against a database of recipes. Shows you what percentage of ingredients you have and what you're missing.

**AI Recipe Generator** - This is the cool part. You can describe what you want (like "something spicy with shrimp" or "a quick vegetarian dinner") and it'll generate a complete recipe for you using GPT.

**Meal Planning** - Creates a weekly meal plan for you. You can filter by dietary preferences and cooking time. Then it'll generate a grocery list of everything you need.

**Filters** - Search by cooking time, difficulty, dietary stuff (vegan, gluten-free, etc.), or cuisine type.

The app saves your favorite recipes and meal plans to JSON files so they stick around between sessions.

## Contributing

If you want to add features or fix bugs, feel free to open a PR. Would love to see what others come up with!

Some ideas I had but haven't gotten to yet:
- Saving custom recipes to the database
- Nutritional information for recipes
- Shopping list export to different formats
- More recipes in the database
- Possibly Making A App For Mac?

## License

MIT License - If your showing it to someone, please tell them that i made this.

## Notes

Built this as a side project to solve a real problem I was having. My friend helped me come up with the initial concept. If you have suggestions or find bugs, let me know!

The recipe database currently has about 10 recipes built in, but the AI generator can create unlimited new ones if you have an API key.
