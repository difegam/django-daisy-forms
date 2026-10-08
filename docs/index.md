---
hide:
  - navigation
  - toc
---

# daisyUI 5 forms for Django

Render daisyUI 5 markup from Django's own form renderer and `BoundField` APIs. Point one setting at the daisy renderer and your existing `{{ form }}` and `{{ formset }}` templates keep working.

<p align="center">
    <a href="https://pypi.org/project/django-daisy-forms/"><img alt="PyPI" src="https://img.shields.io/pypi/v/django-daisy-forms"></a>
    <img alt="Python 3.12+" src="https://img.shields.io/badge/python-3.12%2B-44D19A">
    <img alt="Django 5.2 | 6.0 | 6.1" src="https://img.shields.io/badge/django-5.2%20%7C%206.0%20%7C%206.1-0C4B33">
    <img alt="daisyUI 5" src="https://img.shields.io/badge/daisyUI-5-FFC94A">
    <img alt="Tailwind CSS 4.1+" src="https://img.shields.io/badge/tailwind-4.1%2B-38BDF8">
    <a href="https://github.com/difegam/django-daisy-forms/blob/main/LICENSE"><img alt="MIT licence" src="https://img.shields.io/badge/license-MIT-9B8CFF"></a>
</p>

<p align="center">
  <img alt="django-daisy-forms in 30 seconds: one setting turns a plain Django form into daisyUI, server errors render accessibly, a template tag customizes fields, and a generated Tailwind source file keeps the CSS in sync" src="assets/demo.gif" width="720">
</p>

## Quick start

Install the package:

=== "uv"

    ```bash
    uv add django-daisy-forms
    ```

=== "pip"

    ```bash
    python -m pip install django-daisy-forms
    ```

Add the apps and renderer to your Django settings:

```python
INSTALLED_APPS = [
    # ...
    "django.forms",
    "daisy_forms",
]

FORM_RENDERER = "daisy_forms.renderers.DaisyFormRenderer"
```

Render `{{ form }}` as usual — every field now renders with daisyUI markup.

<div class="grid cards" markdown>

- :material-rocket-launch:{ .lg .middle } **Getting started**

    ______________________________________________________________________

    Install the package, configure the renderer, and render your first form.

    [:octicons-arrow-right-24: Getting started](getting-started/index.md)

- :material-book-open-variant:{ .lg .middle } **Guide**

    ______________________________________________________________________

    Learn how rendering, validation, per-field control, layouts, and themes work.

    [:octicons-arrow-right-24: Guide](guide/index.md)

- :material-code-tags:{ .lg .middle } **Reference**

    ______________________________________________________________________

    Widget classes, template tag API, override points, and management commands.

    [:octicons-arrow-right-24: Reference](reference/index.md)

- :material-chef-hat:{ .lg .middle } **Recipes**

    ______________________________________________________________________

    Practical examples including HTMX form validation.

    [:octicons-arrow-right-24: Recipes](recipes/index.md)

</div>

## Features

| Feature                         | Description                                                                                                                                         |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| **One setting**                 | `FORM_RENDERER` switches every `{{ form }}`, `{{ formset }}` and `{{ form.field.as_field_group }}` to daisyUI markup. No FormHelper, no layout DSL. |
| **Built on Django's APIs**      | A class registry gives each widget its daisyUI component through a custom `BoundField`. Django's global widget templates are never overridden.      |
| **Server-authoritative errors** | Errors use `aria-invalid` and `aria-describedby` ids that Django already generates. No client-side validation.                                      |
| **Per-field control**           | `{% daisy_field %}` merges classes, passes `hx-*` attributes, and opts fields into horizontal layouts, inline choices, or text addons.              |
| **CSS that can't drift**        | A management command writes the Tailwind `@source inline()` file, and `--check` fails CI when it is out of date.                                    |
| **Small footprint**             | One runtime dependency (Django), no JavaScript.                                                                                                     |

## Support

| Requirement  | Supported       |
| ------------ | --------------- |
| Python       | 3.12 or later   |
| Django       | 5.2, 6.0, 6.1   |
| Tailwind CSS | 4.1 or later    |
| daisyUI      | 5.0.36 or later |
