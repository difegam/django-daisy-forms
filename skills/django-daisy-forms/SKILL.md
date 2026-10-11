---
name: django-daisy-forms
description: >-
  Use when installing, configuring, writing templates for, or reviewing code that uses
  django-daisy-forms (daisyUI 5 forms for Django): FORM_RENDERER, DaisyFormRenderer,
  {% daisy_field %}, daisy_forms_css and Tailwind @source, Toggle or Native date widgets,
  htmx form validation, or errors such as daisy_forms.E001, daisy_forms.W001,
  "Attribute is not allowed", or unstyled Django form fields.
argument-hint: "[setup|form|tailwind|htmx|review] [path]"
license: MIT
metadata:
  version: "0.1.0"
---

# django-daisy-forms

django-daisy-forms renders daisyUI 5 markup through Django's own form renderer. One
setting switches every `{{ form }}`, `{{ formset }}` and `{{ field.as_field_group }}`.
The renderer adds the daisyUI classes, error variants and ARIA attributes. Templates
never write them by hand.

This skill describes django-daisy-forms **0.1.0**. Its version always equals the
package release it documents. Before writing code, compare it with the installed
package (`uv pip show django-daisy-forms` or `python -m pip show django-daisy-forms`):

- **Same version:** follow this skill.
- **Installed package is newer:** read the
  [changelog](https://github.com/difegam/django-daisy-forms/blob/main/CHANGELOG.md)
  entries after this version and the current docs at
  <https://difegam.github.io/django-daisy-forms/llms.txt>. Where they disagree with
  this skill, the docs win. Tell the user to run `npx skills update django-daisy-forms`.
- **Installed package is older:** features described here may be missing. Check the
  changelog before using them, and suggest upgrading the package.
- **Not installed:** follow `setup`. It installs the latest release.

The header of a generated `daisy-forms.css` file also names the package version
that wrote it.

Requirements: Python 3.12+, Django 5.2–6.1, Tailwind CSS 4.1+, daisyUI 5.0.36+.

## Modes

The first argument picks the mode. Without one, infer it from the task. The second
argument is a settings file, template, form module or directory to work on.

| Mode | Use for | Read |
| --- | --- | --- |
| `setup` | Install and configure the package in a project | [setup](references/setup.md), then `tailwind` |
| `form` | Write or change forms and templates | [fields](references/fields.md) |
| `tailwind` | Generate the CSS source file, wire the import, add the CI check | [tailwind](references/tailwind.md) |
| `htmx` | Server-side validation with htmx, per field or whole form | [htmx](references/htmx.md), [fields](references/fields.md) |
| `review` | Audit templates, forms and settings | Review checklist below, [troubleshooting](references/troubleshooting.md) |

## Facts agents get wrong

- The renderer is `FORM_RENDERER = "daisy_forms.renderers.DaisyFormRenderer"`, not
  `TemplatesSetting`. `INSTALLED_APPS` needs both `"django.forms"` and `"daisy_forms"`.
- Tailwind never scans `site-packages`. Generate the class list with
  `python manage.py daisy_forms_css --output <path>` and `@import` that file after
  daisyUI. Never add an `@source` that points into `.venv` or `site-packages`.
- Render fields with `{{ form }}` or `{% daisy_field form.x %}`. Never hand-write
  `<input>`, `<select>` or `<textarea>` markup for a form field, and never add component
  classes such as `input`, `select`, `textarea`, `checkbox`, `radio` or `toggle`. The
  renderer adds them. `input-bordered` is a daisyUI 4 class and does not exist in daisyUI 5.
- `{% daisy_field %}` has built-in options: `label=`, `label_class=`, `template=`,
  `choices="inline"`, `prefix=` and `suffix=`. Use them instead of custom markup.
- `class=` and `class+=` both append to the daisyUI classes. Neither replaces them.
- These attributes raise `TemplateSyntaxError` when the template compiles: `on*`,
  `hx-on*`, `x-on*`, `x-init` (with or without a `data-` prefix), `aria-invalid` and
  `aria-describedby`. Use `hx-*` attributes or a script, and use `help_text` to describe
  a field.
- `prefix`/`suffix` work only on stock single-line inputs (text, email, number, URL…).
  `choices="inline"` works only on stock `RadioSelect` and `CheckboxSelectMultiple`.
  Any other combination raises `TemplateSyntaxError`.
- Quote string values: `prefix="$"`. An unquoted value is a template variable. Tags
  cannot nest, so resolve URLs first with `{% url 'name' as some_url %}`, then pass
  `hx-post=some_url`.
- htmx 2 does not swap `4xx` responses by default. For invalid input, return `422` with
  the re-rendered fragment and enable the `422` swap in `htmx.config.responseHandling`.

## Workflow

1. Read the target files and the project's settings before changing anything.
2. Follow the reference for the mode.
3. Verify:
   - `python manage.py check` reports no `daisy_forms.*` messages.
   - `python manage.py daisy_forms_css --output <path> --check` passes once Tailwind is wired.
   - Rendered HTML shows daisyUI classes. The project's Tailwind build includes them.
   - Run the project's tests.
4. Report what changed and anything the user must do, such as rebuilding CSS or
   installing Tailwind or daisyUI. Do not install Tailwind, daisyUI or htmx unless asked.

## Review checklist

Report each finding with file, line, problem and fix.

- Hand-written widget markup or component classes for form fields, including
  daisyUI 4 classes (`input-bordered`, `select-bordered`, `form-control`, `label-text`).
- Disallowed attributes in `{% daisy_field %}` (inline handlers, `aria-invalid`,
  `aria-describedby`) and `+=` on anything other than `class`.
- `prefix`/`suffix` or `choices` on unsupported widgets. Unquoted string values.
- Leftovers from other form libraries (`crispy_forms`, `|crispy`, `widget_tweaks`
  `render_field`) that duplicate or fight the renderer.
- Settings: wrong `FORM_RENDERER`, missing `"django.forms"`, or a project override of
  Django's global widget templates.
- Tailwind: no generated `daisy_forms_css` file, a stale file after an upgrade, a
  path-based `@source` into `site-packages`, or project classes passed through `class+=`
  or `label_class` that Tailwind never scans.
- htmx: invalid responses returned with `200` or `400` instead of `422`, or validation
  rules duplicated in a second form instead of reusing the real one.
