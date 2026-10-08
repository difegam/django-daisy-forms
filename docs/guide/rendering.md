# Rendering forms

django-daisy-forms maps Django widgets to daisyUI components through a class registry. This page explains how the rendering works and what markup is produced.

## How rendering works

When you set `FORM_RENDERER = "daisy_forms.renderers.DaisyFormRenderer"`, Django uses a custom renderer that:

1. Sets `bound_field_class = DaisyBoundField` — every `{{ form.field }}` becomes a `DaisyBoundField`
2. Sets `field_template_name = "daisy_forms/field.html"` — field groups use the package's template
3. Sets `form_template_name = "daisy_forms/form.html"` — forms use the package's template
4. Sets `formset_template_name = "daisy_forms/formset.html"` — formsets use the package's template

The `DaisyBoundField` looks up the widget's daisyUI class from a registry and applies it when the widget renders. Django's global widget templates are never overridden.

## Widget class mapping

Every Django widget gets a daisyUI component class:

| Django widget                                                         | daisyUI class | Example                                       |
| --------------------------------------------------------------------- | ------------- | --------------------------------------------- |
| `TextInput`, `EmailInput`, `URLInput`, `NumberInput`, `PasswordInput` | `input`       | `<input class="input">`                       |
| `Textarea`                                                            | `textarea`    | `<textarea class="textarea">`                 |
| `Select`                                                              | `select`      | `<select class="select">`                     |
| `CheckboxInput`                                                       | `checkbox`    | `<input type="checkbox" class="checkbox">`    |
| `RadioSelect`                                                         | `radio`       | `<input type="radio" class="radio">`          |
| `CheckboxSelectMultiple`                                              | `checkbox`    | `<input type="checkbox" class="checkbox">`    |
| `FileInput`, `ClearableFileInput`                                     | `file-input`  | `<input type="file" class="file-input">`      |
| `Toggle` (package widget)                                             | `toggle`      | `<input type="checkbox" class="toggle">`      |
| `NativeDateInput`                                                     | `input`       | `<input type="date" class="input">`           |
| `NativeTimeInput`                                                     | `input`       | `<input type="time" class="input">`           |
| `NativeDateTimeInput`                                                 | `input`       | `<input type="datetime-local" class="input">` |

!!! note

    `HiddenInput` receives no class. Third-party or custom widgets that are not in the registry render unchanged inside the field wrapper.

## Field markup

Every field renders with a consistent structure:

```html
<div class="fieldset">
  <label class="fieldset-legend" for="id_email">
    Email
    <span class="text-error" aria-hidden="true">*</span>
  </label>
  <p class="label" id="id_email_helptext">We never share it.</p>
  <input type="email" name="email" class="input w-full" id="id_email"
         aria-describedby="id_email_helptext">
</div>
```

For widgets that use `<fieldset>` (radio groups, checkbox groups):

```html
<fieldset class="fieldset" aria-describedby="id_plan_helptext">
  <legend class="fieldset-legend">Plan</legend>
  <p class="label" id="id_plan_helptext">Change any time.</p>
  <div id="id_plan" class="flex flex-col gap-2">
    <label class="label" for="id_plan_0">
      <input type="radio" name="plan" value="basic" class="radio" id="id_plan_0">
      Basic
    </label>
    <label class="label" for="id_plan_1">
      <input type="radio" name="plan" value="pro" class="radio" id="id_plan_1">
      Pro
    </label>
  </div>
</fieldset>
```

For checkboxes and toggles, the control comes before the label:

```html
<div class="fieldset">
  <label class="label" for="id_terms">
    <input type="checkbox" name="terms" class="checkbox" id="id_terms">
    I accept the terms
  </label>
</div>
```

## Element order

Fields follow this order:

1. Label (or legend for grouped choices)
2. Help text
3. Errors (when present)
4. Control

Checkboxes and toggles reverse the first two: control + label, then help, then errors.

## Form markup

A form renders non-field errors first, then each field:

```django
{# daisy_forms/form.html #}
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

## Formset markup

Formsets render the management form, then non-form errors, then each form:

```django
{# daisy_forms/formset.html #}
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

## Custom widgets

Custom widgets that are not in the registry render inside the field wrapper but without daisyUI classes. To style a custom widget, either:

1. Subclass a registered widget (e.g., `class MyInput(TextInput)`)
2. Pass classes through widget `attrs`: `widget=forms.TextInput(attrs={"class": "input"})`

Third-party widgets with custom templates are left untouched by design.
