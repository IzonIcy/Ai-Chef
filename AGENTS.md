# Ai-Chef — Terminal Cooking Assistant

A terminal app that answers "what can I make with chicken, rice, and broccoli?"
without making you scroll through a cookbook.

## Quick Start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python ai_chef.py
```

Requires Python 3.12+ (CI runs 3.13). `mise install` sets up the pinned
toolchain if you use [mise](https://mise.jdx.dev).

## Architecture

Seven modules, flat and deliberately shallow. No framework, no ORM.

| Module            | Responsibility                                                             |
| ----------------- | -------------------------------------------------------------------------- |
| `ai_chef.py`      | Entry point. Rich TUI, menu dispatch, user prompts.                        |
| `ai_generator.py` | OpenAI calls + response parsing (JSON, with a text fallback).              |
| `recipes.py`      | Recipe data model, ingredient matching, text search, portion scaling.      |
| `meal_planner.py` | Weekly plans, grocery list generation, CSV/Markdown export.                |
| `gamification.py` | Streaks, achievements, weekly challenges.                                  |
| `json_store.py`   | Atomic JSON read/write. All persistence funnels through here.              |
| `data_dir.py`     | Resolves the per-user data directory (XDG on Linux, App Support on macOS). |

### Conventions

- **`json_store` owns all disk writes.** Never call `open()` for user data
  elsewhere. It writes to a temp file and renames, so a crash mid-write can't
  corrupt state.
- **User data lives in the data dir, never the repo.** `data_dir.get_data_dir()`
  is the only thing that should construct a path. The repo-level `*.json` names
  in `.gitignore` are belt-and-braces for people who ran old versions.
- **The AI path is optional.** Every feature degrades to a working non-AI path
  when `OPENAI_API_KEY` is unset. Don't let a refactor break that.
- **Parsing is defensive.** Model output is untrusted. `_try_parse_json_recipe`
  falls back to line-prefix parsing; both paths normalise through
  `_normalize_recipe`.

## Development

`pyproject.toml` is the **single source of truth** for dependencies. There is
deliberately no `requirements.txt` — Dependabot updates one file, and a second
copy silently drifts out of sync with CI.

```bash
mise run check     # ruff check + format check + mypy + pytest  (what CI runs)
mise run fix       # ruff --fix + ruff format
```

Individually:

```bash
ruff check .
ruff format --check .
mypy               # scoped to the modules above via `files` in pyproject
python -m pytest
```

### Testing notes

`mypy` is scoped with an explicit `files` list rather than run as `mypy .`.
Walking site-packages makes it hard-fail on syntax errors inside third-party
stubs (numpy's stubs use PEP 695 `type` statements) before checking any of our
code — which is exactly how a type check silently stops type checking.

If you add a module, add it to both `[tool.mypy] files` and
`[tool.setuptools] py-modules`, plus the `COPY` list in the `Dockerfile`.

## Conventions for changes

- One concern per commit. If the message needs the word "also", split it.
- Tests accompany behaviour changes. A bug fix starts with a failing test.
- `ruff format` is enforced by pre-commit and CI — run `mise run fix` before
  pushing rather than after.
- Bump the version in `pyproject.toml` and add a `CHANGELOG.md` entry in the
  same commit as a user-visible change.

## Adding a recipe

Built-in recipes live in `RECIPE_DATABASE` in `recipes.py`. A user-added recipe
goes to `user_recipes.json` in the data dir via `recipes.py`, and the two are
merged at read time — so a built-in addition and a user recipe never collide on
write.

Two things to get right, both enforced by `tests/test_recipe_library.py` and
`tests/test_scaling_amounts.py`:

- **`ingredients` are bare lowercase names with no quantities** — "chicken", not
  "1.5 lbs chicken". `find_recipes_by_ingredients` and the grocery categoriser
  match on these strings exactly, so a quantity in here silently breaks
  matching.
- **Quantities live in the `amounts` sidecar**, a dict mapping each ingredient
  name to a quantity string ("1.5 lbs"). `scale_recipe` scales that and renders
  "3 lbs chicken" for display. Every ingredient needs an entry, and each
  quantity must start with a number so the scaler can read it.
