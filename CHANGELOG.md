# Changelog

All notable changes to this project are documented in this file. The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the
project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Rename the `Unreleased` heading to the version being tagged as part of each
release.

## [Unreleased]

### Added

- `just release-notes`, which drafts the version bump, CHANGELOG entry, and
  GitHub release notes from git history with `claude -p`.
- `DaisyHorizontalFormRenderer`, which renders every field with
  `field_horizontal.html`. Set it as `FORM_RENDERER` or as a form's
  `default_renderer`.
- `fieldsets` form attribute, shaped like the Django admin's, that groups
  `{{ form }}` output into `<fieldset>` sections. Tuples render responsive
  rows of up to four fields and the `collapse` class renders a `<details>`
  section that opens when it contains errors.
- `daisy_fields` form attribute that applies `{% daisy_field %}` options to a
  field wherever it renders, with the same attribute rules.
- `daisy_forms/formset_dynamic.html` (cards) and `daisy_forms/formset_table.html`
  (table rows) formset templates, and the optional
  `static/daisy_forms/js/formset.js` script that adds and removes rows with
  accessible buttons, focus handling, undo for saved rows, `min_num`/`max_num`
  limits, and live announcements. Without the script, the `DELETE` checkbox
  still works.
- Browser tests for the formset script run in CI.

Regenerate the `daisy_forms_css` output: this release adds layout, card,
button, table, and collapse classes.

### Fixed

- Explicitly declared untitled fieldsets now retain their description and extra
  classes instead of rendering only their fields.
- Table formsets now preserve hidden initial values and hidden fields even when
  a row has no visible data columns.
- Removing a saved formset row now suppresses native validation for its visible
  controls while keeping hidden identity and `DELETE` values submitted.
- Subclasses of stock input widgets such as `TextInput`, `EmailInput`, and
  `NumberInput` that keep Django's template now get their daisyUI component and
  error classes. A `NumberInput` subclass with `input_type = "range"` gets
  `range` and `range-error`. Previously these subclasses rendered without
  classes ([#37](https://github.com/difegam/django-daisy-forms/issues/37)).

### Changed

- Grouped choices (optgroups) in `RadioSelect` and `CheckboxSelectMultiple`
  render each group as `<div role="group">` labelled by a `fieldset-legend`
  heading instead of a bare `<div>`.

## [0.1.0] - 2026-10-08

First public release.

### Added

- `DaisyFormRenderer`, which renders `{{ form }}`, `{{ formset }}`, and
  `{{ form.field.as_field_group }}` as daisyUI 5 markup after one
  `FORM_RENDERER` setting.
- `DaisyBoundField` and a widget class registry that maps Django widgets to the
  `input`, `textarea`, `select`, `checkbox`, `radio`, `toggle`, `file-input`,
  and `range` components, with `-error` variants for invalid fields.
- Server-rendered errors with `aria-invalid` and the `{id}_helptext` and
  `{id}_error` ids that Django's `aria-describedby` references.
- `daisy_forms.widgets`: `Toggle`, `NativeDateInput`, `NativeTimeInput`, and
  `NativeDateTimeInput`.
- `{% daisy_field %}` for per-field classes (`class+=`), labels, templates, and
  attributes such as `hx-*`; `label_class=` appends classes to the main label
  or choice-group legend. Inline event handlers and the managed `aria-*`
  attributes are rejected when the template is compiled.
- Opt-in layouts for `{% daisy_field %}`: `daisy_forms/field_horizontal.html`,
  `choices="inline"` for radio and checkbox choices, and escaped text
  `prefix`/`suffix` addons.
- `daisy_forms_css` management command that writes the Tailwind
  `@source inline()` file, with `--check` for CI.
- System checks `daisy_forms.E001` and `daisy_forms.W001` for renderer setup.
- Optional local Playwright browser checks for the form layouts
  (`just browser-setup`, `just browser-test`).

### Changed

- `label_class`, `choices`, `prefix`, and `suffix` are reserved
  `{% daisy_field %}` options.
  Earlier development builds passed them through as HTML attributes. Set the
  HTML `prefix` attribute through widget `attrs` instead.
- The generated `daisy_forms_css` file now includes the layout and addon
  classes. Regenerate it after upgrading.
- CI builds the Tailwind fixture against daisyUI 5.0.36 and 5.7.47.

### Fixed

- Text addons now copy the input's daisyUI size, color, and error modifiers.
  Previously, an invalid field showed neutral addons around a red input, and
  `class+="input-sm"` left the addons at full size.

[Unreleased]: https://github.com/difegam/django-daisy-forms/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/difegam/django-daisy-forms/releases/tag/v0.1.0
