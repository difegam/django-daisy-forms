# Changelog

All notable changes to this project are documented in this file. The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the
project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Rename the `Unreleased` heading to the version being tagged as part of each
release.

## [Unreleased]

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
  attributes such as `hx-*`. Inline event handlers and the managed `aria-*`
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

- `choices`, `prefix`, and `suffix` are reserved `{% daisy_field %}` options.
  Earlier development builds passed them through as HTML attributes. Set the
  HTML `prefix` attribute through widget `attrs` instead.
- The generated `daisy_forms_css` file now includes the layout and addon
  classes. Regenerate it after upgrading.
- CI builds the Tailwind fixture against daisyUI 5.0.36 and 5.7.47.

### Fixed

- Text addons now copy the input's daisyUI size, color, and error modifiers.
  Previously, an invalid field showed neutral addons around a red input, and
  `class+="input-sm"` left the addons at full size.
