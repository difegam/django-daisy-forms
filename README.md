<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/difegam/django-daisy-forms/main/docs/assets/logo-dark.svg">
    <img alt="django-daisy-forms" src="https://raw.githubusercontent.com/difegam/django-daisy-forms/main/docs/assets/logo.svg" width="420">
  </picture>
</p>

<h3 align="center">daisyUI 5 forms for Django.</h3>

<p align="center">
  Render daisyUI 5 markup from Django's own form renderer and <code>BoundField</code>
  APIs. Point one setting at the daisy renderer and your existing
  <code>{{ form }}</code> and <code>{{ formset }}</code> templates keep working.
</p>

<p align="center">
  <a href="https://pypi.org/project/django-daisy-forms/"><img alt="PyPI" src="https://img.shields.io/pypi/v/django-daisy-forms"></a>
  <img alt="Python 3.12+" src="https://img.shields.io/badge/python-3.12%2B-44D19A">
  <img alt="Django 5.2 | 6.0 | 6.1" src="https://img.shields.io/badge/django-5.2%20%7C%206.0%20%7C%206.1-0C4B33">
  <img alt="daisyUI 5" src="https://img.shields.io/badge/daisyUI-5-FFC94A">
  <img alt="Tailwind CSS 4.1+" src="https://img.shields.io/badge/tailwind-4.1%2B-38BDF8">
  <a href="https://github.com/difegam/django-daisy-forms/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/difegam/django-daisy-forms/actions/workflows/ci.yml/badge.svg"></a>
  <a href="https://github.com/difegam/django-daisy-forms/blob/main/LICENSE"><img alt="MIT licence" src="https://img.shields.io/badge/license-MIT-9B8CFF"></a>
</p>

<p align="center">
  <a href="#quickstart">Quickstart</a> ·
  <a href="#why-django-daisy-forms">Why</a> ·
  <a href="#features">Features</a> ·
  <a href="#layouts-and-addons">Layouts</a> ·
  <a href="#support">Support</a> ·
  <a href="#development">Development</a>
</p>

<p align="center">
  <img alt="django-daisy-forms in 30 seconds: one setting turns a plain Django form into daisyUI, server errors render accessibly, a template tag customizes fields, and a generated Tailwind source file keeps the CSS in sync" src="https://raw.githubusercontent.com/difegam/django-daisy-forms/main/docs/assets/demo.gif" width="720">
</p>

## Quickstart

Install the package with uv or pip:

```bash
uv add django-daisy-forms
# or
python -m pip install django-daisy-forms
```

