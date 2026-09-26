# Changelog

All notable changes to this project are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
versioning follows [SemVer](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- Scaling a recipe down to a single unit rendered "1 cups broccoli". Known
  plural units are now singularised when the count is exactly one, using an
  explicit map rather than a "drop the trailing s" rule.
- Short search terms no longer match inside unrelated words. "asi" used to hit
  every instruction containing "roasting"; matching is now on word prefixes, so
  "asi" finds "Asian" and "chick" finds "chicken" without matching "aside".

## [1.2.0] - 2026-09-25

Search, a bigger library, and three correctness fixes.

### Added

- Free-text recipe search across the merged built-in and user recipe set.
  Case-insensitive substring matching over name, cuisine, ingredients, and
  instructions, with every term required to match so multi-word queries stay
  precise. Name hits outrank ingredient hits, which outrank instruction hits.
  An empty query browses everything and lists the cuisines available.
- `recipes.all_cuisines()` for discovering what is in the library.
- The browse menu takes a search query before its existing filters, and
  `filter_recipes` accepts a `pool` so search results can be narrowed further.
- Nine new built-in recipes, bringing the library to 19 across 11 cuisines:
  Thai, Indian, Japanese, Greek, and French dishes, plus more vegan options.
- Library integrity tests covering required keys, unique names, filterable
  difficulty values, known dietary tags, and bare lowercase ingredient names.

### Fixed

- Weekly meal plans no longer fall back to the entire recipe database when
  nothing matches the filters, which meant asking for a keto plan returned a
  week of beef. The cook time cap is now relaxed first since it is only a
  preference, and an unsatisfiable dietary restriction raises with a clear
  message instead of being silently ignored.
- Weekly plans actually vary cuisine. The docstring claimed they did, but the
  code indexed straight into the candidate list in database order.
- Portion scaling now scales built-in recipes. Built-in ingredients are stored
  as bare names so ingredient matching and grocery categorisation keep working,
  which left nowhere for a quantity, so scaling doubled the servings and
  changed nothing else. Recipes now carry an `amounts` sidecar.
- The ingredient finder and the browse menu shared no filter code, so a rule
  change had to be made twice and the finder's copy could not filter by
  cuisine. Both now go through `filter_recipes`.
- Cuisine filtering matches on substrings, so `asi` finds `Asian`.

## [1.1.0] - 2026-09-25

Maintenance release. No new features; the app behaves the same except that the
AI menus now explain themselves when no API key is set.

### Fixed

- The AI cooking tips and ingredient substitutions menus prompted for input
  before checking for an API key, then rendered the generator's "key not set"
  message inside a Panel where it read like a real answer. Both now report the
  missing key up front and exit, matching the existing behaviour of the custom
  recipe menu.
- `mypy` was failing on a syntax error inside a third-party stub (numpy uses
  PEP 695 `type` statements) before it checked any project code, so the type
  check in CI was silently checking nothing. Mypy is now scoped to the project's
  own modules via an explicit `files` list.
- Corrected five untyped containers that mypy flagged once it was actually
  running: the recipe accumulators in `ai_generator.py`, `used_recipes` and
  `grocery_list` in `meal_planner.py`, and `instructions` in `ai_chef.py`.
- Repository-wide `ruff format` compliance. Pre-commit enforced formatting but
  the tree had drifted, so hooks would have rewritten files on first run.

### Changed

- `pyproject.toml` is now the only dependency manifest; `requirements.txt` is
  deleted. The two had drifted onto different major versions of `openai` and
  `rich`, meaning CI and local development were exercising different SDKs.
- Dependencies moved forward to the majors the code is tested against:
  `openai>=3.3,<4`, `rich>=15,<16`, `python-dotenv>=1.2,<2`.
- Minimum supported Python is 3.12, matching `python_version` in the mypy and
  ruff configuration.
- CI installs the project with `pip install -e ".[dev]"` and adds a
  `ruff format --check` step.
- `Dockerfile` installs the project from `pyproject.toml` instead of
  `requirements.txt`, and CI now builds the image and smoke-tests the entrypoint
  so it cannot silently rot.

### Added

- `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`.
- `mise run check` and `mise run fix` tasks wrapping the CI gates.
- `tests/test_ai_chef_menus.py` covering the TUI-level API key guards.
- `AGENTS.md` is tracked in git and rewritten to describe the architecture and
  conventions of the project. The duplicate `.github/copilot-instructions.md`
  was removed so there is a single source of truth for agent instructions.

## [1.0.0]

- Initial release: recipe finder, AI recipe generator, weekly meal planner with
  grocery list export, and gamification (streaks, achievements, challenges).
- Atomic JSON persistence via a shared `json_store` module.
- Per-user data directory (XDG on Linux, App Support on macOS).
- User-defined recipes, recipe scaling, and CSV/Markdown grocery export.
