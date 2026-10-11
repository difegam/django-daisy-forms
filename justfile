# List available recipes
[private]
default:
    @just --list --list-submodules

# Setup
[doc("Install all dependency groups and the Git hooks")]
[group("setup")]
init:
    uv sync --locked --all-groups
    uv run prek install --hook-type pre-commit --hook-type pre-push --hook-type commit-msg

[doc("Remove the virtualenv, caches, and build output")]
[group("setup")]
clean:
    rm -rf .venv .pytest_cache .ruff_cache .mypy_cache .coverage htmlcov site dist
    find . -type d -name "__pycache__" -exec rm -rf {} +

[doc("Rebuild the environment from scratch")]
[group("setup")]
fresh: clean init

[doc("Upgrade dependencies within their declared constraints")]
[group("setup")]
update:
    uv lock --upgrade && uv sync --all-groups

# Development
[doc("Check Python formatting with Ruff")]
[group("dev")]
format-check:
    uv run ruff format --check .

[doc("Format Python files with Ruff")]
[group("dev")]
format:
    uv run ruff format .

[doc("Run Ruff linting")]
[group("dev")]
lint:
    uv run ruff check .

[doc("Run strict mypy with django-stubs")]
[group("dev")]
typecheck:
    uv run mypy --strict src/daisy_forms tests

[doc("Run pytest with coverage")]
[group("dev")]
test:
    uv run pytest --cov

[doc("Run formatting, linting, type checks, and tests")]
[group("dev")]
check: format-check lint typecheck test

[doc("Build wheel and source-distribution artifacts")]
[group("dev")]
build:
    uv build --no-sources

# Tailwind CSS fixture
[doc("Build the Tailwind and daisyUI fixture and check every package class")]
[group("css")]
css-check:
    PYTHONPATH=. uv run django-admin daisy_forms_css --settings=tests.settings --skip-checks --output tests/tailwind/daisy-forms.css
    npm --prefix tests/tailwind ci
    npm --prefix tests/tailwind run build
    uv run python tests/tailwind/check_css.py

[doc("Build the fixture CSS for the browser preview")]
[group("css")]
css-preview: css-check
    npm --prefix tests/tailwind run build:preview

# Browser checks
[doc("Install Playwright, Chromium, and the browser CLI")]
[group("browser")]
browser-setup:
    uv sync --locked --all-groups
    uv run playwright install chromium
    npm ci --prefix tests/browser-cli
    npm --prefix tests/browser-cli exec -- playwright-cli install-browser chromium

[doc("Run the opt-in browser checks for form layouts")]
[group("browser")]
browser-test: css-preview
    uv run pytest --override-ini addopts= -m browser tests/browser

[doc("Serve the layout preview at 127.0.0.1:8000/__preview__/")]
[group("browser")]
browser-preview: css-preview
    PYTHONPATH=. uv run django-admin runserver --skip-checks --settings=tests.settings 127.0.0.1:8000

[doc("Open the preview in the pinned Playwright CLI")]
[group("browser")]
browser-cli:
    npm --prefix tests/browser-cli exec -- playwright-cli open http://127.0.0.1:8000/__preview__/ --headed

# Release
[doc("Draft the changelog entry, version bump and release notes with Claude")]
[group("release")]
release-notes *args:
    scripts/release-notes.sh {{ args }}

[doc("Print an agent prompt to update the skill after a version bump")]
[group("release")]
skill-refresh:
    scripts/skill-refresh-prompt.sh

[doc("Bump the package patch version with uv")]
[group("release")]
bump-patch:
    uv version --bump patch
    @echo "The agent skill is now behind the package. Run: just skill-refresh"

[doc("Bump the package minor version with uv")]
[group("release")]
bump-minor:
    uv version --bump minor
    @echo "The agent skill is now behind the package. Run: just skill-refresh"

[doc("Bump the package major version with uv")]
[group("release")]
bump-major:
    uv version --bump major
    @echo "The agent skill is now behind the package. Run: just skill-refresh"

[doc("Run every local check that CI runs")]
[group("ci")]
verify: check css-check build doc-build doc-llms doc-format-check

# Documentation
[doc("Preview documentation locally")]
[group("docs")]
doc-serve:
    uv run --group docs zensical serve -a localhost:1031

[doc("Build documentation (fail on warnings)")]
[group("docs")]
doc-build:
    uv run --group docs zensical build --clean --strict

[doc("Generate llms.txt into the built site (run after doc-build)")]
[group("docs")]
doc-llms *args:
    scripts/llms-txt.sh {{ args }}

[doc("Format documentation markdown files")]
[group("docs")]
doc-format:
    uvx --from mdformat==1.0.0 --with mdformat-gfm==1.0.0 --with mdformat-front-matters==2.0.0 --with mdformat-footnote==0.1.3 --with mdformat-mkdocs==5.3.0 mdformat --number docs

[doc("Check documentation markdown formatting")]
[group("docs")]
doc-format-check:
    uvx --from mdformat==1.0.0 --with mdformat-gfm==1.0.0 --with mdformat-front-matters==2.0.0 --with mdformat-footnote==0.1.3 --with mdformat-mkdocs==5.3.0 mdformat --number --check docs