Configure the renderer in the project settings. Django's
[`FORM_RENDERER`](https://docs.djangoproject.com/en/stable/ref/settings/#form-renderer)
setting selects the renderer used by every form and formset:

```python
INSTALLED_APPS = [
    # ...
    "django.forms",
    "daisy_forms",
]

FORM_RENDERER = "daisy_forms.renderers.DaisyFormRenderer"
```

Then render `{{ form }}` as usual. `python manage.py check` reports
`daisy_forms.E001` when `django.forms` is missing from `INSTALLED_APPS`, and
`daisy_forms.W001` when `FORM_RENDERER` is not the daisy renderer.

## Why django-daisy-forms

- **One setting.** `FORM_RENDERER` switches every `{{ form }}`, `{{ formset }}`
  and `{{ form.field.as_field_group }}` to daisyUI markup. No FormHelper, no
  layout DSL.
- **Built on Django's APIs.** A class registry gives each widget its daisyUI
  component through a custom `BoundField`. Django's global widget templates are
  never overridden, and custom widgets are left alone.
- **The server has the final say.** Errors come from Django validation and use
  the same `aria-invalid` and `aria-describedby` ids Django already generates.
- **One tag for per-field control.** `{% daisy_field %}` merges classes, passes
  attributes such as `hx-*`, and opts fields into horizontal layouts, inline
  choices, or text addons. It refuses inline event handlers.
- **CSS that can't drift.** A management command writes the Tailwind
  `@source inline()` file, and `--check` fails CI when it is out of date.
- **Small footprint.** One runtime dependency, Django, and no JavaScript.

## Features

### Rendering

Each Django widget gets its daisyUI component class: `input`, `textarea`,
`select`, `checkbox`, `radio`, `toggle`, `file-input`, and `range`. Fields with
errors also get the matching `-error` variant. `daisy_forms.widgets` adds
`Toggle` plus native `NativeDateInput`, `NativeTimeInput`, and
`NativeDateTimeInput` widgets. Help text is escaped unless it is marked safe.

<p align="center">
  <img alt="A plain Django form is scanned into daisyUI markup while each widget is labelled with its class: EmailInput to input, RadioSelect to radio, Select to select, NativeDateInput to input, Toggle to toggle" src="https://raw.githubusercontent.com/difegam/django-daisy-forms/main/docs/assets/demo/render.gif" width="880">
</p>

### Validation

Server-side validation stays authoritative. Invalid fields render with
`aria-invalid="true"`, error lists use the `{id}_error` ids that
`aria-describedby` references, and controls switch to their `-error` class.
When using htmx, return a `422` with the re-rendered field group; no htmx
dependency is required. For whole-form submissions, see the
[HTMX validation recipe](https://github.com/difegam/django-daisy-forms/blob/main/docs/recipes/htmx-form-validation.md).

<p align="center">
  <img alt="Submitting an invalid email returns 422 and the form re-renders with input-error, aria-invalid, and aria-describedby; fixing the email and choosing a plan returns 200" src="https://raw.githubusercontent.com/difegam/django-daisy-forms/main/docs/assets/demo/validate.gif" width="880">
</p>

### Per-field control

For one-off fields, load the tag library and pass normal widget attributes:

```django
{% load daisy_forms %}
{% daisy_field form.email class+="input-sm" hx-post="/validate/email/" hx-trigger="blur" %}
```

`class+=` merges with the daisyUI classes, and `label=` and `template=`
override the label and the field template. `label_class=` appends classes to
the field's main label (or choice-group legend); it does not style individual
choice labels. The package's default and horizontal templates render it;
custom field templates must use `field.label_class` themselves. Add the class
to your Tailwind source or safelist if your project does not otherwise use it.
Every other name becomes a widget attribute except `label`, `label_class`,
`template`, `choices`, `prefix`, and `suffix`. Inline handlers (`on*`, `hx-on*`,
`x-on*`, `x-init`) and the managed `aria-invalid` and `aria-describedby`
attributes raise a `TemplateSyntaxError` when the template is compiled.

<p align="center">
  <img alt="The daisy_field tag renders an input with input-sm and hx attributes, then a field with onclick fails with TemplateSyntaxError: Attribute is not allowed: onclick" src="https://raw.githubusercontent.com/difegam/django-daisy-forms/main/docs/assets/demo/field.gif" width="880">
</p>

### Layouts and addons

Fields stay stacked by default. Opt into a horizontal field, inline choices, or
text addons where they help the form:

```django
{% load daisy_forms %}
{% daisy_field form.email template="daisy_forms/field_horizontal.html" %}
{% daisy_field form.plan choices="inline" %}
{% daisy_field form.features choices="inline" %}
{% daisy_field form.price prefix="$" suffix="USD" %}
```

<p align="center">
  <img alt="Before and after: default stacked form fields compared with horizontal labels, inline choices, and price addons" src="https://raw.githubusercontent.com/difegam/django-daisy-forms/main/docs/images/forms-before-after.png" width="880">
</p>

- **Horizontal fields.** `field_horizontal.html` stacks the label and control on
  narrow screens and places them side by side from the `md` breakpoint.
- **Inline choices.** `choices="inline"` lays out stock `RadioSelect` and
  `CheckboxSelectMultiple` options in a wrapping row.
- **Text addons.** `prefix` and `suffix` join plain text to stock single-line
  widgets styled with daisyUI's `input` component. Values are escaped, so pass
  `$` or `kg` rather than HTML. Addons copy the input's size, color, and error
  modifiers, so `class+="input-sm"` or a validation error styles the whole
  group.

Unsupported combinations, such as `choices="grid"`, `choices` on a select, or
`prefix` on a hidden, checkbox, or radio field, raise a `TemplateSyntaxError`
when the field renders. The layout classes are part of the `daisy_forms_css`
output, so regenerate that file when upgrading the package.

### Composed forms

Use ordinary Django template markup to group fields and place actions. This
keeps the form structure in the project, with no package layout API:

```django
{% load daisy_forms %}
<form method="post">
  {% csrf_token %}
  <fieldset>
    <legend>Account</legend>
    {% daisy_field form.email template="daisy_forms/field_horizontal.html" label_class="font-semibold" %}
  </fieldset>
  <fieldset>
    <legend>Plan and features</legend>
    {% daisy_field form.plan choices="inline" %}
    {% daisy_field form.features choices="inline" %}
  </fieldset>
  <div class="flex flex-col gap-3 sm:flex-row sm:justify-end">
    <button class="btn btn-ghost" type="reset">Reset</button>
    <button class="btn btn-primary" type="submit">Save</button>
  </div>
</form>
```

### Tailwind CSS

The package requires Tailwind CSS 4.1 or later and daisyUI 5.0.36 or later.
Tailwind does not scan `site-packages`, so the package ships its classes as a
source file. Generate it in the project that owns the Tailwind build:

```bash
python manage.py daisy_forms_css --output static/src/daisy-forms.css
```

Import the generated file after Tailwind and daisyUI:

```css
@import "tailwindcss";
@plugin "daisyui";
@import "./daisy-forms.css";
```

Then check it in CI:

```bash
python manage.py daisy_forms_css --output static/src/daisy-forms.css --check
```

<p align="center">
  <img alt="daisy_forms_css writes an @source inline file listing every class the package emits, and the --check run exits cleanly" src="https://raw.githubusercontent.com/difegam/django-daisy-forms/main/docs/assets/demo/css.gif" width="880">
</p>

### Themes

The markup uses daisyUI component classes only, so any daisyUI theme applies
through `data-theme` with nothing to configure in the package.

<p align="center">
  <img alt="The same signup form switching between the dark, cupcake, synthwave, nord, and retro daisyUI themes" src="https://raw.githubusercontent.com/difegam/django-daisy-forms/main/docs/assets/demo/themes.gif" width="520">
</p>

## Support

| Requirement | Supported |
| --- | --- |
| Python | 3.12 or later |
| Django | 5.2, 6.0, 6.1 |
| Tailwind CSS | 4.1 or later |
| daisyUI | 5.0.36 or later |

The package has one runtime dependency, Django. Tailwind CSS and daisyUI remain
dependencies of the project that consumes this package.

## Development

Install [uv](https://docs.astral.sh/uv/) and [Just](https://just.systems/),
then run:

```bash
just init
just check
```

`just init` installs every dependency group and the pre-commit, pre-push, and
commit-msg hooks. `just fresh` removes the environment and caches first.

The available commands are:

```text
just format     Format Python files with Ruff.
just lint       Run Ruff linting.
just typecheck  Run strict mypy with django-stubs.
just test       Run pytest.
just css-check  Build the Tailwind and daisyUI fixture.
just css-preview  Build the fixture CSS for the browser preview.
just check      Run formatting, linting, type checks, and tests.
just build      Build wheel and source-distribution artifacts.
just verify     Run every check CI runs: check, css-check, build, and docs.
just release-notes  Draft the next release's changelog and notes with Claude.

just init       Install all dependency groups and the Git hooks.
just clean      Remove the virtualenv, caches, and build output.
just fresh      Run clean, then init.

just doc-serve         Preview the documentation site locally.
just doc-build         Build the documentation, failing on warnings.
just doc-format        Format the docs Markdown with mdformat.
just doc-format-check  Check the docs Markdown formatting.

just browser-setup    Install Playwright, Chromium, and the browser CLI.
just browser-test     Run the opt-in browser checks for form layouts.
just browser-preview  Serve the layout preview at 127.0.0.1:8000/__preview__/.
just browser-cli      Open the preview in the pinned Playwright CLI.
```

Run `just update` to upgrade the lockfile within declared dependency
constraints and sync all development groups.

For optional local browser validation of the form layouts, use Node 20 or later,
install the browser tools and Chromium, then run the browser checks:

```bash
just browser-setup
just browser-test
```

To inspect the live preview with the pinned Playwright CLI, run `just
browser-preview` in one terminal and `just browser-cli` in another. The browser
checks are opt-in and stay out of the default test and CI runs.

Prek runs Ruff, djlint, codespell, shellcheck, bandit, and file checks before
commits, validates commit messages, and runs strict mypy, coverage, and link
checks before pushes. CI runs the declared Django and Python matrix, builds
both release artifacts and smoke tests them in isolated environments, checks
the Tailwind fixture, and builds the documentation strictly.

<details>
<summary><strong>Releasing</strong></summary>

Run `just release-notes` to draft the release with the
[Claude Code](https://docs.claude.com/en/docs/claude-code) CLI. The script
collects the commits, diffs, and CHANGELOG sections since the latest tag, then
runs `claude -p` with all tools disabled. It writes a suggested version bump, a
CHANGELOG entry, and GitHub release notes to `.release/release.md`. Pass
`--dry-run` to write only the context and prompt, or `--from`/`--to` to choose
the range.

Review the draft, add its entries to CHANGELOG.md under a
`## [X.Y.Z] - YYYY-MM-DD` heading, and update the link references. Then run
`just bump-patch`, `just bump-minor`, or `just bump-major` to update the
package version and lockfile. Merge the changes to `main` through a pull
request, then push a matching semantic version tag such as `v0.1.1`.

The release workflow checks that the tag matches the package version, rebuilds
and smoke-tests the wheel and source distribution, adds provenance attestations,
and publishes through PyPI Trusted Publishing. Before the first release,
configure a PyPI trusted publisher for this GitHub repository and the `pypi`
GitHub Actions environment.

</details>

## License

MIT. See [LICENSE](https://github.com/difegam/django-daisy-forms/blob/main/LICENSE).
