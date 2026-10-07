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
    uv run pytest --cov

css-check:
    PYTHONPATH=. uv run django-admin daisy_forms_css --settings=tests.settings --skip-checks --output tests/tailwind/daisy-forms.css
    npm --prefix tests/tailwind ci
    npm --prefix tests/tailwind run build
    uv run python tests/tailwind/check_css.py

check: format-check lint typecheck test

build:
    uv build --no-sources
