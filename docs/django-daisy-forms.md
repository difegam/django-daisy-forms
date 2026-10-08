# django-daisy-forms: Verified Research, Design Changes, and SPEC.md

The approach holds up: a Django-native daisyUI 5 form renderer without crispy is practical on Django 5.2+. The mechanism is a small `TemplatesSetting` subclass, a custom `BoundField`, and focused templates. Per-field customization reuses Django's widget `attrs`, `Field.template_name`, field-level `bound_field_class`, and one attribute-passthrough tag with a few explicit layout options. The real risk is CSS delivery, not rendering: Tailwind 4 does not scan `site-packages`. The contract therefore makes a generated `@source inline()` file, owned by the user's project, part of the public API.

## TL;DR

- **Keep the integration Django-native.** Since Django 5.2, project-wide `BaseRenderer.bound_field_class` exists alongside `form_template_name`/`field_template_name` (5.0). That means `{{ form }}` can render daisyUI markup after one `FORM_RENDERER` line, without overriding Django's global widget templates. Drop `{% render_form %}`, themes, a full layout DSL, Cotton integration, package settings and Pydantic. Use one tag (`{% daisy_field %}`) for field attributes, optional horizontal groups, inline choices, and text addons.
- **Make the CSS contract explicit.** A management command, `daisy_forms_css`, writes a committed `@source inline("…")` file (needs Tailwind ≥ 4.1) generated from a single Python class registry. A test enforces that the registry is a superset of every class used in the package templates. Path-based `@source` into `site-packages` is offered only as a convenience, because the path breaks across venvs and Docker.
- **Server errors are authoritative and accessible by contract.** Error lists are rendered with `id="{auto_id}_error"` and help text with `id="{auto_id}_helptext"`, which are exactly the ids Django 5.2's `BoundField.aria_describedby` references. Error colour comes from `*-error` classes, not daisyUI's client-side `validator`. Kill criterion: if the spike needs global widget-template overrides or more than one Python extension point beyond those listed, contribute to a crispy daisyUI pack instead.

## Key Findings

### 1. Verified prior art

| Project | Verified status (Oct 2026) | Relevance / gap |
|---|---|---|
| django-crispy-forms | 2.7 released 2026-07-29 ("Confirmed support for Django 6.1"); 2.6 dropped Django 4.2–5.1; 5,162 stars and 731 forks on the djangopackages.org "Crispy Forms" grid (GitHub shows "5.2k"), though that grid still lists PyPI 2.6; MIT | The incumbent; FormHelper/Layout DSL is the thing to avoid |
| crispy-tailwind | 1.0.3, no release since Feb 2024; 424 stars and 64 forks, listed "Production/Stable" on the djangopackages.org Crispy Forms grid | Plain Tailwind utilities, not daisyUI |
| crispy-daisyui | 0.13.0 per djangopackages (updated 1 May 2026), 23 stars, Apache-2.0; fork of crispy-tailwind "modified just enough to suit my needs" | Your proposal said "v0.13.0 Feb 2026", but piwheels shows 0.11.1 on 2026-02-12, so 0.13.0 appears to be later. Requires crispy\[1\]\[2\]\[3\] |
| django-mvp-forms | New, pre-release daisyUI crispy pack; its README claims crispy-daisyui has "no test suite" | Shows demand for daisyUI forms with accessible ids; still crispy-bound\[4\]\[5\]\[6\] |
| django-widget-tweaks | 1.5.1, MIT; `{% render_field form.x class+="…" placeholder=… %}` | Proven HTML-like attribute syntax worth copying; no layout or error markup\[7\]\[8\] |
| django-cotton-ui | 0.3.4 released 2026-09-27; "Tailwind CSS v4 and Alpine.js" | Component kit; needs Alpine; not form-rendering-native\[9\] |
| cotton-daisy | 0.0.2 (Nov 2024), CLI that scaffolds daisyUI components for Cotton | Scaffolding, not a renderer\[10\]\[11\] |
| django-tailwind-cli | 4.5.1 (Dec 2025); opt-in `TAILWIND_CLI_AUTO_SOURCE_EXTERNAL_APPS` adds `@source` only for apps "outside both BASE_DIR and site-packages" | Confirms that installed packages are **not** auto-sourced, which is why the safelist is needed\[12\]\[13\] |
| django-template-partials | Merged into core as `{% partialdef %}`/`{% partial %}` in Django 6.0 | Useful for user-side htmx fragments; not usable in package templates while 5.2 is supported\[14\]\[15\] |
| django-formset | Not re-verified this session | Large client-side framework; a different product category |

**Conclusion:** no maintained package renders daisyUI 5 markup from Django's native form rendering API without crispy. The gap is real but narrow, so a small package is the right size.

### 2. Django API verification

