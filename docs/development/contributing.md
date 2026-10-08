# Contributing

Thank you for your interest in contributing to django-daisy-forms! This guide will help you get started.

## Getting started

1. Fork the repository on GitHub
2. Clone your fork locally:

    ```bash
    git clone https://github.com/your-username/django-daisy-forms.git
    cd django-daisy-forms
    ```

3. Set up the development environment:

    ```bash
    uv sync --all-groups
    uv run prek install
    ```

4. Create a branch for your changes:

    ```bash
    git checkout -b my-feature
    ```

## Making changes

### Code style

The project uses:

- **Ruff** for formatting and linting
- **mypy** for type checking (strict mode with django-stubs)
- **prek** for pre-commit hooks

Run the checks before committing:

```bash
just check
```

### Adding features

When adding a new feature:

1. Write tests first (TDD approach)
2. Ensure the feature works across all supported Django versions (5.2, 6.0, 6.1)
3. Update documentation if needed
4. Add an entry to `CHANGELOG.md` under the `Unreleased` section

### Bug fixes

When fixing a bug:

1. Write a test that reproduces the bug
2. Fix the bug
3. Ensure the test passes
4. Run the full check suite

### CSS changes

If you change the classes used in templates:

1. Run `just css-check` to regenerate the CSS fixture
2. Verify the changes render correctly

The CSS check ensures every class in the templates is included in the `@source inline()` output.

## Submitting changes

1. Push your branch to your fork:

    ```bash
    git push origin my-feature
    ```

2. Open a pull request against the `main` branch
3. Describe your changes and link any related issues
4. Wait for CI to pass

## Code review

All pull requests are reviewed. The reviewer will check:

- Code quality and style
- Test coverage
- Documentation updates
- Backwards compatibility

## Release process

Releases are managed by the maintainers. The process:

1. Choose the release level (patch, minor, major)
2. Run `just bump-patch`, `just bump-minor`, or `just bump-major`
3. Review and commit the version changes
4. Merge to `main`
5. Push a matching semantic version tag (e.g., `v0.1.0`)

The release workflow checks the tag, rebuilds artifacts, adds provenance attestations, and publishes through PyPI Trusted Publishing.

## Reporting issues

Report bugs and request features on the [GitHub Issues](https://github.com/difegam/django-daisy-forms/issues) page.

When reporting a bug, include:

- Python version
- Django version
- Steps to reproduce
- Expected vs actual behavior
- Minimal reproduction case if possible

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
