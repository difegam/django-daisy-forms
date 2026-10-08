# Development

This section covers how to set up a development environment and work on django-daisy-forms.

## Setting up the development environment

Install [uv](https://docs.astral.sh/uv/) and [Just](https://just.systems/), then run:

```bash
just init
just check
```

`just init` installs every dependency group (test, lint, type checking, docs, and browser) and the pre-commit, pre-push, and commit-msg Git hooks. `just fresh` removes the virtual environment and caches first, then runs `init`.

## Available commands

```text
just format     Format Python files with Ruff.
just lint       Run Ruff linting.
just typecheck  Run strict mypy with django-stubs.
just test       Run pytest with coverage.
just check      Run formatting, linting, type checks, and tests.
just css-check  Build the Tailwind and daisyUI fixture.
just css-preview  Build the fixture CSS for the browser preview.
just build      Build wheel and source-distribution artifacts.
just verify     Run every check CI runs: check, css-check, build, and docs.

just init       Install all dependency groups and the Git hooks.
just clean      Remove the virtualenv, caches, and build output.
just fresh      Run clean, then init.
just update     Upgrade the lockfile within declared constraints.

just doc-serve         Preview the documentation site locally.
just doc-build         Build the documentation, failing on warnings.
just doc-llms          Generate llms.txt and page markdown into site/ (after doc-build).
just doc-format        Format the docs Markdown with mdformat.
just doc-format-check  Check the docs Markdown formatting.

just browser-setup    Install Playwright, Chromium, and the browser CLI.
just browser-test     Run the opt-in browser checks for form layouts.
just browser-preview  Serve the layout preview at 127.0.0.1:8000/__preview__/.
just browser-cli      Open the preview in the pinned Playwright CLI.

just release-notes  Draft the next release's changelog and notes with Claude.
just bump-patch     Bump the package version (also bump-minor, bump-major).
```

## Testing

```bash
just test
```

This runs pytest with coverage. The project requires at least 94% coverage.

For optional browser validation of the form layouts, use Node 20 or later:

```bash
just browser-setup
just browser-test
```

To inspect the live preview with the pinned Playwright CLI, run `just browser-preview` in one terminal and `just browser-cli` in another. The browser checks are opt-in and stay out of the default test and CI runs.

## Git hooks

[prek](https://github.com/j178/prek) runs the hooks in `.pre-commit-config.yaml`:

- **Before each commit:** whitespace, end-of-file, YAML, TOML, and JSON checks; Ruff format and lint; bandit; djlint on Django templates (the package templates and golden files are linted but never reformatted); codespell; shellcheck; and the test suite.
- **On the commit message:** commitizen checks that it follows [Conventional Commits](https://www.conventionalcommits.org/).
- **Before each push:** strict mypy, the coverage check, and a link check of the Markdown.
- **On demand:** `just doc-format` (or `uv run prek run mdformat --hook-stage manual --all-files`) formats the docs Markdown.

## Continuous integration

CI runs on every pull request and on `main`:

- Ruff, strict mypy, and pytest across Python 3.12, 3.13, and 3.14 and Django 5.2, 6.0, and 6.1.
- A build of the wheel and source distribution, with a smoke test of each in an isolated environment.
- The Tailwind fixture against daisyUI 5.0.36 and 5.7.47, checking that every package class is in the compiled CSS.
- A strict documentation build and a Markdown formatting check.

Merges to `main` deploy this documentation site to GitHub Pages. Pushing a `v*` tag runs the release workflow; see [Contributing](contributing.md#release-process).

## Documentation

The site is built with [Zensical](https://zensical.org/) from `docs/` and `zensical.toml`:

```bash
just doc-serve         # Live preview at http://localhost:8000
just doc-format        # Format the Markdown
just doc-build         # Strict build; fails on warnings
just doc-llms          # Generate site/llms.txt (run after doc-build)
```

The changelog page includes the repository's `CHANGELOG.md`, and the template reference includes the package templates directly, so neither needs to be copied by hand. `scripts/llms-txt.sh` builds `llms.txt` from the `nav` in `zensical.toml` and copies each page's Markdown next to it, so the file stays in sync with the docs and is published by the same workflow.
