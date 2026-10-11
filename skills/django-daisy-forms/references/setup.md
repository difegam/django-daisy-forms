# Setup

## 1. Install

Use the project's package manager. Check for `uv.lock`, `poetry.lock` or a
`requirements*.txt` file.

```bash
uv add django-daisy-forms
# or
python -m pip install django-daisy-forms   # then add it to requirements
```

## 2. Settings

```python
INSTALLED_APPS = [
    # ...
    "django.forms",  # DaisyFormRenderer loads templates through TemplatesSetting
    "daisy_forms",
]

FORM_RENDERER = "daisy_forms.renderers.DaisyFormRenderer"
```

`TEMPLATES` must include a backend that loads app templates, such as `APP_DIRS: True`.
A subclass of `DaisyFormRenderer` is accepted. Use one only to change templates
project-wide.

## 3. Check

```bash
python manage.py check
```

| Message | Meaning | Fix |
| --- | --- | --- |
| `daisy_forms.E001` | `"django.forms"` is missing from `INSTALLED_APPS` | Add it |
| `daisy_forms.W001` | `FORM_RENDERER` is unset, cannot be imported, or is not `DaisyFormRenderer` or a subclass | Set it as above |

## 4. Tailwind

Continue with [tailwind.md](tailwind.md). The forms render daisyUI classes, but they
stay unstyled until the generated CSS source file is part of the Tailwind build.

## 5. Render

Existing `{{ form }}`, `{{ formset }}` and `{{ form.field.as_field_group }}` templates
now render daisyUI markup. Remove any hand-written component classes from form fields;
see [fields.md](fields.md).

## Scope and opt-outs

- `FORM_RENDERER` is global, so the Django admin forms use it too. Admin templates
  render widgets their own way, so check the admin after setup.
- To opt one form or field out, set `default_renderer` on the form, or set
  `bound_field_class = BoundField` (from `django.forms`) on the form or field.
  `{% daisy_field %}` raises on opted-out fields; render them with `{{ field }}`.
- Custom widgets with their own templates are never restyled. See
  [fields.md](fields.md#widgets).
