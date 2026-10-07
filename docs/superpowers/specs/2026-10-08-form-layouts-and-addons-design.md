# Form layouts and input addons

## Goal

Add a small set of opt-in form presentation choices to `django-daisy-forms` while keeping Django's native form rendering, the current default markup, and the package's no-runtime-dependency policy.

## Current context

`DaisyFormRenderer` renders fields through `DaisyBoundField`. The `{% daisy_field %}` tag already supports field-template overrides and safe widget-attribute passthrough. The implementation contract lists `daisy_forms/field_horizontal.html` as a P1 template, but that template does not exist yet. Radio and checkbox choice groups currently render vertically.

## API

The existing `daisy_field` tag gains three reserved options:

```django
{% daisy_field form.email template="daisy_forms/field_horizontal.html" %}
{% daisy_field form.plan choices="inline" %}
{% daisy_field form.price prefix="$" suffix="USD" %}
```

- `template` keeps using the existing field-template override mechanism.
- `choices` accepts only `inline`. It applies to `RadioSelect` and `CheckboxSelectMultiple`. The default remains vertical. Unknown values or unsupported choice widgets raise `TemplateSyntaxError`.
- `prefix` and `suffix` add optional plain-text addons around supported single-line controls. Values are escaped by Django's template engine. They do not accept HTML or icon markup.
- Prefix and suffix apply only when the field uses a stock widget template and the renderer styles the widget as a daisyUI `input`. Unsupported combinations raise `TemplateSyntaxError` rather than rendering a misleading or unstyled group.
- All options apply to a copy of the bound field or widget and do not mutate the original form.

## Rendering

### Horizontal fields

The horizontal field template keeps the existing label, required indicator, help text, errors, fieldset semantics, and Django-generated accessibility associations. On narrow viewports it stacks the label and control. At a larger breakpoint it places the label in a fixed column and lets the control and its metadata use the remaining width. Checkbox and grouped-choice semantics follow the existing field template.

### Inline choices

`choices="inline"` changes only the outer layout of radio and checkbox choice groups to a wrapping horizontal row. It keeps each choice's current label/input relationship, error classes, optgroup labels, and the field's `fieldset` and `legend`. The default remains the current vertical layout.

### Prefix and suffix addons

Text addons render as sibling items in a full-width daisyUI `join` group. The control keeps its input and error classes and receives `join-item`. Each text addon renders as a non-interactive `span` with `input join-item` styling. Empty or omitted addons do not render. The input remains associated with the field's external label; the addon text stays in the accessible reading order.

## Documentation examples

Add concise README examples for horizontal fields, inline radio/checkbox groups, and a currency field with prefix and suffix. State which widget types accept addons, that addon values are text, and that defaults remain unchanged. Include the Tailwind class-generation step if new classes are added.

## Constraints

- Keep Django as the only runtime dependency.
- Do not add Crispy Forms, a layout DSL, JavaScript, or new package settings.
- Keep current rendering as the default.
- Register every class that the package emits in `classes.py` so `daisy_forms_css` includes it.
- Preserve escaping, existing class merge behavior, widget-copy semantics, and current accessibility markup.

## Verification

Review the rendered markup for the horizontal template, inline choices, error states, and text addons. Check that unsupported combinations fail clearly, addon values are escaped, current form defaults remain unchanged, and the generated Tailwind source includes the new daisyUI and utility classes.

## Out of scope

Icon addons, autocomplete, client-side behavior, arbitrary custom layout compositions, responsive layout configuration, and dynamic formsets.
