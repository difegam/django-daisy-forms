# Tailwind CSS

Tailwind does not scan `site-packages`. The package ships its class list as a
management command that writes an `@source inline()` file. The project commits that
file.

## Generate

Put the file next to the project's main CSS entry point. Find the entry point by
searching for `@import "tailwindcss"`.

```bash
python manage.py daisy_forms_css --output static/src/daisy-forms.css
```

The output is one line: a version comment plus `@source inline("alert ... w-full")`.

## Import after Tailwind and daisyUI

```css
@import "tailwindcss";
@plugin "daisyui";
@import "./daisy-forms.css";
```

Then rebuild CSS with the project's existing command, such as
`npx @tailwindcss/cli -i ... -o ...`, django-tailwind-cli or a `package.json` script.
If the project has no Tailwind 4.1+ and daisyUI 5.0.36+ build, tell the user. Do not
install one unless asked.

## CI and upgrades

```bash
python manage.py daisy_forms_css --output static/src/daisy-forms.css --check
```

`--check` exits non-zero with `<path> is out of date.` when the file is missing or
stale. Add it to CI, and regenerate the file after every package upgrade.

## Project classes

Classes passed through `class+=`, `class=` or `label_class=`, and classes in custom
field templates, come from the project's own templates. Tailwind generates them only
when it scans those templates, so make sure its sources include the template
directories, or safelist the classes with another `@source inline()`.

## Do not

- Add `@source "<venv>/site-packages/daisy_forms/templates"`. Paths differ across
  machines, Docker images and CI. `daisy_forms_css --print-source-path` prints that
  path for local experiments only.
- Edit the generated file by hand. `--check` fails on any difference.
