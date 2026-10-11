# Forms, fields and templates

## Default: let the renderer work

```django
<form method="post">
  {% csrf_token %}
  {{ form }}
  <button class="btn btn-primary" type="submit">Save</button>
</form>
```

`{{ form }}` renders non-field errors as a daisyUI alert, every visible field as a
field group (label, control, help text, errors), and the hidden fields. Each field
gets its component class (`input`, `select`, `textarea`, `checkbox`, `radio`,
`toggle`, `file-input`, `range`), plus `-error` and `aria-invalid="true"` when it is
invalid. Error lists use the `{id}_error` ids that `aria-describedby` points at.
`{{ formset }}` works the same way. Buttons are not part of the form, so style them
with daisyUI classes yourself.

## `{% daisy_field %}` for one field

```django
{% load daisy_forms %}
{% daisy_field form.email class+="input-sm" placeholder="you@example.com" %}
```

| Option | Effect |
| --- | --- |
| `label="Work email"` | Replaces the label text |
| `label_class="font-semibold"` | Appends classes to the main label or the choice-group legend, not to option labels |
| `template="daisy_forms/field_horizontal.html"` | Uses another field template. The horizontal one stacks on mobile and puts label and control side by side from `md` |
| `choices="inline"` | Lays out stock `RadioSelect`/`CheckboxSelectMultiple` options in a wrapping row. `inline` is the only value |
| `prefix="$"` `suffix="USD"` | Joins escaped plain-text addons to a stock single-line input. Addons copy the input's size, color and error modifiers |
| `class="..."` or `class+="..."` | Both append to the daisyUI classes |
| any other `name="value"` | Becomes a widget attribute, for example `hx-post`, `placeholder`, `autocomplete` or `data-*` |

Rules, all enforced with `TemplateSyntaxError`:

- Rejected when the template compiles: `on*`, `hx-on*`, `x-on*`, `x-init` (also with
  a `data-` prefix), `aria-invalid` and `aria-describedby`. Only `class` accepts `+=`.
- Rejected when the field renders: `choices` with any value other than `"inline"` or
  on another widget, and `prefix`/`suffix` on selects, textareas, checkboxes, radios,
  file or hidden inputs, or widgets with custom templates.
- Values are template expressions. Quote literals (`prefix="$"`); unquoted names are
  variables. Tags do not nest, so write `{% url 'x' as x_url %}` before
  `{% daisy_field form.f hx-post=x_url %}`.
- The first argument must be a bound field. A typo raises
  `ValueError: ... expected a bound field, got ''`.

Classes passed here and to `label_class` come from project templates. Tailwind must
scan those templates (see [tailwind.md](tailwind.md)).

## Composed layouts

Group fields with plain HTML. The package has no layout DSL or FormHelper.

```django
{% load daisy_forms %}
<form method="post">
  {% csrf_token %}
  {% if form.non_field_errors %}<div role="alert" class="alert alert-error alert-soft">{{ form.non_field_errors }}</div>{% endif %}
  <fieldset>
    <legend>Account</legend>
    {% daisy_field form.email template="daisy_forms/field_horizontal.html" %}
  </fieldset>
  {% daisy_field form.plan choices="inline" %}
  {% daisy_field form.price prefix="$" suffix="USD" class+="input-sm" %}
  {% for field in form.hidden_fields %}{{ field }}{% endfor %}
  <button class="btn btn-primary" type="submit">Save</button>
</form>
```

When fields are rendered one by one, render `non_field_errors` and the hidden fields
yourself. `{{ form }}` does both.

## Widgets

Set widgets in the form class, not in templates:

```python
from django import forms
from daisy_forms.widgets import (
    NativeDateInput,
    NativeDateTimeInput,
    NativeTimeInput,
    Toggle,
)


class EventForm(forms.Form):
    starts_on = forms.DateField(widget=NativeDateInput)  # <input type="date">
    starts_at = forms.TimeField(widget=NativeTimeInput)  # type="time"
    opens = forms.DateTimeField(widget=NativeDateTimeInput)  # type="datetime-local"
    public = forms.BooleanField(widget=Toggle, required=False)  # class="toggle"
    volume = forms.IntegerField(
        widget=forms.NumberInput(attrs={"type": "range"})
    )  # class="range"
```

Stock `DateInput` renders `type="text"`, which is Django's default. Widgets get classes
through their class hierarchy, so subclasses of stock widgets inherit theirs. Widgets
with their own templates (third-party, `MultiWidget`, `SplitDateTimeWidget`) render
inside the field group without a daisyUI class. Subclass a stock widget, or pass
`attrs={"class": "input"}`.

## Do not

- Hand-write `<input>`/`<select>`/`<textarea>` for a form field. Doing so loses
  errors, ids, ARIA attributes and `required`.
- Add component classes (`input`, `select`, …) or daisyUI 4 classes (`input-bordered`,
  `form-control`, `label-text`). Size and color modifiers (`input-sm`,
  `select-primary`) are fine through `class+=`.
- Override Django's global `django/forms/widgets/*.html` templates. The package
  swaps its own templates on a copy of each widget.
- Combine with crispy-forms or widget_tweaks rendering for the same form.