- **Django 5.0:** introduced field group templates, `BoundField.as_field_group()`, `BaseRenderer.field_template_name` (default `"django/forms/field.html"`) and `Field.template_name`. It also added `aria-describedby` linking help text and `aria-invalid="true"` on invalid fields (ticket #32820, fixed Aug 2023).\[16\]\[17\]\[18\]
- **Django 5.1:** added `aria-describedby` for widgets rendered in a `<fieldset>` (radios, checkbox groups). The attribute goes on the `<fieldset>`, not on each input.\[19\]\[20\]
- **Django 5.2 (LTS; djangoproject.com/download lists the latest release as 5.2.17, mainstream support ended December 3, 2025, and extended support runs to April 2028):** added `bound_field_class` at three levels: `BaseRenderer.bound_field_class` for the project, `Form.bound_field_class` per form, and `Field.bound_field_class` per field. Ticket #32819 (closed 2025-01-02) finished the error association.\[21\]\[22\] Django's source builds `aria-describedby` from `f"{self.auto_id}_helptext"` and `f"{self.auto_id}_error"`, in that order, and only when help text or errors exist.\[20\] It skips this when the widget is hidden, when `auto_id` is empty, when `aria-describedby` is already in `widget.attrs` or `as_widget(attrs=…)`, and when `widget.use_fieldset` is true. 5.2 also added the `BoundField.aria_describedby` property and `ErrorList(field_id=…)`, so the default error template can render `id="{{ field_id }}_error"`.
- **Django 6.0:** added template partials, built-in CSP, and the Tasks framework. It removed the `DjangoDivFormRenderer`/`Jinja2DivFormRenderer` transitional renderers, and the `URLField` default scheme became `https`.\[23\]\[24\] Django ticket #36772 reported that file inputs lost `aria-describedby` in 6.0, because `ClearableFileInput.use_fieldset = True` trips the `not self.use_fieldset` guard. It was closed as "invalid" in Jan 2026 with the note "This issue was fixed by #36829", and the #36829 commit was backported to 6.0.x. Verified by running Django 5.2.18, 6.0.9 and 6.1.2: `ClearableFileInput.use_fieldset` is `False` on all three, so file inputs keep `aria-describedby`. The attached #36829 patch also sets `use_fieldset = True` only on `AdminFileWidget`.
- **Django 6.1 (released 2026-08-05):** admin forms now show help text "after the field label and before the field input" and validation errors "after the help text and before the field input", with checkboxes excepted. 6.1 also adds the `csp_nonce_attr` tag (which can render a `Media` object with nonces), CSP nonces on all built-in templates, an accessible translatable `BLANK_CHOICE_LABEL`, and calendar versioning, so Django 7.0 becomes "Django 2028".\[25\]
- **No 6.x-only API would materially simplify the design.** Partials could merge the widget templates into one file, but that saves files, not concepts. Stay on the 5.2 floor.

**A renderer subclass is needed, but only a minimal one.** Overriding widget templates requires `TemplatesSetting` (Django docs: "To override widget templates, you must use the TemplatesSetting renderer").\[22\]\[26\]\[27\] A subclass is also the only way to set `bound_field_class` and `field_template_name` project-wide without overriding `django/forms/div.html` and `django/forms/field.html` globally.\[21\]\[28\] There is no renderer-level per-widget template API: it is only proposed in django/new-features #172.\[29\] Widget templates are therefore swapped inside the `BoundField` and never overridden globally.

### 3. daisyUI 5 / Tailwind 4 verification

- **Classes:** daisyUI 5 removed `form-control`, `label-text` and `label-text-alt` in favour of `fieldset` (component), `fieldset-legend` (part) and `label` (component).\[30\]\[31\] Form components are `input`, `select`, `textarea`, `checkbox`, `radio`, `toggle` and `file-input`, each with `-error` colour and `-xs…-xl` size modifiers.\[32\]\[33\] `input` is documented for text-like types; "For checkbox, radio, file, range use their own class names."\[34\]
- **`validator` / `validator-hint`:** these colour fields from native constraint validation. The hint "still occupies space even if it's invisible" unless `hidden` is added.\[35\] Changelog fixes: 5.0.18 "validator working with aria-invalid", 5.0.36 "validator on aria-invalid="false" should not be considered as invalid", and 5.2.4 "style for nested validator with aria-invalid attribute".\[35\]\[36\] **Recommendation:** do not add `validator` by default. It colours valid fields green and duplicates server messages.\[35\] Make it opt-in through `attrs`.
- **`include` / `exclude` plugin options** (e.g. `@plugin "daisyui" { include: button, input, select; }`) restrict which component CSS is available.\[37\] Whether daisyUI 5 emits component CSS for classes Tailwind never detects is **not verified**, so the contract must not depend on it.
- **Tailwind 4:** `@source "<path>"` registers extra paths.\[38\] `@source inline("…")` was added in Tailwind v4.1.0 ("Add @source inline(…) and @source not inline(…) (#17147)") and is brace-expanded. The Tailwind docs say the v3 `safelist` option is "not supported in v4.0. To safelist utilities in v4 use @source inline()." Tailwind scans files as plain text, so dynamically built class names are invisible.
- **htmx 4.0.0 (2026-08-28)** swaps 4xx/5xx responses by default and drops `htmx:validation:*` events in favour of native validation. Attribute inheritance is now explicit (`:inherited`). htmx.org says 4.0 "is not currently marked as latest in NPM… We will mark it latest at some point in 2027"; on npm, `latest` is 2.0.10 and `next` is 4.0.0. This fits a server-authoritative renderer: return a `422` with the re-rendered form or field group and no configuration is needed.

## Recommended Changes to the Proposal

| # | Decision | Recommendation | Tradeoff |
|---|---|---|---|
| 1 | Rendering mechanism | `DaisyFormRenderer(TemplatesSetting)` with 4 class attributes plus `DaisyBoundField` | Requires `django.forms` in `INSTALLED_APPS` (Django requirement for TemplatesSetting)\[27\]\[28\]\[39\] |
| 2 | Per-widget classes | **BoundField class registry** (MRO lookup, dict in `classes.py`) applied in `build_widget_attrs`; no global widget-template overrides | Classes live in Python, so a safelist is mandatory (that is the point of the registry) |
| 3 | Widget templates (radio, checkbox group, clearable file) | Swap `template_name`/`option_template_name` on a **copy** of the widget, only if the widget still uses Django's stock template | Third-party widgets with custom templates are untouched by design |
| 4 | Third-party/custom widgets | Same guard: unknown widgets or customized templates get no daisy class and render inside the standard field wrapper | Custom widgets need an explicit `attrs={"class": …}` to be styled |
| 5 | Template tags | **One tag**: `{% daisy_field bf [label=…] [label_class=…] [template=…] [choices=inline] [prefix=…] [suffix=…] attr=value… %}` with widget-tweaks-style passthrough. Drop `{% render_form %}` (`{{ form }}` works) | Hyphenated attributes (`hx-post`) need a small custom kwarg parser |
| 6 | Python per-field options | No new API: widget `attrs` (classes merge), `Field.template_name`, field-level `bound_field_class`, plus `daisy_forms.widgets` (Toggle, NativeDate/Time/DateTime) | Size and colour variants are spelled as daisyUI classes, not enums |
| 7 | Configuration | **No package settings, no Pydantic.** Configure by subclassing the renderer (class attributes) | Less "magic"; teams that want a toggle subclass in 3 lines |
| 8 | Error UX | Server errors only: `aria-invalid`, ids matching Django, `*-error` classes; `validator` opt-in | No live client feedback by default (use htmx per-field validation) |
| 9 | Field element order | label → help → errors → control, aligned with Django 6.1 admin; checkboxes: control+label, then help, errors | Differs from daisyUI doc examples (help below input); overridable via `field.html`\[25\] |
| 10 | help_text escaping | Render `{{ field.help_text }}` **without** `\|safe`: plain strings are escaped, `mark_safe` strings pass through | Deliberate divergence from Django's documented "isn't HTML-escaped"; document it\[17\] |
| 11 | Tailwind integration | Generated `@source inline()` file in the user's repo, `--check` for CI; path printer as secondary | One extra step on install and upgrade |
| 12 | Themes, layouts, horizontal, Cotton | Themes are pure CSS (`data-theme`), so drop them. Keep layout composition in templates. Horizontal is an opt-in `field_horizontal.html`; inline choices and text addons are direct tag options. Cotton is a docs recipe only | Avoids a general-purpose layout DSL |
| 13 | Tests | Golden-HTML files compared with `assertHTMLEqual` (no syrupy); a real Tailwind build job; axe optional in P1; no visual regression | Golden files must be reviewed on markup changes, which is intended |
| 14 | Packaging | `uv_build` backend (stable; pure Python; templates inside the module root are packaged); MIT; name `django-daisy-forms` / import `daisy_forms` **after** a PyPI 404 check\[40\]\[41\]\[42\] | uv_build has fewer knobs than hatchling, which is fine for pure Python |
| 15 | Type checking | mypy `--strict` + django-stubs (pick one checker); ruff lint and format | django-stubs pins lag Django releases slightly |

**Where the original proposal over-engineers:**
- `render_form`, themes, a general layout DSL, Cotton integration, visual regression, and a settings layer duplicate Django or CSS.

**Where it under-specifies:**
- class merge semantics;
- the exact error and help ids (they must match Django's `aria_describedby`);
- help-text escaping;
- `use_fieldset` widgets, including `ClearableFileInput`;
- the `DateInput` default `type="text"`;
- the impact of the renderer-level `BoundField` on Django admin;
- the Tailwind ≥ 4.1 floor;
- what happens to unknown widgets.

---

# SPEC.md: django-daisy-forms implementation contract

> Normative keywords: MUST, MUST NOT, SHOULD, MAY. Anything not listed here is out of scope until this file changes.

## 1. Goals
1. `{{ form }}`, `{{ formset }}` and `{{ form.x.as_field_group }}` render daisyUI 5 markup after setting `FORM_RENDERER = "daisy_forms.renderers.DaisyFormRenderer"`.
2. Accessible by default: labels, `aria-invalid`, and `aria-describedby` ids that match Django's own conventions.
3. Server-side validation is authoritative, and htmx works without any htmx dependency.
4. Small surface: one renderer, one BoundField, one template tag, four widgets, one management command, one system check module.

## 2. Non-goals
crispy compatibility, FormHelper, a general Layout DSL, Bootstrap or plain-Tailwind renderers, Alpine, JavaScript of any kind, client-side validation logic, themes, package-level settings, Pydantic, Jinja2 support, autocomplete, date pickers, dynamic formsets, multistep wizards.

## 3. Supported versions
- Python ≥ 3.12. Django ≥ 5.2 (`Django>=5.2,<6.2`). CI covers Django 5.2, 6.0 and 6.1 on Python 3.12, 3.13 and 3.14 where Django officially supports the combination.
- Tailwind CSS ≥ 4.1 (needed for `@source inline()`). daisyUI ≥ 5.0.36 (aria-invalid fixes).
- MUST NOT use any Django API newer than 5.2. In particular, package templates MUST NOT use `{% partialdef %}`.

## 4. Public API

### 4.1 Installation
```python
INSTALLED_APPS = [..., "django.forms", "daisy_forms"]
FORM_RENDERER = "daisy_forms.renderers.DaisyFormRenderer"
# TEMPLATES: at least one DjangoTemplates engine with APP_DIRS=True
```

### 4.2 Renderer (`daisy_forms/renderers.py`)
```python
class DaisyFormRenderer(TemplatesSetting):
    form_template_name = "daisy_forms/form.html"
    formset_template_name = "daisy_forms/formset.html"
    field_template_name = "daisy_forms/field.html"
    bound_field_class = DaisyBoundField
```
No other public attributes in P0. Users customize by subclassing it.

### 4.3 `DaisyBoundField` (`daisy_forms/boundfield.py`)
- `build_widget_attrs(attrs, widget)` MUST call `super()` first, so Django's `required`, `disabled`, `aria-invalid` and `aria-describedby` are kept. It then merges `class` in this order, de-duplicated and space-joined:
  1. the registry base class;
  2. `"{base}-error"` if `self.errors` and the widget is not hidden;
  3. existing `widget.attrs["class"]`;
  4. `extra_attrs["class"]` from the tag.
- Other `extra_attrs` keys override widget attrs. The keys `aria-invalid` and `aria-describedby` from tag kwargs are rejected.
- `as_widget(widget=None, attrs=None, only_initial=False)` MUST swap in the package template only on a `copy.copy(widget)`, and only when the widget's `template_name`/`option_template_name` equal the stock value of its nearest registered Django base class.
- Instance attributes: `extra_attrs: dict[str, str]` (default empty), `template_override: str | None`, `label_class: str | None`, `choice_layout: str | None`, `prefix: str | None`, and `suffix: str | None`. These are set only on copies made by the tag.
- A blank `template_override` MUST raise `TemplateDoesNotExist` before Django's template loader runs.
- Escape hatch (documented): set `Field.bound_field_class = forms.BoundField` to opt a field out. An opted-out field cannot be passed to `{% daisy_field %}`, which raises `TemplateSyntaxError`; render it with `{{ field }}` instead.

### 4.4 Class registry (`daisy_forms/classes.py`)
```python
WIDGET_CLASSES: Final[Mapping[type[Widget], str | None]] = {
    HiddenInput: None, Textarea: "textarea", Select: "select",
    CheckboxInput: "checkbox", Toggle: "toggle",
    CheckboxSelectMultiple: "checkbox", RadioSelect: "radio",
    FileInput: "file-input", Input: "input",
}
LAYOUT_CLASSES: Final[frozenset[str]]  # every class literal used in package templates
def daisy_class_for(widget: Widget) -> str | None: ...  # first hit in type(widget).__mro__
def all_classes() -> frozenset[str]: ...  # base + "-error" variants + LAYOUT_CLASSES
```
Unregistered widgets (e.g. `MultiWidget`/`SplitDateTimeWidget` in P0) return `None` and render unchanged inside the wrapper.

### 4.5 Widgets (`daisy_forms/widgets.py`)
- `Toggle(CheckboxInput)`, rendered with `class="toggle"`.
- `NativeDateInput(DateInput)`: `input_type="date"`, `format="%Y-%m-%d"`.
- `NativeTimeInput(TimeInput)`: `input_type="time"`, `format="%H:%M"`.
- `NativeDateTimeInput(DateTimeInput)`: `input_type="datetime-local"`, `format="%Y-%m-%dT%H:%M"`.

Stock `DateInput` and the other stock widgets keep Django's defaults (`type="text"`); the package MUST NOT change input types silently.

### 4.6 Template tag (`{% load daisy_forms %}`)
```django
{% daisy_field form.email label="Work email" class="input-sm" hx-post="/validate/email/" hx-trigger="blur" %}
{% daisy_field form.email label_class="text-primary" %}
{% daisy_field form.bio template="daisy_forms/field_horizontal.html" %}
{% daisy_field form.plan choices="inline" %}
{% daisy_field form.price prefix="$" suffix="USD" %}
```
- Grammar: `{% daisy_field <bound_field> (<name>(=|+=)<expr>)* %}`. Names match `^[A-Za-z_][A-Za-z0-9_:.\-]*$`. Values are template expressions.
- Reserved names: `label` (overrides label text), `label_class` (appends classes to the main label or choice-group legend), `template` (field group template), `choices` (`inline` for stock `RadioSelect` and `CheckboxSelectMultiple`), and `prefix`/`suffix` (escaped text for stock widgets rendered with daisyUI's `input` component). Every other name becomes a widget attribute. `class=` and `class+=` both **append** to daisy classes; `+=` is accepted for parity with django-widget-tweaks and is rejected on any other name.
- `label_class` affects the primary label for ordinary fields, the standalone label for checkbox/toggle fields, and the legend for grouped choices. It does not affect individual choice option labels. The package's default and horizontal templates render it; custom field templates are responsible for applying `field.label_class` if desired. Since the value is supplied by the project, include custom classes in the project's Tailwind scan or safelist.
- `choices` accepts only `inline`; unsupported values, widget types, or custom choice templates MUST raise `TemplateSyntaxError`. The default choice layout remains vertical.
- `prefix` and `suffix` MUST only be accepted for stock, visible, single-line widgets rendered with daisyUI's `input` component. Hidden, checkbox, radio, file, range, color, and custom-template widgets are rejected. Text addons MUST be escaped and MUST NOT accept HTML or icon markup. Addons MUST mirror the control's daisyUI `input-*` size, colour and error modifiers so the joined group renders as one control.
- `label_class`, `choices`, `prefix` and `suffix` are reserved `{% daisy_field %}` options. Earlier builds passed `choices`, `prefix`, and `suffix` through as widget attributes. Set the HTML `prefix` attribute (RDFa) through widget `attrs` instead.
- MUST raise `TemplateSyntaxError` (case-insensitively) for inline-handler names (`on*`, `hx-on*`, `x-on*`, `x-init`, with an optional `data-` prefix) and for `aria-invalid`/`aria-describedby`.
- MUST raise `ValueError` at render time when the argument does not resolve to a bound field (for example a mistyped field name).
- Renders `copy.copy(bf)` with overrides through `as_field_group()` (or the template override). It never mutates the form.

### 4.7 Management command
`python manage.py daisy_forms_css [--output PATH] [--check] [--print-source-path]`
- Default output is `daisy-forms.css`, containing a header comment with the package version and one line: `@source inline("<sorted all_classes() joined by space>");`.
- `--check` exits 1 if PATH differs from what would be generated (for CI).
- `--print-source-path` prints `@source "<abs path to daisy_forms/templates>";` and is documented as local-dev only.

### 4.8 System checks (`daisy_forms/checks.py`)
- `daisy_forms.E001`: `django.forms` missing from `INSTALLED_APPS`.
- `daisy_forms.W001`: `FORM_RENDERER` is not `DaisyFormRenderer` or a subclass of it.

### 4.9 Template override points
Users override these by placing same-named files in their project `TEMPLATES["DIRS"]`:
- `daisy_forms/form.html`
- `daisy_forms/formset.html`
- `daisy_forms/field.html`
- `daisy_forms/_field_meta.html` (help text and errors, included by `field.html`; a custom `field.html` must ship or replace it)
- `daisy_forms/field_horizontal.html`
- `daisy_forms/widgets/radio.html`, `radio_option.html`, `checkbox_select.html`, `checkbox_option.html`, `clearable_file_input.html`
- `daisy_forms/widgets/radio_inline.html`, `checkbox_select_inline.html`

Template names are public API, and renames are breaking changes.

## 5. Markup contract (daisyUI 5)

`field_horizontal.html` preserves the field markup and accessibility rules below while placing the label beside the control at larger breakpoints. The default `field.html` remains unchanged. `choices="inline"` swaps only the outer container of stock radio and checkbox choice widgets to a wrapping row. Text addons wrap the control in `<div class="join w-full">`; each addon is `<span class="input … join-item w-auto">` carrying the same daisyUI `input-*` size, colour and error modifiers as the control (for example `input-sm`, `input-primary`, `input-error`), and the control drops `w-full` for `join-item flex-1`.

Rules that apply to every field:
- The wrapper is `<div class="fieldset">` for single controls and `<fieldset class="fieldset">` + `<legend class="fieldset-legend">` when `field.use_fieldset` (RadioSelect and CheckboxSelectMultiple; `ClearableFileInput` is `False` on 5.2, 6.0 and 6.1, but the template reads `field.use_fieldset`, so it follows Django).
- The `<fieldset>` gets `aria-describedby="{{ field.aria_describedby }}"` when that value is non-empty, which mirrors Django.\[20\]
- Help text is `<p class="label" id="{auto_id}_helptext">` and is rendered whenever `help_text` is set. Django references that id even if a template omits it.\[43\]
- Errors are `<ul class="text-error text-sm" id="{auto_id}_error">` with one `<li>` per error, rendered whenever errors exist.\[44\]
- The required marker is `<span class="text-error" aria-hidden="true"> *</span>` inside the label. The `required` attribute comes from Django.
- Order: label, help, errors, control. Checkbox and Toggle use control + label inline, then help, then errors.

**Text-like** (TextInput, EmailInput, URLInput, NumberInput, PasswordInput, DateInput, DateTimeInput, TimeInput, Native*), shown here in the error state:
```html
<div class="fieldset">
  <label class="fieldset-legend" for="id_email">Email<span class="text-error" aria-hidden="true"> *</span></label>
  <p class="label" id="id_email_helptext">We never share it.</p>
  <ul class="text-error text-sm" id="id_email_error"><li>Enter a valid email address.</li></ul>
  <input type="email" name="email" value="x" class="input input-error w-full" required aria-invalid="true" aria-describedby="id_email_helptext id_email_error" id="id_email">
</div>
```
The default state is the same without `input-error`, `aria-invalid` and the `<ul>`. The disabled state adds `disabled`.

**Textarea / Select / SelectMultiple / NullBooleanSelect**: same wrapper. The control class is `textarea w-full` or `select w-full`, plus `-error` when invalid. Whether `select` styling suits `multiple` MUST be checked in the spike.

**FileInput**: `class="file-input w-full"` (+ `file-input-error`). **ClearableFileInput**: a package template renders the current-file link (escaped `href` and text), then `<label class="label"><input type="checkbox" class="checkbox" name="{name}-clear" id="{name}-clear_id"> Clear</label>`, then the file input.

**CheckboxInput / Toggle:**
```html
<div class="fieldset">
  <label class="label" for="id_terms">
    <input type="checkbox" name="terms" class="checkbox checkbox-error" required aria-invalid="true" aria-describedby="id_terms_error" id="id_terms"> I accept the terms
  </label>
  <ul class="text-error text-sm" id="id_terms_error"><li>This field is required.</li></ul>
</div>
```

**RadioSelect** (CheckboxSelectMultiple is identical with `checkbox` classes):
```html
<fieldset class="fieldset" aria-describedby="id_plan_helptext id_plan_error">
  <legend class="fieldset-legend">Plan</legend>
  <p class="label" id="id_plan_helptext">Change any time.</p>
  <ul class="text-error text-sm" id="id_plan_error"><li>Select a valid choice.</li></ul>
  <div id="id_plan" class="flex flex-col gap-2">
    <label class="label" for="id_plan_0"><input type="radio" name="plan" value="basic" class="radio radio-error" required aria-invalid="true" id="id_plan_0"> Basic</label>
  </div>
</fieldset>
```

**Form** (`form.html`): non-field and hidden-field errors (Django's `errors` context) render first as `<div role="alert" class="alert alert-error alert-soft"><ul>…</ul></div>`, then each visible field's `as_field_group`, then hidden fields raw with no wrapper.
**Formset** (`formset.html`): `{{ formset.management_form }}`, then `non_form_errors` in the same alert markup, then each form.

## 6. Tailwind source-integration contract
1. Every class literal in package templates MUST appear in `LAYOUT_CLASSES` or be derivable from `WIDGET_CLASSES`. A test parses all package templates and fails on any class missing from `all_classes()`.
2. Templates MUST NOT build class names dynamically (no `input-{{ size }}`).
3. Documented user setup is `@import "tailwindcss"; @plugin "daisyui"; @import "./daisy-forms.css";`, with `daisy_forms_css --check` in the user's CI after upgrades.
4. User-overridden templates live in the user's project and are scanned normally.

## 7. Security requirements
1. Package templates MUST NOT use `|safe`, `{% autoescape off %}` or `mark_safe` on labels, help text, errors, choice labels, values or attrs. Help text is escaped unless the developer passed a `SafeString`.
2. Attributes are emitted only through Django's widget attrs rendering (escaped). Python code MUST use `format_html` and never f-string HTML.
3. The tag rejects `on*`, `hx-on*`, `x-on*` and `x-init` inline-handler attributes. The package ships no inline `<script>` or `style=`, so it is CSP-neutral under Django 6.0+ CSP.
4. An XSS test suite injects `<script>`, `"><img onerror>` and quote characters into labels, help text, choices, errors, initial values and tag values, and asserts the output is escaped.

## 8. Project layout (uv, src layout)
```
pyproject.toml          # build-backend = "uv_build" (bounded); license = "MIT"
src/daisy_forms/
  __init__.py  apps.py  renderers.py  boundfield.py  classes.py
  widgets.py   checks.py  py.typed
  templatetags/daisy_forms.py
  management/commands/daisy_forms_css.py
  templates/daisy_forms/{form,formset,field}.html
  templates/daisy_forms/widgets/*.html
tests/  golden/<widget>__<state>.html  test_*.py  tailwind/{input.css,package.json}
noxfile.py → NOT used; matrix lives in CI via `uv run --with "django~=X.Y"`
```
Tooling: `uv sync`, `uv run pytest`, `uv run mypy --strict src` (django-stubs plugin), `uv run ruff check && ruff format --check`, `uv build`. Optional local visual checks use `just browser-setup`, `just browser-test`, `just browser-preview`, and `just browser-cli`; marked browser checks are excluded from default test and CI runs.

## 9. Testing & CI contract
- **Unit/golden:** pytest + pytest-django. Scalar, checkbox, grouped-choice and clearable-file fields are compared with canonical golden HTML using `assertHTMLEqual`; specialised tests cover widget classes, error states, disabled fields and attribute handling. Golden files are the markup contract in §5.
- **A11y invariants (programmatic):** for every rendered field, each id in `aria-describedby` exists in the output; invalid visible controls carry `aria-invalid="true"`; every visible control has a `<label for>` or sits inside a `<fieldset>` with a `<legend>`.
- **Registry test:** the template-class scan is a subset of `all_classes()` (§6.1).
- **CSS job:** install `tailwindcss`, `@tailwindcss/cli` and `daisyui@5` via npm, as a matrix over the supported floor (daisyUI 5.0.36) and the locked fixture version (5.7.47). Build `tests/tailwind/input.css` (imports the generated file and has no `@source` to site-packages). Assert compiled CSS contains a selector for every class in `all_classes()`.
- **Matrix:** GitHub Actions over Python {3.12, 3.13, 3.14} × Django {5.2, 6.0, 6.1}, plus a `main` (allowed-failure) job.
- **Admin smoke test:** render a `ModelAdmin` change form under `DaisyFormRenderer`; it MUST not raise, and the diff vs the stock renderer is limited to added `class` tokens.
- **Release gate:** all jobs green, `uv build` produces a wheel that contains templates and `py.typed`, and the version is in the CHANGELOG.

**Acceptance criteria (P0 done):**
1. `{{ form }}` with all 17 listed widgets matches its golden files on all matrix cells.
2. A formset with a prefix renders unique ids and a management form.
3. The XSS suite passes.
4. The CSS job passes.
5. mypy strict passes with zero `type: ignore` in `src/` (outside of explicitly justified lines).
6. `daisy_forms_css --check` round-trips.
7. Dogfooded in at least one of the author's htmx projects, with a per-field `422` validation recipe documented.

## 10. Milestones
- **Spike (≤ 3 days):**
  - Scope: renderer, BoundField, `field.html`, `form.html`, and text, select, textarea, checkbox and radio on Django 5.2 and 6.1.
  - Golden tests and the CSS job.
  - Verify: admin impact; `select[multiple]` styling; whether daisyUI emits component CSS without detection; `@source inline()` inside an imported file.
- **P0 (0.1.0):** all §5 widgets, formsets, the tag, the widgets module, the command, checks, docs and full CI.
- **P1 (0.2.x):**
  - Done (unreleased): `field_horizontal.html`, inline choice layouts, and text prefix/suffix addons;
  - Done (unreleased): README examples for the opt-in field layouts and addons;
  - Done (unreleased): optional local Playwright browser checks (`just browser-test`); axe is still open;
  - MultiWidget/SplitDateTime templates;
  - Done (unreleased): whole-form htmx 2 validation using a re-rendered `422` fragment (see [`docs/recipes/htmx-form-validation.md`](recipes/htmx-form-validation.md));
  - htmx 4 validation and response-handling updates, plus a Django 6 partials recipe;
  - documented size and colour class recipes.
- **P2 (not committed):** autocomplete, pickers, dynamic formsets, multistep. Each needs a separate proposal.

## 11. Kill / pivot criteria
Stop building and contribute a daisyUI 5 template pack to an existing crispy pack (crispy-daisyui or django-mvp-forms) if the spike shows any of the following:
- (a) correct markup needs overriding Django's global `django/forms/widgets/*` or `django/forms/field.html` templates;
- (b) per-field customization needs any Python extension point beyond renderer subclass, `DaisyBoundField`, widget `attrs`, `Field.template_name`/`bound_field_class` and `{% daisy_field %}`;
- (c) the safelist approach cannot make the CSS job pass on Tailwind 4.1+ with daisyUI 5;
- (d) admin rendering breaks in a way the BoundField cannot avoid without per-form opt-in. In that case, pivot to a form-level `bound_field_class` mixin instead of the renderer-level default before killing.

## Caveats
- PyPI name availability for `django-daisy-forms`, `daisy-forms`, `django-daisyui-forms`, `django-daisyforms` and `daisyforms` could not be confirmed: none turned up in searches, but no direct 404 check was done. Run `curl -sf https://pypi.org/pypi/<name>/json` before committing. PyPI treats `-`, `_` and `.` as equivalent and may reject names that are too similar to existing ones.
- Whether daisyUI 5 emits component CSS for undetected classes and how daisyUI styles `select[multiple]` are not verified. Each of these is an explicit spike check, not an assumption. Django ticket #36772 (file input `aria-describedby` in 6.0) is resolved: #36829 restored `ClearableFileInput.use_fieldset = False`, confirmed on 5.2.18, 6.0.9 and 6.1.2.
- The renderer-level `bound_field_class` also applies to Django admin forms. The expected effect is extra, unstyled class tokens, because admin does not load daisyUI CSS. This is a spike verification item with a defined fallback (§11d).
- django-formset's current status was not re-verified. The star counts come from djangopackages snapshots and are approximate.

## Sources

1. [crispy daisyui](https://pypi.org/project/crispy-daisyui/)
2. [piwheels - crispy-daisyui](https://www.piwheels.org/project/crispy-daisyui/)
3. [Crispy Forms](https://djangopackages.org/grids/g/crispy-forms-packages/)
4. [FS-002: Choice, boolean and file inputs drawn as daisyUI · Issue #6 · django-mvp/django-mvp-forms](https://github.com/django-mvp/django-mvp-forms/issues/6)
5. [A single form field doesn't tie its help text and errors to the control · Issue #412 · django-mvp/django-mvp](https://github.com/django-mvp/django-mvp/issues/412)
6. [GitHub - django-mvp/django-mvp-forms: A daisyUI template pack for django-crispy-forms, with form fields and widgets for django-mvp projects · GitHub](https://github.com/django-mvp/django-mvp-forms)
7. [django-widget-tweaks/README.rst at master · jazzband/django-widget-tweaks](https://github.com/jazzband/django-widget-tweaks/blob/master/README.rst)
8. [django-widget-tweaks: Style Django Forms in Templates](https://openapps.pro/packages/django-widget-tweaks)
9. [django-cotton-ui · PyPI](https://pypi.org/project/django-cotton-ui/0.3.4/)
10. [Ecosystem - Django Cotton](https://django-cotton.com/docs/ecosystem)
11. [cotton-daisy · PyPI](https://pypi.org/project/cotton-daisy/)
12. [Releases · django-commons/django-tailwind-cli](https://github.com/django-commons/django-tailwind-cli/releases)
13. [Django Packages : Reusable apps, sites and tools directory for Django](https://djangopackages.org/grids/g/tailwindcss/)
14. [Django 6.0 release notes](https://docs.djangoproject.com/en/6.1/releases/6.0/)
15. [Django: what’s new in 6.0 - Adam Johnson](https://adamj.eu/tech/2025/12/03/django-whats-new-6.0/)
16. [Django 5.0 release notes](https://docs.djangoproject.com/en/6.1/releases/5.0/)
17. [Form fields](https://docs.djangoproject.com/en/5.2/ref/forms/fields/)
18. [#32820 (Fields’ errors should be programmatically associated with fields.) – Django](https://code.djangoproject.com/ticket/32820)
19. [Django 5.1 release notes — Django 5.2.17.dev20260714173342 documentation](https://django.readthedocs.io/en/5.2.x/releases/5.1.html)
20. [#32819 (Fields’ help text and errors should be associated with input)](https://code.djangoproject.com/ticket/32819)
21. [The form rendering API — Django 6.0.2 documentation](https://django.readthedocs.io/en/stable/ref/forms/renderers.html)
22. [The Form Rendering API - Django 6.0 - W3cubDocs](https://docs.w3cub.com/django~6.0/ref/forms/renderers)
23. [The form rendering API — Django 5.2.8.dev20251017180519 documentation](https://django.readthedocs.io/en/5.2.x/ref/forms/renderers.html)
24. [django.forms.renderers](https://docs.djangoproject.com/en/5.0/_modules/django/forms/renderers/)
25. [Django 6.1 release notes | Django documentation](https://docs.djangoproject.com/en/6.1/releases/6.1/)
26. [The form rendering API](https://docs.djangoproject.com/en/5.1/ref/forms/renderers/)
27. [The form rendering API](https://django.fun/docs/django/4.0/ref/forms/renderers/)
28. [Rendering form fields as group in Django](https://www.valentinog.com/blog/django-form-field-as-group/)
29. [Allow Widgets templates to be specified in a FormRenderer class · Issue #172 · django/new-features](https://github.com/django/new-features/issues/172)
30. [Tailwind Fieldset Component](https://daisyui.com/components/fieldset/)
31. [daisyUI Changelog — daisyUI Tailwind CSS Component UI Library](https://daisyui.com/docs/changelog/?lang=cs)
32. [daisyUI 5 release notes — daisyUI Tailwind CSS Component UI Library](https://daisyui.com/docs/v5/?lang=en)
33. [Tailwind Toggle Component](https://daisyui.com/components/toggle/?lang=en)
34. [Tailwind Text Input Component](https://daisyui.com/components/input/)
35. [Tailwind Validator Component – daisyUI](https://daisyui.com/components/validator/)
36. [daisyUI Changelog — daisyUI Tailwind CSS Component UI Library](https://daisyui.com/docs/changelog/?lang=en)
37. [Config — daisyUI Tailwind CSS Component UI Library](https://daisyui.com/docs/config/)
38. [Installation — Django-Tailwind 2.0.0 documentation](https://django-tailwind.readthedocs.io/en/latest/installation.html)
39. [Django: Customizing how a model form renders fields](https://nemecek.be/blog/175/django-customizing-how-a-model-form-renders-fields)
40. [The uv build backend - Astral Docs](https://docs.astral.sh/uv/concepts/build-backend/)
41. [The uv build backend is now stable](https://pydevtools.com/blog/uv-build-backend/)
42. [Creating projects](https://docs.astral.sh/uv/concepts/projects/init/)
43. [Fix clock-sensitive visual baselines and overview date ARIA by Kauror · Pull Request #239 · Kauror/juristid](https://github.com/Kauror/juristid/pull/239)
44. [The Forms API](https://docs.djangoproject.com/en/6.0/ref/forms/api/)
