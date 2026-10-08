# Troubleshooting

Common problems and how to fix them.

## Fields render without daisyUI styling

The markup has classes such as `input` and `fieldset`, but the page shows
unstyled controls.

1. **The generated CSS source file is missing or out of date.** Tailwind does
    not scan `site-packages`, so it only sees the package classes through the
    file that `daisy_forms_css` writes. Regenerate it, then rebuild your CSS:

    ```bash
    python manage.py daisy_forms_css --output static/src/daisy-forms.css
    ```

    Regenerate it after every package upgrade, and add the `--check` run to CI.
    See [Tailwind CSS integration](tailwind-css.md).

2. **The import order is wrong.** Import the generated file after Tailwind and
    daisyUI:

    ```css
    @import "tailwindcss";
    @plugin "daisyui";
    @import "./daisy-forms.css";
    ```

3. **The versions are too old.** The package needs Tailwind CSS 4.1 or later
    and daisyUI 5.0.36 or later.

## Fields render as plain Django markup

The output has no daisyUI classes at all.

- Check that `FORM_RENDERER = "daisy_forms.renderers.DaisyFormRenderer"` is
    set, and run `python manage.py check`. `daisy_forms.W001` means the setting
    is missing, points at another renderer, or cannot be imported.
- `daisy_forms.E001` means `"django.forms"` is missing from `INSTALLED_APPS`.
    The renderer loads templates through Django's `TemplatesSetting`, which needs
    it.
- A form or field can override the renderer or opt out with
    `bound_field_class = BoundField`. See [System checks](../reference/system-checks.md)
    and [Opting out of the tag](per-field-control.md#opting-out-of-the-tag).

## A custom or third-party widget is unstyled

Only widgets in the class registry get a daisyUI class, and widgets with their
own templates are never changed. Subclass a registered widget, or pass the class
through the widget's `attrs`. See [Widgets](../reference/widgets.md#unregistered-widgets).

## Classes from `class+=` or `label_class` have no effect

Classes you pass to `{% daisy_field %}` are written in your own templates, so
Tailwind generates them only if it scans those templates. Make sure your
Tailwind sources include your template directories, or add the classes to a
safelist with `@source inline()`.

## `{% daisy_field %}` raises an error

| Error                                                                               | Cause                                                                                                                                                                                                           |
| ----------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Attribute is not allowed: …`                                                       | Inline event handlers (`on*`, `hx-on*`, `x-on*`, `x-init`) and the managed `aria-invalid` and `aria-describedby` attributes are rejected when the template compiles. Use a script or `hx-*` attributes instead. |
| `Only class supports +=`                                                            | `+=` works only with `class`.                                                                                                                                                                                   |
| `{% daisy_field %} expected a bound field, got ''.`                                 | The field name is misspelled or the form is missing from the context.                                                                                                                                           |
| `… cannot be used on a field that opts out of DaisyBoundField …`                    | The field sets `bound_field_class = BoundField`. Render it with `{{ field }}`.                                                                                                                                  |
| `choices must be set to 'inline'.`                                                  | `choices` accepts only `"inline"`.                                                                                                                                                                              |
| `choices='inline' requires a stock RadioSelect or CheckboxSelectMultiple widget.`   | Inline choices work only with those stock widgets.                                                                                                                                                              |
| `prefix and suffix require a stock widget rendered with daisyUI's input component.` | Addons work only with stock single-line inputs such as text, email, number, and URL.                                                                                                                            |

See the [template tag reference](../reference/template-tags.md) for the full API.

## Validation errors don't appear after an htmx request

htmx does not swap `4xx` responses by default. Return `422` with the
re-rendered form and configure htmx to swap it. See the
[HTMX form validation recipe](../recipes/htmx-form-validation.md).
