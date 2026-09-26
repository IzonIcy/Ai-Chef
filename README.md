# AI Chef

[![CI](https://github.com/IzonIcy/Ai-Chef/actions/workflows/ci.yml/badge.svg)](https://github.com/IzonIcy/Ai-Chef/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](pyproject.toml)

A terminal app that helps you figure out what to cook based on ingredients you
already have.

I built this because I kept buying groceries without a plan, letting food go bad,
and then ordering takeout. Turns out the problem wasn't lack of recipes — it was
that looking through cookbooks for "what can I make with chicken, rice, and
broccoli" takes forever. So I made something that does it instantly.

## What it does

- **Recipe finder** — tell it what ingredients you have, it tells you what you
  can make and what else you'd need
- **Recipe search** — free-text search by name, cuisine, or ingredient across
  19 built-in recipes plus your own
- **AI recipe generator** — describe a craving, GPT writes you a custom recipe
  (optional, needs an API key)
- **Meal planner** — generates a weekly plan and a grocery list from your
  dietary preferences, exported as CSV or Markdown
- **Filters** — by cook time, difficulty, dietary restrictions, cuisine
- **Gamification** — cooking streaks, achievements, and weekly challenges
- **Portion scaling** — scale any recipe up or down, quantities included

## Running it

Requires Python 3.12 or newer.

```bash
git clone https://github.com/IzonIcy/Ai-Chef.git
cd Ai-Chef
python -m venv .venv && source .venv/bin/activate
pip install -e .
python ai_chef.py
```

### Optional: AI features

Every feature works without an API key. The recipe finder, meal planner,
grocery export, scaling, and gamification are entirely local. The three
AI-backed features — custom recipe generation, cooking tips, and ingredient
substitutions — tell you they need a key and exit cleanly, rather than failing
somewhere in the middle. That's deliberate, so the app is useful without paying
for anything.

To enable the AI features, copy the example env file and fill in your key:

```bash
cp .env.example .env
```

```
OPENAI_API_KEY=sk-your-key-here
```

## Docker

```bash
docker build -t ai-chef .
docker run -it ai-chef
```

Pass the key in with `-e OPENAI_API_KEY=sk-...` if you want the AI path. Your
recipes and plans are written to the data dir inside the container, so mount a
volume to `/home/chef/.local/share/ai-chef` to keep them.

## Development

`pyproject.toml` is the single source of truth for dependencies. Run the same
gates CI runs with:

```bash
pip install -e ".[dev]"
mise run check
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the conventions a change should
follow, and [AGENTS.md](AGENTS.md) for how the modules fit together.

## Tech

Python 3.12+, the OpenAI SDK, and Rich for the terminal UI. Built-in recipes
live in code; your own recipes, plans, and pantry live in the platform data
directory (`~/.local/share/ai-chef` on Linux, `~/Library/Application
Support/ai-chef` on macOS). SQLite felt like overkill for a JSON file I can edit
by hand — `json_store` writes atomically, so a crash mid-write can't corrupt it.

## What I learned

This was my first project working with LLM APIs. The most interesting part was
prompt engineering for recipe generation — getting the model to output
structured, parsable recipes instead of prose paragraphs took some iteration,
and the defensive parsing path in `ai_generator.py` is the scar tissue from that.

The other thing I got wrong early: the project had two dependency manifests that
quietly drifted onto different major versions of the SDK, so CI and my laptop
were testing different code. One source of truth, or neither.

## Maybe later

- Importing recipes from a URL
- Nutrition info per serving
- A proper `CONTRIBUTING` wishlist of beginner-friendly issues

## License

MIT — see [LICENSE](LICENSE).
