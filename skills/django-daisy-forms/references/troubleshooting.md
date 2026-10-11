# Troubleshooting

## Symptoms

| Symptom | Cause | Fix |
| --- | --- | --- |
| Markup has no daisyUI classes | `FORM_RENDERER` not set, or the form or field opts out | Set `daisy_forms.renderers.DaisyFormRenderer` and run `manage.py check`; look for `default_renderer` or `bound_field_class = BoundField` |
| Classes present, page unstyled | Generated CSS file missing, stale or imported in the wrong order; Tailwind or daisyUI too old | Regenerate with `daisy_forms_css --output ...`, import it after `@plugin "daisyui"`, rebuild CSS; Tailwind 4.1+, daisyUI 5.0.36+ |
| `class+=` or `label_class` classes have no effect | Tailwind does not scan the template that sets them | Add the template dirs to Tailwind sources, or safelist with `@source inline()` |
| A custom or third-party widget is unstyled | Widget is not in the class registry, or has its own template | Subclass a stock widget or pass `attrs={"class": "input"}` |
| htmx validation errors never appear | htmx 2 does not swap `4xx` | Return `422` and enable it in `responseHandling` ([htmx.md](htmx.md)) |
| CI fails `<path> is out of date.` | Package upgraded, file not regenerated, or edited by hand | Rerun `daisy_forms_css --output <path>` and commit |

## System checks

| Id | Meaning |
| --- | --- |
| `daisy_forms.E001` | `"django.forms"` missing from `INSTALLED_APPS` |
| `daisy_forms.W001` | `FORM_RENDERER` cannot be imported, or is not `DaisyFormRenderer` or a subclass |

## `{% daisy_field %}` errors

| Error | Cause |
| --- | --- |
| `Attribute is not allowed: <name>` | Inline handler (`on*`, `hx-on*`, `x-on*`, `x-init`, optionally `data-`-prefixed) or managed `aria-invalid`/`aria-describedby` |
| `Only class supports +=` | `+=` used on another attribute |
| `Invalid daisy_field attribute: <bit>` | Argument is not `name=value` / `class+=value`, e.g. a stray word or spaces around `=` |
| `daisy_field requires a bound field` | No field argument |
| `... expected a bound field, got ''.` | Misspelled field name or form missing from context |
| `... cannot be used on a field that opts out of DaisyBoundField ...` | Field uses `bound_field_class = BoundField`; render with `{{ field }}` |
| `choices must be set to 'inline'.` | Any other `choices` value |
| `choices='inline' requires a stock RadioSelect or CheckboxSelectMultiple widget.` | Inline choices on another widget |
| `prefix and suffix require a stock widget rendered with daisyUI's input component.` | Addons on select, textarea, checkbox, radio, file, hidden, or custom-template widgets |
| `TemplateDoesNotExist: Daisy field template overrides cannot be blank.` | `template=""` |
