FROM python:3.13-slim

WORKDIR /app

# Dependencies come from pyproject.toml, the single source of truth.
COPY pyproject.toml README.md ./
COPY ai_chef.py ai_generator.py data_dir.py gamification.py json_store.py meal_planner.py recipes.py ./

RUN pip install --no-cache-dir . \
    && useradd --create-home --uid 1000 chef \
    && chown -R chef:chef /app

USER chef

CMD ["python", "ai_chef.py"]
