# System checks

django-daisy-forms provides two system checks to verify your configuration. Run them with `python manage.py check`.

## `daisy_forms.E001`

**Severity:** Error

**Meaning:** `django.forms` is missing from `INSTALLED_APPS`.

**Fix:** Add `django.forms` to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "django.forms",
    "daisy_forms",
]
```

**Why it matters:** The package uses `TemplatesSetting` as the renderer base class. Django requires `django.forms` to be in `INSTALLED_APPS` for `TemplatesSetting` to work.

## `daisy_forms.W001`

**Severity:** Warning

**Meaning:** `FORM_RENDERER` is not set to `DaisyFormRenderer` or a subclass of it. It is also raised when the `FORM_RENDERER` path cannot be imported, with the import error in the message.

**Fix:** Set `FORM_RENDERER` in your settings:

```python
FORM_RENDERER = "daisy_forms.renderers.DaisyFormRenderer"
```

**Why it matters:** If `FORM_RENDERER` is not set to the daisy renderer, forms will not render with daisyUI markup.

**When to ignore:** You can ignore this warning if you are:

- Using a custom renderer that subclasses `DaisyFormRenderer`
- Testing the package without the renderer
- Intentionally using a different renderer for specific forms

## Running checks

Run checks with:

```bash
python manage.py check
```

Or to run only daisy_forms checks:

```bash
python manage.py check --tag daisy_forms
```

To suppress a warning, add it to `SILENCED_SYSTEM_CHECKS`:

```python
SILENCED_SYSTEM_CHECKS = ["daisy_forms.W001"]
```

## Check implementation

The checks run with the `templates` tag. They live in `daisy_forms/checks.py`:

```python
--8<-- "src/daisy_forms/checks.py"
```
