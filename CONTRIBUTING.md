# Contributing

Thanks for looking at Ai-Chef. It's a small, deliberately simple project — seven
flat modules and no framework — so contributions should stay in that spirit.

## Getting set up

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

`pyproject.toml` is the only dependency manifest. Please don't add a
`requirements.txt`; a second copy just drifts out of sync with CI.

## Before you open a PR

```bash
mise run check
```

That runs `ruff check`, `ruff format --check`, `mypy`, and `pytest` — the same
four gates CI runs. If you don't have mise, run them individually in that order.

## Ground rules

- **One concern per commit.** If your commit message needs the word "also",
  split it into two commits.
- **Tests accompany behaviour changes.** A bug fix starts with a failing test
  that reproduces the bug, then the fix.
- **The AI path is optional.** Every feature must still work with
  `OPENAI_API_KEY` unset. Please don't add a hard dependency on the API.
- **Model output is untrusted.** Parse it defensively and keep the non-AI
  fallback working.
- **User data goes through `json_store` and `data_dir`.** Don't call `open()` for
  user data, and don't write anything into the repo directory at runtime.
- If you add a module, register it in three places: `[tool.mypy] files`,
  `[tool.setuptools] py-modules`, and the `COPY` list in the `Dockerfile`.

## Style

`ruff format` owns formatting — don't hand-tune quotes or wrapping. `ruff check`
handles import order and most lint. Beyond that, match the surrounding code:
plain functions, no classes where a function does, explicit over clever.

## Reporting bugs

Open an issue with what you did, what you expected, and what happened instead,
plus your OS and Python version. If it involves the AI path, include whether
`OPENAI_API_KEY` was set — the fallback path behaves differently on purpose.
