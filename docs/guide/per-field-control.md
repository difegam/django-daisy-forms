# Per-field control

For one-off fields, the `{% daisy_field %}` template tag lets you customize classes, labels, templates, and attributes without touching the form class.

## Basic usage

Load the tag library and pass the bound field:

```django
{% load daisy_forms %}
{% daisy_field form.email %}
```

## Adding classes

Use `class=` or `class+=` to append daisyUI classes:

```django
{% daisy_field form.email class+="input-sm" %}
{% daisy_field form.bio class+="textarea-lg" %}
```

Both `class=` and `class+=` append to the daisyUI classes. The `+=` syntax is accepted for parity with django-widget-tweaks.

## Passing attributes

Any other keyword argument becomes a widget attribute:

```django
{% daisy_field form.email hx-post="/validate/email/" hx-trigger="blur" %}
{% daisy_field form.search placeholder="Search..." %}
{% daisy_field form.quantity min="1" max="100" %}
```

Hyphenated attributes like `hx-post` work without special syntax.

## Overriding the label

Use `label=` to change the label text:

```django
{% daisy_field form.email label="Work email" %}
```

## Styling the label

Use `label_class=` to append classes to the label or legend:

```django
{% daisy_field form.email label_class="font-semibold text-primary" %}
```

`label_class` affects:

- The primary label for ordinary fields
- The standalone label for checkbox/toggle fields
- The legend for grouped choices (radio, checkbox group)

It does **not** affect individual choice option labels.

!!! note

    Since `label_class` is supplied by your project, include custom classes in your Tailwind scan or safelist.

## Overriding the template

Use `template=` to change the field template:

```django
{% daisy_field form.email template="daisy_forms/field_horizontal.html" %}
```

See [Layouts & addons](layouts-addons.md) for details on the horizontal template.

## Reserved options

The following names are reserved and do not become widget attributes:

| Option        | Purpose                                      |
| ------------- | -------------------------------------------- |
| `label`       | Overrides label text                         |
| `label_class` | Appends classes to the label or legend       |
| `template`    | Overrides the field template                 |
| `choices`     | Layout for radio/checkbox choices (`inline`) |
| `prefix`      | Text addon before the input                  |
| `suffix`      | Text addon after the input                   |

To set the HTML `prefix` attribute (RDFa), use widget `attrs` instead:

```python
email = forms.EmailField(
    widget=forms.EmailInput(attrs={"prefix": "something"}),
)
```

## Disallowed attributes

The tag rejects these attributes to prevent security issues and conflicts:

- Inline event handlers: `on*`, `hx-on*`, `x-on*`, `x-init` (with optional `data-` prefix)
- Managed attributes: `aria-invalid`, `aria-describedby`

Attempting to use these raises a `TemplateSyntaxError` when the template is compiled:

```django
{% daisy_field form.email onclick="alert('hi')" %}
```

```text
TemplateSyntaxError: Attribute is not allowed: onclick
```

## Invalid field names

Passing a non-bound-field argument raises a `ValueError` at render time:

```django
{% daisy_field form.nonexistent %}
```

```text
ValueError: ...
```

## How it works

The tag renders a copy of the bound field with overrides. It never mutates the form:

1. Parses the tag arguments
2. Validates that reserved names are used correctly
3. Rejects disallowed attributes
4. Creates a `copy.copy(bf)` with the overrides
5. Renders through `as_field_group()` (or the template override)

## Opting out of the tag

To opt a field out of the daisy rendering entirely, set `bound_field_class` on the field:

```python
from django import forms
from django.forms import BoundField


class MyForm(forms.Form):
    email = forms.EmailField()
    email.bound_field_class = BoundField  # Opt out
```

An opted-out field cannot be passed to `{% daisy_field %}`. Render it with `{{ field }}` instead.
