# Development

This section covers how to set up a development environment and contribute to django-daisy-forms.

## Setting up the development environment

Install [uv](https://docs.astral.sh/uv/) and [Just](https://just.systems/), then run:

```bash
uv sync --all-groups
uv run prek install
just check
```

This installs all dependencies (test, lint, type-checking, and browser groups), sets up pre-commit hooks, and runs the full check suite.

## Available commands

```text
just format     Format Python files with Ruff.
just lint       Run Ruff linting.
just typecheck  Run strict mypy with django-stubs.
just test       Run pytest.
just css-check  Build the Tailwind and daisyUI fixture.
just css-preview  Build the fixture CSS for the browser preview.
just check      Run formatting, linting, type checks, and tests.
just build      Build wheel and source-distribution artifacts.

just browser-setup    Install Playwright, Chromium, and the browser CLI.
just browser-test     Run the opt-in browser checks for form layouts.
just browser-preview  Serve the layout preview at 127.0.0.1:8000/__preview__/.
just browser-cli      Open the preview in the pinned Playwright CLI.
```

Run `just update` to upgrade the lockfile within declared dependency constraints and sync all development groups.

## Browser tests

For optional local browser validation of the form layouts, use Node 20 or later:

```bash
just browser-setup
just browser-test
```

To inspect the live preview with the pinned Playwright CLI, run `just browser-preview` in one terminal and `just browser-cli` in another. The browser checks are opt-in and stay out of the default test and CI runs.

## Testing

Run the test suite:

```bash
just test
```

This runs pytest with coverage. The project requires 94% coverage minimum.

To run tests including the optional browser checks:

```bash
just browser-test
```

## Code quality

Run the full check suite (formatting, linting, type-checking, tests):

```bash
just check
```

Individual checks:

```bash
just format-check  # Check formatting without modifying files
just format        # Format files
just lint          # Run Ruff linting
just typecheck     # Run strict mypy with django-stubs
```

## Building

Build wheel and source-distribution artifacts:

```bash
just build
```

## Updating dependencies

Upgrade the lockfile within declared constraints and sync all development groups:

```bash
just update
```

Prek runs Ruff and whitespace, YAML, and TOML checks before commits. CI runs the declared Django and Python matrix, builds both release artifacts, and smoke tests them in isolated environments.
