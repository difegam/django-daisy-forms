# Templates

django-daisy-forms provides a set of templates that you can override in your project. This page documents every overridable template and its structure.

## Override mechanism

To override a package template, create a file with the same name in your project's template directory:

```python
# settings.py
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # Your project templates
        "APP_DIRS": True,
        # ...
    },
]
```

```text
templates/
  daisy_forms/
    field.html  # Overrides the package template
```

Template names are public API, and renames are breaking changes.

## Form templates

The listings below are included from the package source, so they always match the released templates.

### `daisy_forms/form.html`

Renders a form. The context is Django's form rendering context: `errors` (non-field errors, including hidden-field errors), `fields` (pairs of visible bound field and its errors), and `hidden_fields`.

```django
--8<-- "src/daisy_forms/templates/daisy_forms/form.html"
```

### `daisy_forms/formset.html`

Renders a formset: the management form, non-form errors, then each form.

```django
--8<-- "src/daisy_forms/templates/daisy_forms/formset.html"
```

## Field templates

### `daisy_forms/field.html`

The default field template. Single checkboxes and toggles render the control inside a `label`; grouped choices use a `fieldset` and `legend`; every other widget gets a `fieldset-legend` label followed by help text, errors, and the control.

```django
--8<-- "src/daisy_forms/templates/daisy_forms/field.html"
```

### `daisy_forms/_field_meta.html`

Renders help text and errors with the `{id}_helptext` and `{id}_error` ids that Django's `aria-describedby` references. Included by both field templates. If you override a field template, include it or render equivalent markup.

```django
--8<-- "src/daisy_forms/templates/daisy_forms/_field_meta.html"
```

### `daisy_forms/field_horizontal.html`

The opt-in horizontal layout. Label and control stack on narrow screens and sit side by side from the `md` breakpoint. Use it with `{% daisy_field form.email template="daisy_forms/field_horizontal.html" %}`.

```django
--8<-- "src/daisy_forms/templates/daisy_forms/field_horizontal.html"
```

## Widget templates

The renderer swaps these in on a copy of stock `RadioSelect`, `CheckboxSelectMultiple`, and `ClearableFileInput` widgets. Widgets with custom templates are left untouched.

### `daisy_forms/widgets/radio.html`

Renders a `RadioSelect` as a vertical list of options.

```django
--8<-- "src/daisy_forms/templates/daisy_forms/widgets/radio.html"
```

### `daisy_forms/widgets/radio_option.html`

Renders a single radio option inside its label.

```django
--8<-- "src/daisy_forms/templates/daisy_forms/widgets/radio_option.html"
```

### `daisy_forms/widgets/radio_inline.html`

Used for `choices="inline"`: the same options in a wrapping row.

```django
--8<-- "src/daisy_forms/templates/daisy_forms/widgets/radio_inline.html"
```

### `daisy_forms/widgets/checkbox_select.html`

Renders a `CheckboxSelectMultiple` as a vertical list of options.

```django
--8<-- "src/daisy_forms/templates/daisy_forms/widgets/checkbox_select.html"
```

### `daisy_forms/widgets/checkbox_option.html`

Renders a single checkbox option inside its label.

```django
--8<-- "src/daisy_forms/templates/daisy_forms/widgets/checkbox_option.html"
```

### `daisy_forms/widgets/checkbox_select_inline.html`

Used for `choices="inline"`: the same options in a wrapping row.

```django
--8<-- "src/daisy_forms/templates/daisy_forms/widgets/checkbox_select_inline.html"
```

### `daisy_forms/widgets/clearable_file_input.html`

Renders a `ClearableFileInput` with the current file link and the clear checkbox.

```django
--8<-- "src/daisy_forms/templates/daisy_forms/widgets/clearable_file_input.html"
```

## Overriding templates

When overriding templates:

1. **Preserve accessibility** — keep `aria-describedby`, `aria-invalid`, and `id` attributes
2. **Include `_field_meta.html`** — or replace it with equivalent help text and error rendering
3. **Use the correct classes** — daisyUI component classes (`input`, `select`, etc.) and layout classes (`fieldset`, `fieldset-legend`, etc.)
4. **Escape user input** — never use `|safe` on labels, help text, errors, or values

## Template context

Field templates receive a `field` variable that is a `DaisyBoundField` instance. Available attributes:

- `field.label` — the label text
- `field.label_class` — classes to append to the label (set by `{% daisy_field %}`)
- `field.help_text` — help text
- `field.errors` — error list
- `field.auto_id` — the auto-generated ID
- `field.id_for_label` — the ID to use for the label's `for` attribute
- `field.aria_describedby` — the `aria-describedby` value (space-separated IDs)
- `field.use_fieldset` — whether to use `<fieldset>` (True for radio/checkbox groups)
- `field.field.required` — whether the field is required
- `field.field.widget` — the widget instance
