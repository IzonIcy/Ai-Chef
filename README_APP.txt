# AI Chef macOS App

Native SwiftUI app for AI Chef, powered by the same Python backend used by the CLI.

## Overview

The macOS app adds a native interface while keeping your original Python project structure and logic intact.

- Native SwiftUI UI for recipe workflows
- JSON-based subprocess bridge (no API server)
- Shared backend with the CLI
- Easy extension path for new features

## Quick Start

From the repository root:

```bash
cd /Users/ryanbahadori/Documents/GitHub/Ai-Chef
chmod +x setup_macos_app.sh
./setup_macos_app.sh
open .
```

In Xcode, press `Cmd+R` to build and run.

## Core Features

### Find Recipes
- Search by comma-separated ingredients
- View matching recipes and details
- Save favorites

### Generate Recipes
- Describe what you want to cook
- Generate custom recipes via OpenAI

### Meal Planner
- Plan meals for breakfast/lunch/dinner/snacks
- Organize week-level meal plans

### Saved Recipes
- Persist favorite recipes
- Search and revisit saved items

## Architecture

```text
SwiftUI App (macOS)
        ↓
macos_app/PythonBridge.swift
        ↓
python3 app_bridge.py <command>
        ↓
app_bridge.py
        ↓
Python modules (recipes.py, ai_generator.py, meal_planner.py, ai_chef.py)
```

## Key Files

### App Layer
- `macos_app/AiChef_Updated.swift` — main SwiftUI app
- `macos_app/PythonBridge.swift` — subprocess execution + JSON handling

### Python Layer
- `app_bridge.py` — command router used by Swift
- `recipes.py` — recipe data/search/filter logic
- `ai_generator.py` — OpenAI recipe/tips integration
- `meal_planner.py` — planning + saved recipes behavior
- `ai_chef.py` — terminal CLI

### Setup and Docs
- `setup_macos_app.sh` — setup automation
- `QUICK_START.md` — short setup reference
- `MACOS_APP_GUIDE.md` — full architecture/troubleshooting guide
- `APP_SETUP_COMPLETE.md` — setup summary

## Validation Commands

Run from project root:

```bash
python3 app_bridge.py get_all_recipes
python3 app_bridge.py find_recipes '["chicken", "rice"]'
python3 app_bridge.py generate_recipe "quick pasta dinner"
python3 ai_chef.py
```

## Troubleshooting

### Python not found in app
- Update interpreter path in `macos_app/PythonBridge.swift`
- Verify interpreter path:

```bash
which python3
```

### App cannot find recipes or modules
- Ensure you run from repository root
- Confirm `recipes.py` and related modules exist at top-level

### OpenAI generation fails
- Ensure `.env` includes:

```env
OPENAI_API_KEY=sk-your-key
```

- Restart the app after environment changes

### Python changes do not appear in app
- Quit and relaunch app (`Cmd+Q`, then reopen)

## Checklist

Before build:
- Python 3.8+ installed
- Xcode installed
- `setup_macos_app.sh` executable

After setup:
- `python3 app_bridge.py get_all_recipes` returns valid JSON
- Project opens in Xcode
- App builds with `Cmd+R`

After run:
- Ingredient search works
- AI generation works (with valid key)
- CLI still runs (`python3 ai_chef.py`)

## Notes

- App and CLI share one backend codebase.
- Backend changes in Python affect both interfaces.
- Keep UI behavior in Swift and domain logic in Python modules.

---

Status: Ready to use
Version: 1.0
