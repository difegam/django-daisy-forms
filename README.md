# django-daisy-forms

`django-daisy-forms` provides Django-native daisyUI 5 form rendering without
django-crispy-forms. It uses Django's form renderer and `BoundField` APIs, so
existing `{{ form }}` and `{{ formset }}` templates keep working.

## Support policy

The package targets Python 3.12 or later and Django 5.2, 6.0, and 6.1. It has
one runtime dependency, Django. Tailwind CSS and daisyUI remain dependencies of
the project that consumes this package.

## Installation

After the first release is published to PyPI, install the package with uv or
pip:

```bash
uv add django-daisy-forms
# or
python -m pip install django-daisy-forms
```

## Consumer setup

Configure the renderer in the project settings:

```python
INSTALLED_APPS = [
    # ...
    "django.forms",
    "daisy_forms",
]

FORM_RENDERER = "daisy_forms.renderers.DaisyFormRenderer"
```

The package requires Tailwind CSS 4.1 or later and daisyUI 5.0.36 or later.
Generate the class source file in the project that owns the Tailwind build:

```bash
python manage.py daisy_forms_css --output static/src/daisy-forms.css
```

Import the generated file after Tailwind and daisyUI, then check it in CI:

```css
@import "tailwindcss";
@plugin "daisyui";
@import "./daisy-forms.css";
```

```bash
python manage.py daisy_forms_css --output static/src/daisy-forms.css --check
```

For one-off fields, load the tag library and pass normal widget attributes:

```django
{% load daisy_forms %}
{% daisy_field form.email class+="input-sm" hx-post="/validate/email/" hx-trigger="blur" %}
```

The package keeps server-side validation authoritative. Return a `422` with
the re-rendered field group when using htmx; no htmx dependency is required.

## Layout examples

The default keeps fields stacked vertically. Opt into a horizontal field,
inline radio choices, or text addons where they help the form:

![Before and after: default stacked form fields compared with horizontal labels, inline choices, and price addons](docs/images/forms-before-after.png)

```django
{% load daisy_forms %}
{% daisy_field form.email template="daisy_forms/field_horizontal.html" %}
{% daisy_field form.plan choices="inline" %}
{% daisy_field form.price prefix="$" suffix="USD" %}
```

Inline choices apply to radio and checkbox choice fields. Prefixes and suffixes
are plain text addons for supported single-line inputs; the values are escaped
by Django's template engine. Fields remain stacked by default.

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
just css-check  Build the Tailwind and daisyUI fixture.
just check      Run formatting, linting, type checks, and tests.
just build      Build wheel and source-distribution artifacts.
```

Run `just update` to upgrade the lockfile within declared dependency
constraints and sync all development groups.

Prek runs Ruff and whitespace, YAML, and TOML checks before commits. CI runs
the declared Django and Python matrix, builds both release artifacts, and smoke
tests them in isolated environments.

## Releases

Choose the release level and run `just bump-patch`, `just bump-minor`, or
`just bump-major`. These recipes use `uv version --bump` to update the package
version and lockfile. Review and commit the changes, merge them to `main`, then
push a matching semantic version tag such as `v0.1.0`. The release workflow
checks that the tag matches the package version, rebuilds and smoke-tests the
wheel and source distribution, adds provenance attestations, and publishes
through PyPI Trusted Publishing. Before the first release, configure a PyPI
trusted publisher for this GitHub repository and the `pypi` GitHub Actions
environment.

## License

MIT. See [LICENSE](LICENSE).
