# Formsets

`{{ formset }}` renders the management form, non-form errors, and each form in turn. For formsets where people add and remove rows, the package ships two opt-in templates and a small script.

## Templates

| Template                           | Layout                                                                 |
| ---------------------------------- | ---------------------------------------------------------------------- |
| `daisy_forms/formset_dynamic.html` | Each form in a daisyUI `card`. Forms use their own `fieldsets`.        |
| `daisy_forms/formset_table.html`   | One table row per form, with a header row built from the field labels. |

Choose a template in any of the ways Django supports:

```django
{% include "daisy_forms/formset_table.html" with formset=formset %}
```

```python
from django.forms import BaseFormSet, formset_factory


class TableFormSet(BaseFormSet):
    template_name = "daisy_forms/formset_table.html"


ItemFormSet = formset_factory(ItemForm, formset=TableFormSet, can_delete=True)
```

A renderer subclass with `formset_template_name` changes every formset that uses it.

## The script

Load the script once on pages that use these templates:

```django
{% load static %}
<script src="{% static 'daisy_forms/js/formset.js' %}" defer></script>
```

The script is plain JavaScript with no dependencies. It needs `django.contrib.staticfiles` or another way to serve the file. It finds every `data-daisy-formset` element when the page loads, and every one that htmx swaps in later (`htmx:load`). Call `window.daisyForms.initFormsets(element)` after inserting markup by other means.

With the script loaded:

- **Add** clones `empty_form`, increments `TOTAL_FORMS`, focuses the new row's first field, and processes it with htmx when htmx is present.
- **Remove** on an unsaved row deletes it from the page, renumbers the rows after it, and decrements `TOTAL_FORMS`.
- **Remove** on a saved row checks its hidden `DELETE` box, dims it, and disables its non-hidden controls so browser validation ignores the row. Hidden identity fields and `DELETE` remain submitted. The same button then reads **Undo remove**. Django deletes the row on submit.
- Buttons are disabled at the formset's `min_num` and `max_num`.
- Buttons are real `<button type="button">` elements named with their row number, such as "Remove 2". A polite live region announces each change.
- `daisy-formset:added` and `daisy-formset:removed` events bubble from the formset with the row `index` in `detail`.

Saved rows can only be removed when the formset has `can_delete=True`.

## Without JavaScript

Without the script the Add and Remove buttons stay hidden, and the `DELETE` checkbox is visible. The formset submits exactly as `{{ formset }}` would.

## Table details

- Each control is labelled by its column header through `aria-labelledby`. Choice groups get a `role="group"` labelled the same way.
- Help text appears under the header. Each cell also keeps a visually hidden copy with the `{id}_helptext` id that `aria-describedby` references.
- Field errors appear in their cell with the `{id}_error` id. A form's non-field errors appear in a full-width row above it.
- Hidden fields are kept in the action cell, including when a form has no visible data columns. Fields with `show_hidden_initial=True` also render their hidden initial value.
- The table scrolls sideways on narrow screens. Use `formset_dynamic.html` when rows should stack.

## Translations

Button labels and announcements ("Remove", "Undo remove", "Add another", "Add {model}", "Row added.") are translatable with Django's i18n. The Add label uses the model's `verbose_name` for model formsets.
