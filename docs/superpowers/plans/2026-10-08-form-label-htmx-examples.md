# Form label styling, HTMX validation, and layout examples Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add opt-in label styling, a complete app-side HTMX validation recipe, and a composed form preview without changing default rendering or adding runtime dependencies.

**Architecture:** Add `label_class` to the existing copied `DaisyBoundField` options and render it in the default and horizontal field templates. Expand the local browser preview with consumer-side sections and actions, then document HTMX 2 whole-form validation as an app integration that reuses Django's rendered errors.

**Tech Stack:** Django 5.2+, Python, Django templates, daisyUI 5, Tailwind CSS 4.1+, HTMX 2 (documentation example only).

**Spec:** `docs/superpowers/specs/2026-10-08-form-label-htmx-examples-design.md`

## Global Constraints

- Keep the package centered on Django's native form renderer, preserve existing defaults, and add no runtime dependencies.
- The value appends to the existing classes on the field's primary label or legend.
- It applies to ordinary labels, checkbox/toggle labels, and the legend for radio or checkbox groups. It does not apply to individual radio or checkbox options.
- Classes supplied by consumers must be included in their own Tailwind source scan or safelist; they do not belong in the package-generated class list.
- For an ordinary request, render the full page with the form and its errors.
- For an HTMX request with invalid data, return the rendered form fragment with status `422` so Django's existing error markup is reused.
- Configure HTMX to swap `422` responses. HTMX 2 does not swap `4xx` responses by default; the recipe will show the documented response-handling configuration.
- The package itself will not add HTMX, JavaScript, request middleware, or special form response behavior.
- Existing markup remains unchanged when `label_class` is omitted.
- Do not add automated tests or run test commands; the approved spec excludes them.

## Review Focus

- Omitted `label_class` must leave current markup unchanged. Manually compare default and horizontal field output without the option.
- Multiple label class tokens must append to the existing class attribute without replacing it. Inspect output for `label_class="font-semibold text-primary"`.
- Checkbox/toggle labels and choice-group legends must receive classes while individual choice labels remain unchanged. Inspect each in the local preview.
- Horizontal responsive classes and fieldset semantics must survive label styling. Inspect the preview at narrow and wide viewport widths.
- HTMX 2 must swap an invalid `422` response while regular POSTs still render the full page. Check the recipe's response configuration and view branches against the stated behavior.

---

### Task 1: Add opt-in label classes

**Files:**
- Modify: `src/daisy_forms/boundfield.py`
- Modify: `src/daisy_forms/templatetags/daisy_forms.py`
- Modify: `src/daisy_forms/templates/daisy_forms/field.html`
- Modify: `src/daisy_forms/templates/daisy_forms/field_horizontal.html`
- Modify: `README.md`
- Modify: `docs/django-daisy-forms.md`
- Modify: `CHANGELOG.md`

**Interfaces:**
- Consumes: Existing `DaisyFieldNode.render()` copy flow and `DaisyBoundField` field-template context.
- Produces: `DaisyBoundField.label_class: str | None`, populated by `{% daisy_field ... label_class="..." %}` and appended by the package's default and horizontal field templates.

- [ ] **Step 1: Add the per-render label class value**

In `DaisyBoundField`, add `label_class: str | None = None`. In `DaisyFieldNode.render()`, handle the reserved `label_class` option by assigning its resolved string value to the copied bound field. Keep the original field unchanged.

- [ ] **Step 2: Render additive classes on primary labels and legends**

In `field.html` and `field_horizontal.html`, append `field.label_class` to the existing class attribute for the single-checkbox label and the primary label or legend in each branch. Keep option labels in `daisy_forms/widgets/*_option.html` unchanged. Preserve the existing class attribute exactly when the value is empty or omitted.

- [ ] **Step 3: Update the public and internal documentation**

Document the `label_class` syntax, additive behavior, supported label/legend scope, custom-template responsibility, Tailwind source requirement, and newly reserved tag option in `README.md` and `docs/django-daisy-forms.md`. Add the new option under `Added` in `CHANGELOG.md`.

- [ ] **Step 4: Inspect the rendered markup manually**

