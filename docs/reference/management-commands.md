# Management commands

django-daisy-forms provides one management command: `daisy_forms_css`. This command generates the Tailwind CSS source file.

## daisy_forms_css

Generates a CSS file with an `@source inline()` directive listing every daisyUI class the package uses.

```bash
python manage.py daisy_forms_css --output static/src/daisy-forms.css
```

This creates a file with an inline source listing all package classes.

Options:

**--output PATH** — Output file path (default: daisy-forms.css in the current directory).

**--check** — Exit with status 1 if the file is missing or differs from what would be generated. Useful for CI to catch drift. Does not write the file.

**--print-source-path** — Print a path-based source directive instead of writing a file. For local development only. Path-based source breaks across environments and containers, so use inline() for production.

The command imports all_classes() from daisy_forms.classes, sorts them alphabetically, writes the inline source directive, and adds a version header. Run after installation, after upgrading, and in CI with --check.

### Committing the file

Commit the generated file to your repository. This ensures that:

- All developers use the same classes
- CI can verify the file is up to date
- Deployment doesn't require running the command

### Example workflow

1. Install the package:

    ```bash
    uv add django-daisy-forms
    ```

2. Generate the CSS source file:

    ```bash
    python manage.py daisy_forms_css --output static/src/daisy-forms.css
    ```

3. Import it in your main CSS file:

    ```css
    @import "tailwindcss";
    @plugin "daisyui";
    @import "./daisy-forms.css";
    ```

4. Commit the generated file:

    ```bash
    git add static/src/daisy-forms.css
    git commit -m "Add daisy-forms CSS source file"
    ```

5. Add a CI check:

    ```yaml
    - name: Check daisy-forms CSS
      run: python manage.py daisy_forms_css --output static/src/daisy-forms.css --check
    ```
