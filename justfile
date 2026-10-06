[private]
format-check:
    uv run ruff format --check .

format:
    uv run ruff format .

lint:
    uv run ruff check .

typecheck:
    uv run mypy --strict src/daisy_forms tests

test:
    uv run pytest

check: format-check lint typecheck test

build:
    uv build --no-sources
