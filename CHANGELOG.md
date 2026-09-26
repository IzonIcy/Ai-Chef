# Changelog

All notable changes to this project are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
versioning follows [SemVer](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

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
- `AGENTS.md` is tracked in git and rewritten to describe the architecture and
  conventions of the project. The duplicate `.github/copilot-instructions.md`
  was removed so there is a single source of truth for agent instructions.

## [1.0.0]

- Initial release: recipe finder, AI recipe generator, weekly meal planner with
  grocery list export, and gamification (streaks, achievements, challenges).
- Atomic JSON persistence via a shared `json_store` module.
- Per-user data directory (XDG on Linux, App Support on macOS).
- User-defined recipes, recipe scaling, and CSV/Markdown grocery export.
