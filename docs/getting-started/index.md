# Getting started

Get django-daisy-forms running in under five minutes. This section covers installation, configuration, and rendering your first form.

## Prerequisites

Before you begin, make sure your project meets these requirements:

| Requirement  | Version          |
| ------------ | ---------------- |
| Python       | 3.12 or later    |
| Django       | 5.2, 6.0, or 6.1 |
| Tailwind CSS | 4.1 or later     |
| daisyUI      | 5.0.36 or later  |

## Installation

Install the package with your preferred Python package manager:

=== "uv"

    ```bash
    uv add django-daisy-forms
    ```

=== "pip"

    ```bash
    python -m pip install django-daisy-forms
    ```

## Configuration

Add `django.forms` and `daisy_forms` to `INSTALLED_APPS`, then set the form renderer:

```python
# settings.py

INSTALLED_APPS = [
    # ...
    "django.forms",
    "daisy_forms",
]

FORM_RENDERER = "daisy_forms.renderers.DaisyFormRenderer"
```

!!! note

    `django.forms` must be in `INSTALLED_APPS` for the `TemplatesSetting` renderer to work. This is a Django requirement, not a package requirement.

### System checks

After configuration, run `python manage.py check` to verify your setup:

| Code               | Severity | Meaning                                          |
| ------------------ | -------- | ------------------------------------------------ |
| `daisy_forms.E001` | Error    | `django.forms` is missing from `INSTALLED_APPS`  |
| `daisy_forms.W001` | Warning  | `FORM_RENDERER` is not set to the daisy renderer |

## Your first form

With the renderer configured, existing forms render with daisyUI markup automatically:

```python
# forms.py
from django import forms


class SignupForm(forms.Form):
    email = forms.EmailField(
        help_text="We never share it.",
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
    )
    plan = forms.ChoiceField(
        choices=[("basic", "Basic"), ("pro", "Pro"), ("enterprise", "Enterprise")],
        widget=forms.RadioSelect,
    )
```

```django
{# template.html #}
<form method="post">
  {% csrf_token %}
  {{ form }}
  <button class="btn btn-primary" type="submit">Sign up</button>
</form>
```

That's it — every field renders with the correct daisyUI component class (`input`, `radio`, etc.), help text and errors are accessible via `aria-describedby`, and invalid fields get the `-error` variant.

## Next steps

<div class="grid cards" markdown>

- :material-book-open-variant:{ .lg .middle } **Learn how it works**

    ______________________________________________________________________

    Understand the rendering mechanism, validation, and per-field control.

    [:octicons-arrow-right-24: Guide](../guide/index.md)

- :material-code-tags:{ .lg .middle } **Explore the API**

    ______________________________________________________________________

    Widget classes, template tags, and overridable templates.

    [:octicons-arrow-right-24: Reference](../reference/index.md)

- :material-palette:{ .lg .middle } **Tailwind CSS setup**

    ______________________________________________________________________

    Generate the CSS source file for Tailwind.

    [:octicons-arrow-right-24: Tailwind CSS](../guide/tailwind-css.md)

</div>
