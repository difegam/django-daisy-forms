# Template tags

django-daisy-forms provides one template tag: `{% daisy_field %}`. This page documents its full API.

## Loading the tag library

```django
{% load daisy_forms %}
```

## Basic syntax

```django
{% daisy_field <bound_field> [options] [attributes] %}
```

## Options

### `label`

Overrides the label text:

```django
{% daisy_field form.email label="Work email" %}
```

### `label_class`

Appends classes to the label or legend:

```django
{% daisy_field form.email label_class="font-semibold text-primary" %}
```

Affects the primary label for ordinary fields, the standalone label for checkbox/toggle fields, and the legend for grouped choices. Does **not** affect individual choice option labels.

### `template`

Overrides the field template:

```django
{% daisy_field form.email template="daisy_forms/field_horizontal.html" %}
```

### `choices`

Layout for radio/checkbox choices. Only accepts `inline`:

```django
{% daisy_field form.plan choices="inline" %}
```

Only works with `RadioSelect` and `CheckboxSelectMultiple`. Raises `TemplateSyntaxError` for unsupported widgets or values.

### `prefix`

Text addon before the input:

```django
{% daisy_field form.price prefix="$" %}
```

Only works with stock, visible, single-line widgets rendered with daisyUI's `input` component. Raises `TemplateSyntaxError` for unsupported widgets.

### `suffix`

Text addon after the input:

```django
{% daisy_field form.price suffix="USD" %}
```

Same restrictions as `prefix`.

## Attributes

Any other keyword argument becomes a widget attribute:

```django
{% daisy_field form.email hx-post="/validate/email/" hx-trigger="blur" %}
{% daisy_field form.search placeholder="Search..." %}
{% daisy_field form.quantity min="1" max="100" %}
```

### Class attributes

Both `class=` and `class+=` append to daisyUI classes:

```django
{% daisy_field form.email class="input-sm" %}
{% daisy_field form.email class+="input-sm" %}
```

The `+=` syntax is accepted for parity with django-widget-tweaks. `+=` is rejected on any other attribute name.

### Hyphenated attributes

Hyphenated attributes work without special syntax:

```django
{% daisy_field form.email hx-post="/validate/email/" %}
{% daisy_field form.search data-testid="search-input" %}
```

## Disallowed attributes

The tag rejects these attributes to prevent security issues and conflicts:

### Inline event handlers

- `on*` (e.g., `onclick`, `onchange`)
- `hx-on*` (e.g., `hx-on-click`)
- `x-on*` (e.g., `x-on-click`)
- `x-init`
- With optional `data-` prefix (e.g., `data-on-click`)

### Managed attributes

- `aria-invalid` — managed by the package based on validation state
- `aria-describedby` — managed by the package to link help text and errors

Attempting to use these raises a `TemplateSyntaxError` at template compile time:

```django
{% daisy_field form.email onclick="alert('hi')" %}
```

```text
TemplateSyntaxError: Attribute is not allowed: onclick
```

## Error handling

### Invalid field names

Passing a non-bound-field argument raises a `ValueError` at render time:

```django
{% daisy_field form.nonexistent %}
```

```text
ValueError: ...
```

### Invalid options

Unsupported option values raise `TemplateSyntaxError`:

```django
{% daisy_field form.plan choices="grid" %}
```

```text
TemplateSyntaxError: ...
```

## How it works

The tag:

1. Parses the tag arguments
2. Validates that reserved names are used correctly
3. Rejects disallowed attributes
4. Creates a `copy.copy(bf)` with the overrides
5. Renders through `as_field_group()` (or the template override)

The tag never mutates the original form or bound field.

## Complete example

```django
{% load daisy_forms %}
<form method="post">
  {% csrf_token %}

  <fieldset>
    <legend>Account</legend>
    {% daisy_field form.email
        template="daisy_forms/field_horizontal.html"
        label="Work email"
        label_class="font-semibold"
        hx-post="/validate/email/"
        hx-trigger="blur"
        class+="input-sm" %}
  </fieldset>

  <fieldset>
    <legend>Plan</legend>
    {% daisy_field form.plan choices="inline" %}
  </fieldset>

  <fieldset>
    <legend>Pricing</legend>
    {% daisy_field form.price prefix="$" suffix="USD" %}
  </fieldset>

  <div class="flex gap-3">
    <button class="btn btn-primary" type="submit">Save</button>
  </div>
</form>
```
