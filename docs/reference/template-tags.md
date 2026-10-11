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

**label** — Overrides the label text:

```django
{% daisy_field form.email label="Work email" %}
```

**label_class** — Appends classes to the label or legend:

```django
{% daisy_field form.email label_class="font-semibold text-primary" %}
```

Affects the primary label for ordinary fields, the standalone label for checkbox/toggle fields, and the legend for grouped choices, but not individual choice option labels.

**template** — Overrides the field template:

```django
{% daisy_field form.email template="daisy_forms/field_horizontal.html" %}
```

**choices** — Layout for radio/checkbox choices. Only accepts `inline`:

```django
{% daisy_field form.plan choices="inline" %}
```

Works only with RadioSelect and CheckboxSelectMultiple. Raises TemplateSyntaxError for unsupported widgets or values.

**prefix** — Text addon before the input:

```django
{% daisy_field form.price prefix="$" %}
```

Works only with stock, visible, single-line widgets rendered with daisyUI's input component. Raises TemplateSyntaxError for unsupported widgets.

**suffix** — Text addon after the input:

```django
{% daisy_field form.price suffix="USD" %}
```

Same restrictions as prefix.

Addon text is escaped. The addons copy the input's daisyUI size, color, and
error modifiers (`input-xs` to `input-xl`, `input-primary` and the other color
variants, `input-ghost`, `input-error`), so `class+="input-sm"` or a validation
error styles the whole group:

```django
{% daisy_field form.price prefix="$" suffix="USD" class+="input-sm" %}
```

## Attributes

Any other keyword argument becomes a widget attribute:

```django
{% daisy_field form.email hx-post="/validate/email/" hx-trigger="blur" %}
{% daisy_field form.search placeholder="Search..." %}
{% daisy_field form.quantity min="1" max="100" %}
```

Both `class=` and `class+=` append to daisyUI classes:

```django
{% daisy_field form.email class="input-sm" %}
{% daisy_field form.email class+="input-sm" %}
```

The `+=` syntax is accepted for parity with django-widget-tweaks. It is rejected on any other attribute name. Hyphenated attributes work without special syntax:

```django
{% daisy_field form.email hx-post="/validate/email/" %}
{% daisy_field form.search data-testid="search-input" %}
```

## Disallowed attributes

The tag rejects inline event handlers (`on*`, `hx-on*`, `x-on*`, `x-init` with optional `data-` prefix) and managed attributes (`aria-invalid`, `aria-describedby`) to prevent security issues and conflicts. Attempting to use these raises a TemplateSyntaxError at template compile time:

```django
{% daisy_field form.email onclick="alert('hi')" %}
```

```text
TemplateSyntaxError: Attribute is not allowed: onclick
```

## Error handling

Invalid field names raise ValueError at render time:

```django
{% daisy_field form.nonexistent %}
```

```
ValueError: {% daisy_field %} expected a bound field, got ''.
```

A field whose `bound_field_class` is a plain BoundField opts out of the package. Passing it to the tag raises TemplateSyntaxError.

Unsupported option values raise TemplateSyntaxError when the field renders:

| Usage                                                                                        | Error                                                                               |
| -------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| `choices="grid"`                                                                             | `choices must be set to 'inline'.`                                                  |
| `choices="inline"` on a non-choice widget                                                    | `choices='inline' requires a stock RadioSelect or CheckboxSelectMultiple widget.`   |
| `prefix` or `suffix` on a hidden, checkbox, radio, textarea, file, or custom-template widget | `prefix and suffix require a stock widget rendered with daisyUI's input component.` |

`+=` on any attribute other than `class` fails when the template compiles with
`Only class supports +=`.

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
