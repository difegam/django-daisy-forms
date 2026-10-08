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

### `daisy_forms/form.html`

Renders a complete form with non-field errors, visible fields, and hidden fields.

```django
{% if form.errors %}
  {% if form.non_field_errors %}
    <div role="alert" class="alert alert-error alert-soft">
      <ul>
        {% for error in form.non_field_errors %}
          <li>{{ error }}</li>
        {% endfor %}
      </ul>
    </div>
  {% endif %}
{% endif %}

{% for field in form.visible_fields %}
  {{ field.as_field_group }}
{% endfor %}

{% for field in form.hidden_fields %}
  {{ field }}
{% endfor %}
```

### `daisy_forms/formset.html`

Renders a formset with the management form, non-form errors, and each form.

```django
{{ formset.management_form }}

{% if formset.non_form_errors %}
  <div role="alert" class="alert alert-error alert-soft">
    <ul>
      {% for error in formset.non_form_errors %}
        <li>{{ error }}</li>
      {% endfor %}
    </ul>
  </div>
{% endif %}

{% for form in formset %}
  {{ form }}
{% endfor %}
```

## Field templates

### `daisy_forms/field.html`

The default field template. Renders a single field with label, help text, errors, and control.

```django
{% if field.use_fieldset %}
  <fieldset class="fieldset"{% if field.aria_describedby %} aria-describedby="{{ field.aria_describedby }}"{% endif %}>
    <legend class="fieldset-legend">{{ field.label }}{% if field.field.required %}<span class="text-error" aria-hidden="true"> *</span>{% endif %}</legend>
    {% include "daisy_forms/_field_meta.html" %}
    {{ field }}
  </fieldset>
{% else %}
  <div class="fieldset">
    {% if field.field.widget.input_type == "checkbox" or field.field.widget.input_type == "toggle" %}
      <label class="label" for="{{ field.id_for_label }}">
        {{ field }}
        {{ field.label }}{% if field.field.required %}<span class="text-error" aria-hidden="true"> *</span>{% endif %}
      </label>
    {% else %}
      <label class="fieldset-legend" for="{{ field.id_for_label }}">{{ field.label }}{% if field.field.required %}<span class="text-error" aria-hidden="true"> *</span>{% endif %}</label>
    {% endif %}
    {% include "daisy_forms/_field_meta.html" %}
    {% if field.field.widget.input_type != "checkbox" and field.field.widget.input_type != "toggle" %}
      {{ field }}
    {% endif %}
  </div>
{% endif %}
```

### `daisy_forms/_field_meta.html`

Renders help text and errors. Included by `field.html`.

```django
{% if field.help_text %}
  <p class="label" id="{{ field.auto_id }}_helptext">{{ field.help_text }}</p>
{% endif %}

{% if field.errors %}
  <ul class="text-error text-sm" id="{{ field.auto_id }}_error">
    {% for error in field.errors %}
      <li>{{ error }}</li>
    {% endfor %}
  </ul>
{% endif %}
```

If you override `field.html`, you must also include or replace `_field_meta.html`.

### `daisy_forms/field_horizontal.html`

Horizontal field layout. Label and control sit side by side at the `md` breakpoint.

```django
<div class="fieldset sm:flex sm:items-start sm:gap-4">
  <label class="fieldset-legend sm:w-1/3 sm:pt-2" for="{{ field.id_for_label }}">
    {{ field.label }}{% if field.field.required %}<span class="text-error" aria-hidden="true"> *</span>{% endif %}
  </label>
  <div class="flex-1">
    {% include "daisy_forms/_field_meta.html" %}
    {{ field }}
  </div>
</div>
```

## Widget templates

### `daisy_forms/widgets/radio.html`

Renders a `RadioSelect` widget.

```django
<div id="{{ widget.attrs.id }}" class="flex flex-col gap-2">
  {% for group, options, index in widget.optgroups %}
    {% for option in options %}
      <label class="label" for="{{ option.attrs.id }}">
        <input type="{{ option.type }}" name="{{ option.name }}" value="{{ option.value }}" class="radio{% if widget.attrs.class %} {{ widget.attrs.class }}{% endif %}"{% if option.selected %} checked{% endif %}{% for name, value in option.attrs.items %}{% if name != "id" and name != "type" and name != "name" and name != "value" and name != "class" %} {{ name }}="{{ value }}"{% endif %}{% endfor %} id="{{ option.attrs.id }}">
        {{ option.label }}
      </label>
    {% endfor %}
  {% endfor %}
</div>
```

### `daisy_forms/widgets/radio_option.html`

Renders a single radio option. Used by `radio.html`.

### `daisy_forms/widgets/checkbox_select.html`

Renders a `CheckboxSelectMultiple` widget. Similar to `radio.html` but with `checkbox` class.

### `daisy_forms/widgets/checkbox_option.html`

Renders a single checkbox option. Used by `checkbox_select.html`.

### `daisy_forms/widgets/clearable_file_input.html`

Renders a `ClearableFileInput` widget with the current file link and clear checkbox.

```django
{% if widget.value and widget.value.url %}
  <div class="mb-2">
    <a href="{{ widget.value.url }}" class="link">{{ widget.value.name }}</a>
    <label class="label ml-4">
      <input type="checkbox" name="{{ widget.name }}-clear" id="{{ widget.name }}-clear_id" class="checkbox checkbox-sm">
      Clear
    </label>
  </div>
{% endif %}
<input type="{{ widget.type }}" name="{{ widget.name }}" class="file-input{% if widget.attrs.class %} {{ widget.attrs.class }}{% endif %}"{% for name, value in widget.attrs.items %}{% if name != "type" and name != "name" and name != "class" %} {{ name }}="{{ value }}"{% endif %}{% endfor %} id="{{ widget.attrs.id }}">
```

### `daisy_forms/widgets/radio_inline.html`

Renders a `RadioSelect` widget with inline choices.

### `daisy_forms/widgets/checkbox_select_inline.html`

Renders a `CheckboxSelectMultiple` widget with inline choices.

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
