# Ingredient extraction results

## Baseline

No baseline recorded.

The machine that built this eval has no OpenAI key and no local Ollama, so
`python scripts/eval_ingredients.py` exits with one line: `No AI endpoint set.
Set OPENAI_API_KEY or OPENAI_BASE_URL (for Ollama).` No score here is measured.
Do not add one by hand.

## Recording one

Run from the repository root against any OpenAI-compatible vision endpoint:

```bash
OPENAI_API_KEY=sk-... .venv/bin/python scripts/eval_ingredients.py
```

Against a local server:

```bash
OPENAI_BASE_URL=http://localhost:11434/v1 OPENAI_MODEL=llava \
  .venv/bin/python scripts/eval_ingredients.py
```

Paste the summary line under "Baseline" with the model name, the date and the
commit SHA, so a later run has a number to beat. A real run costs 20 requests.

## What is measured

The `--photo` path turns a picture into bare ingredient names. This repository
ships no photo set, so `eval/ingredient_cases.tsv` holds 20 kitchen scenes as
written descriptions, each with the ingredient names a person reading that
scene would list. The description stands in for the picture, and the script
sends it through the same extraction function `--photo` uses, marked as no
photo being available. A score here covers the prompt and the reply parsing.
It says nothing about a vision model's reading of pixels.

Every expected name is a bare lowercase name that appears in `recipes.py`
ingredients, so a hit is a name the recipe matcher can use.

## Scoring rules

Both sides are lowercased and whitespace-collapsed, then compared as sets.

- Precision is the share of the model's names that are labelled. An empty
  reply scores 0.
- Recall is the share of the labelled names the model found.
- Exact set match is true only when the two sets are equal.
- Overall accuracy is the mean of precision, the mean of recall, and the share
  of cases that matched exactly.
- Synonyms are not folded. `tomato` and `tomatoes` are separate names, so a
  model that says one where the label says the other loses on both sides.

`python scripts/eval_ingredients.py --dry-run` validates the labels file and
prints the case count without calling a model.
