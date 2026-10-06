# django-daisy-forms

`django-daisy-forms` will provide Django-native daisyUI form rendering without
django-crispy-forms. The renderer, templates, and `daisy_forms_css` management
command are not implemented yet. The repository now has its development and
release tooling in place.

## Support policy

The package targets Python 3.12 or later and Django 5.2, 6.0, and 6.1. It has
one runtime dependency, Django. Tailwind CSS and daisyUI remain dependencies of
the project that consumes this package.

## Planned consumer setup

Once the renderer implementation is released, projects will configure:

```python
INSTALLED_APPS = [
    # ...
    "django.forms",
    "daisy_forms",
]

FORM_RENDERER = "daisy_forms.renderers.DaisyFormRenderer"
```

The package will require Tailwind CSS 4.1 or later. Its future
`daisy_forms_css` command will generate an `@source inline()` file containing
the daisyUI classes used by package templates. Consumer projects will import
that generated file into their Tailwind stylesheet and run
`daisy_forms_css --check` in CI after package upgrades.

## Contributor setup

Install [uv](https://docs.astral.sh/uv/) and [Just](https://just.systems/),
then run:

```bash
uv sync --all-groups
uv run prek install
just check
```

The available commands are:

```text
just format     Format Python files with Ruff.
just lint       Run Ruff linting.
just typecheck  Run strict mypy with django-stubs.
just test       Run pytest.
just check      Run formatting, linting, type checks, and tests.
just build      Build wheel and source-distribution artifacts.
```

Prek runs Ruff and whitespace, YAML, and TOML checks before commits. CI runs
the declared Django and Python matrix, builds both release artifacts, and smoke
tests them in isolated environments.

## Releases

Push a semantic version tag such as `v0.1.0` after CI is green. The release
workflow rebuilds and smoke-tests the artifacts, adds provenance attestations,
and publishes through PyPI Trusted Publishing. Configure the `pypi` GitHub
Actions environment with PyPI before pushing the first release tag.

## License

MIT. See [LICENSE](LICENSE).
