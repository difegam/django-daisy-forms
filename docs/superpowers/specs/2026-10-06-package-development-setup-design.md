# Package development setup design

## Purpose

Set up `django-daisy-forms` as a publishable Django application. The project
will implement the renderer described in
`docs/django-daisy-forms.md`, support Python 3.12 and later, and support Django
5.2, 6.0, and 6.1.

This document defines the repository tooling only. It does not implement the
renderer, its templates, or its public API.

## Decisions

The repository uses `uv` and `uv_build` for dependency management and package
builds. It uses a `src` layout with the import package named `daisy_forms`.
The current starter import package, `django_daisy_forms`, and its console
script entry point do not match the intended API and will be replaced.

`pyproject.toml` is the source of truth for package metadata and tool
configuration. It will include:

- Python floor of 3.12 and Django runtime dependency floor of 5.2.
- MIT SPDX license metadata, project URLs, classifiers, keywords, and a useful
  package description.
- `uv_build` as the build backend.
- Dependency groups for `test`, `lint`, `type`, and an aggregate `dev` group.
- Configuration for pytest, Ruff, mypy, and coverage.

The initial package has one runtime dependency: Django. Tailwind CSS and
daisyUI remain consumer-side requirements and are documented rather than added
to the Python distribution.

## Repository layout

```text
src/daisy_forms/                 # publishable Django application
tests/                           # test settings, fixtures, and tests
.github/workflows/ci.yml         # pull request and main quality checks
.github/workflows/release.yml    # tagged PyPI publication
.pre-commit-config.yaml          # prek hooks
justfile                         # short local command aliases
docs/superpowers/specs/          # approved design records
```

The package includes `py.typed` and its Django templates. Distribution smoke
tests verify that both the wheel and source distribution contain those files.

The test settings module lives in `tests.settings`. It configures the smallest
Django installation that can exercise the public renderer integration. The
repository does not add Docker, a database service, a demo project, browser
tests, JavaScript, or Node tooling in this phase.

## Quality tools

Ruff provides formatting and linting. It targets Python 3.12 and checks the
source and test directories. Its rule selection covers imports, bug-prone code,
Django issues, security concerns, annotations, and supported-Python upgrades.
Test-only exceptions are narrowly scoped, such as allowing `assert`.

Mypy is the sole type checker. It runs in strict mode and uses
`django-stubs` with the Django settings module in `tests.settings`.
Configuration applies strict rules to `src/daisy_forms`; only test-specific
exceptions may be added when needed for fixtures. It must not silence missing
types globally.

Pyre, Pyrefly, and ty are not included. Unit Bridge has both Pyrefly and ty
configuration, but maintaining more than one type checker would create
duplicated and inconsistent diagnostics for this library.

Pytest and pytest-django test the package through actual Django forms. Tests
use `assertHTMLEqual` for markup, cover renderer configuration, template tags,
system checks, Tailwind class-registry generation, escaping, and distribution
contents.

`prek` runs the quick local checks: Ruff formatting, Ruff linting, whitespace
cleanup, and YAML and TOML validation. It does not run the full test matrix.

## Commands

The optional `justfile` gives each command one job:

```text
just format     Run Ruff formatting.
just lint       Run Ruff linting.
just typecheck  Run strict mypy.
just test       Run pytest.
just check      Check formatting, linting, types, and tests.
just build      Build without local source overrides.
```

Contributor setup is:

```text
uv sync --all-groups
uv run prek install
just check
```

## Continuous integration and releases

The CI workflow runs on pull requests and pushes to `main`. It installs from
the committed lockfile, checks Ruff formatting, runs Ruff lint and strict
mypy, and runs pytest over an explicit Django and Python compatibility matrix.
The matrix covers Django 5.2, 6.0, and 6.1 on the Python versions officially
supported by each release.

CI builds the wheel and source distribution with `uv build --no-sources`. It
then installs each artifact in an isolated environment and runs a smoke test
that imports `daisy_forms` and renders a basic Django form. This catches
missing package data and source-layout errors that source-tree tests cannot.

A version tag runs the same checks, then publishes with PyPI Trusted
Publishing. The workflow uploads build artifacts, creates provenance
attestations, and grants `id-token: write` only to the publication job.

## Failure behavior and exclusions

The setup catches stale lockfiles, style regressions, type errors, broken
renderer imports, missing templates, absent type markers, and missing Tailwind
source output before release. It fails closed: a release cannot publish after
any quality or distribution check fails.

The README documents the support matrix, installation, renderer setup,
Tailwind 4.1 source-file workflow, local commands, and release procedure. It
separates maintainer checks from consumer integration steps.

## Reference review

Unit Bridge is useful as a reference for `uv` dependency groups, `prek`,
Ruff, pytest-django, small command aliases, a locked dependency workflow, and
pinned GitHub Actions. It is an application with Postgres, Docker, Node, and
browser testing, so those parts do not transfer to this library.

The choices here follow current documentation for
[Ruff](https://docs.astral.sh/ruff/configuration/),
[mypy](https://mypy.readthedocs.io/en/stable/config_file.html),
[uv packaging](https://docs.astral.sh/uv/guides/package/),
[Django reusable applications](https://docs.djangoproject.com/en/stable/intro/reusable-apps/),
and [pytest-django](https://pytest-django.readthedocs.io/).
