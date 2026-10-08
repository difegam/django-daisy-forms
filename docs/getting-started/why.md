# Why django-daisy-forms

django-daisy-forms exists to fill a gap: no maintained package renders daisyUI 5 markup from Django's native form rendering API without requiring django-crispy-forms.

## The problem

Django's built-in form rendering is clean but unstyled. To get styled forms, most projects reach for django-crispy-forms with a template pack. This works, but introduces:

- A separate rendering pipeline that bypasses Django's `BoundField` APIs
- A layout DSL (FormHelper, Layout objects) that duplicates Django's template language
- An additional dependency with its own release cycle

For daisyUI specifically, existing options are limited:

| Package          | Status                      | Approach                                 |
| ---------------- | --------------------------- | ---------------------------------------- |
| crispy-tailwind  | Unmaintained since Feb 2024 | Plain Tailwind utilities, not daisyUI    |
| crispy-daisyui   | Low activity                | Requires crispy, fork of crispy-tailwind |
| django-mvp-forms | Pre-release                 | Requires crispy                          |

## The approach

django-daisy-forms takes a different path:

### One setting

`FORM_RENDERER` switches every `{{ form }}`, `{{ formset }}` and `{{ form.field.as_field_group }}` to daisyUI markup. No FormHelper, no layout DSL.

### Built on Django's APIs

A class registry gives each widget its daisyUI component through a custom `BoundField`. Django's global widget templates are never overridden, and custom widgets are left alone.

### Server-authoritative errors

Errors come from Django validation and use the same `aria-invalid` and `aria-describedby` ids Django already generates. The server has the final say — no client-side validation framework to configure or fight with.

### Per-field control when you need it

`{% daisy_field %}` merges classes, passes attributes such as `hx-*`, and opts fields into horizontal layouts, inline choices, or text addons. It refuses inline event handlers.

### CSS that can't drift

A management command writes the Tailwind `@source inline()` file, and `--check` fails CI when it is out of date. Your Tailwind build always knows about every daisyUI class the package emits.

### Small footprint

One runtime dependency (Django), no JavaScript, no Alpine, no build step beyond what your project already has.

## Design principles

1. **Django-native.** Use Django's own extension points (`TemplatesSetting`, `bound_field_class`, widget `attrs`) rather than reinventing them.

2. **Server-authoritative.** Validation errors come from Django. The package renders them accessibly and lets htmx swap the fragment.

3. **No magic.** No package-level settings, no Pydantic, no configuration layer. Customize by subclassing the renderer.

4. **CSS is a contract.** Tailwind 4 does not scan `site-packages`. The package makes this explicit with a generated `@source inline()` file and a CI check.

5. **Small surface.** One renderer, one BoundField, one template tag, four widgets, one management command, one system check module.

## When to use something else

django-daisy-forms is not for everyone. Consider alternatives if you need:

- **A general-purpose layout DSL** — django-crispy-forms has this, django-daisy-forms does not
- **Bootstrap or plain Tailwind** — this package is daisyUI-specific
- **Client-side validation** — use htmx with Django validation, or a different tool
- **Django < 5.2** — the package requires Django 5.2+ for `bound_field_class` at the renderer level
