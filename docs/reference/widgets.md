# Widgets

django-daisy-forms maps Django widgets to daisyUI components through a class registry. This page documents the mapping and the custom widgets the package provides.

## Widget class mapping

The class registry maps Django widget types to daisyUI component classes using the widget's MRO (method resolution order), so subclasses of registered widgets inherit the class.

| Widget                                                      | Class      | Notes                                   |
| ----------------------------------------------------------- | ---------- | --------------------------------------- |
| HiddenInput                                                 | None       | No class applied                        |
| TextInput, EmailInput, URLInput, NumberInput, PasswordInput | input      | Via Input base class                    |
| DateInput, DateTimeInput, TimeInput                         | input      | Registered directly                     |
| Textarea                                                    | textarea   |                                         |
| Select                                                      | select     | Includes NullBooleanSelect              |
| CheckboxInput                                               | checkbox   |                                         |
| RadioSelect                                                 | radio      |                                         |
| CheckboxSelectMultiple                                      | checkbox   |                                         |
| FileInput, ClearableFileInput                               | file-input | ClearableFileInput uses custom template |
| Toggle                                                      | toggle     | Package widget                          |
| NativeDateInput, NativeTimeInput, NativeDateTimeInput       | input      | Package widgets                         |

## Input types

Some input types have their own daisyUI component. The effective `type`
(an attribute passed to the widget or `{% daisy_field %}` first, then the
widget's own `input_type`) is checked before the widget class:

| Input `type` | daisyUI class | Notes                                              |
| ------------ | ------------- | -------------------------------------------------- |
| `range`      | `range`       | For example `NumberInput(attrs={"type": "range"})` |
| `color`      | *None*        | Rendered without a component class                 |

## Error variants

When a field has validation errors, the package appends `-error` to the base class. Each component class has a corresponding `-error` variant: input-error, textarea-error, select-error, checkbox-error, radio-error, toggle-error, file-input-error, range-error.

## Custom widgets

### Toggle

A checkbox rendered as a toggle switch:

```python
from daisy_forms.widgets import Toggle


class MyForm(forms.Form):
    notifications = forms.BooleanField(
        widget=Toggle,
        required=False,
    )
```

Renders as:

```html
<input type="checkbox" name="notifications" class="toggle" id="id_notifications">
```

### Native date/time inputs

Native HTML5 date, time, and datetime inputs:

```python
from daisy_forms.widgets import NativeDateInput, NativeTimeInput, NativeDateTimeInput


class MyForm(forms.Form):
    start_date = forms.DateField(widget=NativeDateInput)
    start_time = forms.TimeField(widget=NativeTimeInput)
    start_datetime = forms.DateTimeField(widget=NativeDateTimeInput)
```

These render with the correct `type` attribute:

- `NativeDateInput` → `<input type="date">`
- `NativeTimeInput` → `<input type="time">`
- `NativeDateTimeInput` → `<input type="datetime-local">`

!!! note

    Stock `DateInput` and `TimeInput` render with `type="text"` by default (Django's behavior). The package does not change this. Use the `Native*` widgets for HTML5 inputs.

## How the registry works

The lookup checks the input type first, then walks the widget's MRO:

```python
def daisy_class_for(widget: Widget, input_type: str | None = None) -> str | None:
    effective_type = (
        input_type or widget.attrs.get("type") or getattr(widget, "input_type", None)
    )
    if (
        isinstance(widget, Input)
        and effective_type is not None
        and effective_type in INPUT_TYPE_CLASSES
    ):
        return INPUT_TYPE_CLASSES[effective_type]
    for widget_type in type(widget).__mro__:
        if widget_type in WIDGET_CLASSES:
            return WIDGET_CLASSES[widget_type]
    return None
```

This means:

1. Subclasses of registered widgets inherit the class
2. Custom widgets that don't inherit from registered types return `None`
3. `None` means no class is applied (the widget renders unchanged inside the field wrapper)

## Unregistered widgets

Widgets not in the registry (`MultiWidget`, `SplitDateTimeWidget`, custom widgets) render inside the field wrapper but without daisyUI classes. You can style an unregistered widget by subclassing a registered widget (if it's a variant), passing classes through the widget's `attrs`, or overriding the widget template.

## Template swapping

For widgets that use Django's stock templates (radio, checkbox group, clearable file), the package swaps in its own templates on a copy of the widget. RadioSelect uses `daisy_forms/widgets/radio.html`, CheckboxSelectMultiple uses `daisy_forms/widgets/checkbox_select.html`, and ClearableFileInput uses `daisy_forms/widgets/clearable_file_input.html`. Third-party widgets with custom templates are left unchanged.

## Registry source

The registry lives in `daisy_forms/classes.py`:

```python
WIDGET_CLASSES: Final[Mapping[type[Widget], str | None]] = {
    HiddenInput: None,
    Textarea: "textarea",
    Select: "select",
    CheckboxInput: "checkbox",
    Toggle: "toggle",
    CheckboxSelectMultiple: "checkbox",
    RadioSelect: "radio",
    DateInput: "input",
    DateTimeInput: "input",
    TimeInput: "input",
    FileInput: "file-input",
    Input: "input",
}

INPUT_TYPE_CLASSES: Final[Mapping[str, str | None]] = {
    "range": "range",
    "color": None,
}
```

`LAYOUT_CLASSES` lists the layout classes used in the package templates. The
`daisy_forms_css` command combines it with every component class and its
`-error` variant to write the `@source inline()` file.
