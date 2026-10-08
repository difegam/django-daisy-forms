[doc("Install all dependency groups and the Git hooks")]
init:
    uv sync --locked --all-groups
    uv run prek install --hook-type pre-commit --hook-type pre-push --hook-type commit-msg

[doc("Remove the virtualenv, caches, and build output")]
clean:
    rm -rf .venv .pytest_cache .ruff_cache .mypy_cache .coverage htmlcov site dist
    find . -type d -name "__pycache__" -exec rm -rf {} +

[doc("Rebuild the environment from scratch")]
fresh: clean init

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
    uv sync --locked --all-groups
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
    scripts/release-notes.sh {{ args }}

[doc("Bump the package patch version with uv")]
bump-patch:
    uv version --bump patch

[doc("Bump the package minor version with uv")]
bump-minor:
    uv version --bump minor

[doc("Bump the package major version with uv")]
bump-major:
    uv version --bump major

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
