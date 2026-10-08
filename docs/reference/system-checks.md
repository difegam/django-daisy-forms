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

**Meaning:** `FORM_RENDERER` is not set to `DaisyFormRenderer` or a subclass of it.

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

The checks are defined in `daisy_forms/checks.py`:

```python
from django.conf import settings
from django.core.checks import Error, Warning, register


@register()
def check_django_forms_installed(app_configs, **kwargs):
    errors = []
    if "django.forms" not in settings.INSTALLED_APPS:
        errors.append(
            Error(
                "django.forms is not in INSTALLED_APPS",
                hint="Add 'django.forms' to INSTALLED_APPS.",
                id="daisy_forms.E001",
            )
        )
    return errors


@register()
def check_form_renderer(app_configs, **kwargs):
    warnings = []
    from daisy_forms.renderers import DaisyFormRenderer

    renderer_path = getattr(settings, "FORM_RENDERER", None)
    if renderer_path != "daisy_forms.renderers.DaisyFormRenderer":
        # Check if it's a subclass
        try:
            from django.utils.module_loading import import_string

            renderer_class = import_string(renderer_path)
            if not issubclass(renderer_class, DaisyFormRenderer):
                warnings.append(
                    Warning(
                        "FORM_RENDERER is not DaisyFormRenderer",
                        hint="Set FORM_RENDERER = 'daisy_forms.renderers.DaisyFormRenderer'",
                        id="daisy_forms.W001",
                    )
                )
        except (ImportError, AttributeError):
            warnings.append(
                Warning(
                    "FORM_RENDERER is not DaisyFormRenderer",
                    hint="Set FORM_RENDERER = 'daisy_forms.renderers.DaisyFormRenderer'",
                    id="daisy_forms.W001",
                )
            )
    return warnings
```
