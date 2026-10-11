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

Run `just` with no arguments to list every recipe with its description, grouped
by purpose:

| Group     | Recipes                                                                    | Use it to                                                                 |
| --------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| `setup`   | `init`, `clean`, `fresh`, `update`                                         | Install or rebuild the environment and upgrade the lockfile               |
| `dev`     | `format`, `format-check`, `lint`, `typecheck`, `test`, `check`, `build`    | Format, lint, type check, test, and build the distributions               |
| `css`     | `css-check`, `css-preview`                                                 | Build the Tailwind and daisyUI fixture and check the package classes      |
| `browser` | `browser-setup`, `browser-test`, `browser-preview`, `browser-cli`          | Run and inspect the opt-in browser checks                                 |
| `docs`    | `doc-serve`, `doc-build`, `doc-llms`, `doc-format`, `doc-format-check`     | Preview, build, and format this site                                      |
| `release` | `release-notes`, `bump-patch`, `bump-minor`, `bump-major`, `skill-refresh` | Prepare a release; see [Release process](contributing.md#release-process) |
| `ci`      | `verify`                                                                   | Run every check that CI runs before opening a pull request                |

`just check` is the everyday entry point. `just update` upgrades the lockfile
within the declared dependency constraints and syncs all development groups.
Give every new recipe a `[doc("...")]` description and a `[group("...")]`
attribute so it shows up in the right place in `just`.

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

## Agent skill

The repository ships an agent skill in `skills/django-daisy-forms`, published
through the `skills` CLI (see [AI integration](../ai-integration.md#agent-skill)).
Its `metadata.version` must equal the package version:

- `tests/test_skill.py` checks the version, the frontmatter, and the reference
    links.
- The `skill-version` pre-commit hook runs when `pyproject.toml` or the skill's
    `SKILL.md` is staged, and rejects a commit whose versions differ.
- `just skill-refresh` prints a prompt for Claude Code or Codex. The agent reads
    the git history since the skill was last updated, updates the skill, and
    sets its version with `scripts/sync-skill-version.sh`.

When a change affects settings, the template tag, widgets, the management
command, system checks, or error messages, update the skill in the same pull
request.

## Documentation

The site is built with [Zensical](https://zensical.org/) from `docs/` and `zensical.toml`:

```bash
just doc-serve         # Live preview at http://localhost:8000
just doc-format        # Format the Markdown
just doc-build         # Strict build; fails on warnings
just doc-llms          # Generate site/llms.txt (run after doc-build)
```

The changelog page includes the repository's `CHANGELOG.md`, and the template reference includes the package templates directly, so neither needs to be copied by hand. `scripts/llms-txt.sh` builds `llms.txt` from the `nav` in `zensical.toml` and copies each page's Markdown next to it, so the file stays in sync with the docs and is published by the same workflow.
