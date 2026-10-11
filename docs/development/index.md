# Development

This section covers how to set up a development environment and work on django-daisy-forms.

## Setting up the development environment

Install [uv](https://docs.astral.sh/uv/) and [Just](https://just.systems/), then run:

```bash
just init
just check
```

`just init` installs every dependency group (test, lint, type checking, docs, and browser) and sets up Git hooks. `just fresh` removes the virtual environment and caches first, then runs init.

## Available commands

Run `just` with no arguments to list all recipes grouped by purpose:

| Group   | Recipes                                                          | Purpose                                   |
| ------- | ---------------------------------------------------------------- | ----------------------------------------- |
| setup   | init, clean, fresh, update                                       | Install or rebuild the environment        |
| dev     | format, format-check, lint, typecheck, test, check, build        | Format, lint, type check, test, and build |
| css     | css-check, css-preview                                           | Check package classes in compiled CSS     |
| browser | browser-setup, browser-test, browser-preview, browser-cli        | Run browser validation checks             |
| docs    | doc-serve, doc-build, doc-llms, doc-format, doc-format-check     | Preview, build, and format docs           |
| release | release-notes, bump-patch, bump-minor, bump-major, skill-refresh | Prepare a release                         |
| ci      | verify                                                           | Run all pre-PR checks                     |

`just check` is the everyday entry point. `just update` upgrades the lockfile
within the declared dependency constraints and syncs all development groups.
Give every new recipe a `[doc("...")]` description and a `[group("...")]`
attribute so it shows up in the right place in `just`.

## Testing

```bash
just test
```

This runs pytest with coverage. The project requires at least 94% coverage. For optional browser validation of layouts, use Node 20 or later:

```bash
just browser-setup
just browser-test
```

To inspect the live preview, run `just browser-preview` and `just browser-cli` in separate terminals. Browser checks are opt-in and do not run by default in CI.

## Git hooks

[prek](https://github.com/j178/prek) runs hooks from `.pre-commit-config.yaml`. Before each commit, it runs whitespace and YAML/TOML/JSON checks, Ruff, bandit, djlint on templates, codespell, shellcheck, and the test suite. The commit message hook enforces [Conventional Commits](https://www.conventionalcommits.org/). Before each push, it runs strict mypy, the coverage check, and Markdown link validation. Use `just doc-format` to format the docs.

## Continuous integration

CI runs on every pull request and on main. It runs Ruff, strict mypy, and pytest across Python 3.12, 3.13, and 3.14 with Django 5.2, 6.0, and 6.1. It builds and smoke-tests both wheel and source distributions, checks the Tailwind fixture against daisyUI 5.0.36 and 5.7.47, runs a strict docs build, and checks Markdown formatting. Merges to main deploy the documentation to GitHub Pages. Pushing a v\* tag runs the release workflow. See [Contributing](contributing.md#release-process).

## Agent skill

An agent skill lives in `skills/django-daisy-forms`, published through the skills CLI (see [AI integration](../ai-integration.md#agent-skill)). Its version must match the package version. `tests/test_skill.py` checks the version and frontmatter. The `skill-version` pre-commit hook rejects commits whose versions differ. Run `just skill-refresh` to generate a prompt for Claude Code, which updates the skill and syncs its version. When a change affects settings, the template tag, widgets, the management command, system checks, or error messages, update the skill in the same pull request.

## Documentation

The site is built with [Zensical](https://zensical.org/) from `docs/` and `zensical.toml`:

```bash
just doc-serve         # Live preview at http://localhost:8000
just doc-format        # Format the Markdown
just doc-build         # Strict build; fails on warnings
just doc-llms          # Generate site/llms.txt (run after doc-build)
```

The changelog includes `CHANGELOG.md` and the template reference includes package templates directly, so neither needs to be copied manually. `scripts/llms-txt.sh` builds `llms.txt` from `zensical.toml` and copies each page's Markdown next to it, keeping the file in sync.
