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

browser-setup:
    uv sync --locked --group dev --group browser
    uv run playwright install chromium
    npm ci --prefix tests/browser-cli
    npm --prefix tests/browser-cli exec -- playwright-cli install-browser chromium

css-preview: css-check
    npm --prefix tests/tailwind run build:preview

browser-test: css-preview
    uv run pytest --override-ini addopts= -m browser tests/browser

browser-preview: css-preview
    PYTHONPATH=. uv run django-admin runserver --skip-checks --settings=tests.settings 127.0.0.1:8000

browser-cli:
    npm --prefix tests/browser-cli exec -- playwright-cli open http://127.0.0.1:8000/__preview__/ --headed

check: format-check lint typecheck test

build:
    uv build --no-sources

[doc("Upgrade dependencies within their declared constraints")]
update:
    uv lock --upgrade && uv sync --all-groups

[doc("Draft the changelog entry, version bump and release notes with Claude")]
release-notes *args:
    scripts/release-notes.sh {{args}}

[doc("Bump the package patch version with uv")]
bump-patch:
    uv version --bump patch

[doc("Bump the package minor version with uv")]
bump-minor:
    uv version --bump minor

[doc("Bump the package major version with uv")]
bump-major:
    uv version --bump major