Render default, horizontal, checkbox/toggle, and grouped-choice fields with and without `label_class`. Confirm omitted values preserve the prior markup, supplied classes append to the main label or legend, and choice option labels do not change.

- [ ] **Step 5: Commit the label-class change**

```bash
git add src/daisy_forms/boundfield.py src/daisy_forms/templatetags/daisy_forms.py src/daisy_forms/templates/daisy_forms/field.html src/daisy_forms/templates/daisy_forms/field_horizontal.html README.md docs/django-daisy-forms.md CHANGELOG.md
git commit -m "feat: support per-field label classes"
```

### Task 2: Expand the composed form preview

**Files:**
- Modify: `tests/templates/browser/form_preview.html`
- Modify: `README.md`

**Interfaces:**
- Consumes: Existing preview form fields and the `label_class`, horizontal-field, inline-choice, and addon APIs.
- Produces: A local preview showing form composition with named sections and an action row, plus a concise README example using ordinary Django template markup.

- [ ] **Step 1: Compose the preview form from sections**

In `form_preview.html`, group related fields inside named `fieldset` elements with `legend` text. Keep the existing email, plan, features, and price examples, and use the opt-in horizontal, inline-choice, addon, and label-class options where they demonstrate the pattern.

- [ ] **Step 2: Add a clear responsive action row**

Place the submit and reset actions together at the end of the preview form. Use daisyUI button classes and make the primary submit action visually distinct. Keep the actions usable on narrow viewports.

- [ ] **Step 3: Document consumer-side composition**

Add a short README example showing section fieldsets and the action row around the renderer's fields. Explain that this is regular project-template composition and does not require a package layout API.

- [ ] **Step 4: Review the preview at narrow and wide sizes**

Open the local browser preview and confirm sections, labels, inline choices, addons, and actions remain legible and aligned at mobile and desktop widths.

- [ ] **Step 5: Commit the composition example**

```bash
git add tests/templates/browser/form_preview.html README.md
git commit -m "docs: demonstrate composed form layouts"
```

### Task 3: Add the HTMX validation recipe

**Files:**
- Create: `docs/recipes/htmx-form-validation.md`
- Modify: `README.md`
- Modify: `docs/django-daisy-forms.md`

**Interfaces:**
- Consumes: `DaisyFormRenderer`, `{% daisy_field %}` HTMX attribute passthrough, normal Django form binding and validation, and HTMX 2 response handling.
- Produces: A self-contained app-side recipe for full-page POSTs and HTMX form submissions, plus a discoverable link from the README and updated roadmap notes.

- [ ] **Step 1: Write the consuming Django view example**

In `docs/recipes/htmx-form-validation.md`, show a view that binds `request.POST`, calls `form.is_valid()`, detects `HX-Request`, renders the full page for ordinary requests, returns the form fragment with status `422` for invalid HTMX requests, and returns a success fragment with status `200` for valid HTMX requests.

- [ ] **Step 2: Write the template and HTMX 2 response configuration**

Show the form fragment with a stable id, `hx-post`, `hx-target`, `hx-swap="outerHTML"`, and `{% csrf_token %}`. Include the complete default response-handling array with an explicit `422` swap rule. State that the recipe uses Django's server-rendered error markup and that the package itself does not depend on HTMX.

- [ ] **Step 3: Link and reconcile project documentation**

Add a short README section linking to the recipe and update the relevant roadmap/integration note in `docs/django-daisy-forms.md` so it points to the completed whole-form `422` example. Keep the existing no-JavaScript package claim clear.

- [ ] **Step 4: Review the example against Django and HTMX behavior**

Check that ordinary invalid POSTs render a complete page, invalid HTMX requests return a swappable form fragment with status `422`, valid HTMX requests return the success fragment, and the configuration preserves the documented HTMX 2 defaults for other status codes.

- [ ] **Step 5: Commit the HTMX recipe**

```bash
git add docs/recipes/htmx-form-validation.md README.md docs/django-daisy-forms.md
git commit -m "docs: add HTMX form validation recipe"
```

## Execution Notes

Run tasks in order. Task 2 uses the `label_class` API from Task 1. Task 3 is documentation-only and can follow the preview task. Keep the current README content intact while applying the focused edits described above.
