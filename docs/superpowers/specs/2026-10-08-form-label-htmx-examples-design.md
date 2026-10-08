# Form label styling, HTMX validation, and layout examples

## Goal

Add the three agreed improvements to django-daisy-forms: optional per-field label classes, an app-side HTMX validation recipe, and a more complete composed-layout preview. Keep the package centered on Django's native form renderer, preserve existing defaults, and add no runtime dependencies.

## Agreed understanding

The project is a renderer package, not a general UI framework. Its job is to produce accessible daisyUI markup for Django forms and leave page composition and client-side behavior to the consuming project. The requested improvements should make common styling and integration patterns easier to understand without adding Crispy Forms, Django Components, Labb, or django-formset as dependencies.

## Current context

- `DaisyFormRenderer` uses `DaisyBoundField` and package field templates.
- `{% daisy_field %}` already supports widget classes and attributes, label text, field templates, inline choices, and text addons.
- The default and horizontal field templates render a main label or legend. Checkbox fields render the control and label together. Choice option labels are rendered by separate widget templates.
- The browser preview already demonstrates horizontal fields, inline choices, text addons, responsive behavior, and server-rendered field errors.
- The README already documents a `422` HTMX pattern, but it does not provide a complete request/response example.
- Commit `a0c2489` added modifier propagation for text addons and expanded layout documentation. Its changes are committed and outside this spec's edit scope.

## Design

### 1. Optional label classes

Add a reserved `label_class` option to `{% daisy_field %}`:

```django
{% daisy_field form.email label_class="font-semibold" %}
```

The value appends to the existing classes on the field's primary label or legend. It applies to ordinary labels, checkbox/toggle labels, and the legend for radio or checkbox groups. It does not apply to individual radio or checkbox options. It does not replace the existing `label`, `fieldset-legend`, or responsive classes.

Implement the option on a copied `DaisyBoundField`, following the existing per-render option pattern. Update the package's default and horizontal field templates to render the additional class tokens. Template autoescaping remains enabled. Classes supplied by consumers must be included in their own Tailwind source scan or safelist; they do not belong in the package-generated class list.

Custom field templates remain responsible for rendering this optional property if they want to support it. The option is reserved by the tag and documented as such.

### 2. Composed form preview

Extend the existing local browser preview with an example form that demonstrates composition around the package's field groups:

- group related inputs into named sections using native `fieldset` and `legend` markup;
- use the existing horizontal field, inline choices, and addon options where they fit;
- give the form a clear action row with primary and secondary actions;
- retain responsive stacking and daisyUI theme behavior.

The preview demonstrates consumer-side template composition. It does not add a form-layout DSL or change the package's default form template.

### 3. App-side HTMX validation recipe

Add a concise, runnable recipe showing a consuming Django view and template handling both normal and HTMX form submissions:

1. Bind the form to `request.POST` and call `is_valid()` on the server.
2. For an ordinary request, render the full page with the form and its errors.
3. For an HTMX request with invalid data, return the rendered form fragment with status `422` so Django's existing error markup is reused.
4. For a valid HTMX request, return a small success fragment with status `200`.
5. Configure HTMX to swap `422` responses. HTMX 2 does not swap `4xx` responses by default; the recipe will show the documented response-handling configuration. The server remains authoritative for validation.

The package itself will not add HTMX, JavaScript, request middleware, or special form response behavior. The recipe will include CSRF handling and explain that a consuming app may change the target and fragment shape to fit its page.

## Compatibility and accessibility

- Existing markup remains unchanged when `label_class` is omitted.
- The option changes CSS classes only; it does not change label text, `for` associations, fieldset semantics, `aria-describedby`, `aria-invalid`, or widget attributes.
- Choice option labels keep their current classes and label/input associations.
- The existing addon modifier behavior and class registry remain unchanged.
- No runtime package dependencies or package-level JavaScript are added.

## Verification approach

Review the rendered output for ordinary fields, checkboxes, grouped choices, and the horizontal template, both with and without `label_class`. Use the existing preview to inspect the composed layout at narrow and wide viewports. Review the HTMX recipe against HTMX 2's documented `422` handling and Django's normal CSRF and form-validation flow. No automated test additions or test commands are part of this design request.

## Scope exclusions

- No generic layout DSL or Crispy Forms integration.
- No Django Components, Labb, django-formset, or django-formify dependency.
- No client-side validation system, dynamic formsets, or package-owned JavaScript.
- No changes to the default field/form layout or to the existing addon modifier implementation.
