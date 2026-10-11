# System checks

django-daisy-forms provides two system checks to verify your configuration. Run them with `python manage.py check`.

## daisy_forms.E001

Error: `django.forms` is missing from `INSTALLED_APPS`. The package uses `TemplatesSetting` as the renderer base class, which requires `django.forms` to be installed. Add it:

```python
INSTALLED_APPS = [
    # ...
    "django.forms",
    "daisy_forms",
]
```

## daisy_forms.W001

Warning: `FORM_RENDERER` is not set to `DaisyFormRenderer` or a subclass. It is also raised when the path cannot be imported. Set it in your settings:

```python
FORM_RENDERER = "daisy_forms.renderers.DaisyFormRenderer"
```

Without this setting, forms will not render with daisyUI markup. Ignore this warning if you are using a custom renderer that subclasses DaisyFormRenderer, testing the package without the renderer, or using a different renderer for specific forms.

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
