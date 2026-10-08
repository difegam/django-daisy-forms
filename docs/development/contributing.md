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
    just init
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
- **prek** for Git hooks (see [Git hooks](index.md#git-hooks))

Run the checks before committing:

```bash
just check
```

### Commit messages

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/). The commit-msg hook rejects other formats. Use a type, an optional scope, and a short imperative summary:

```text
feat: add a label_class option to daisy_field
fix(boundfield): copy input modifiers to text addons
docs: document the range input type
chore(just): add a doc-format-check recipe
ci: build the docs on pull requests
```

Common types are `feat`, `fix`, `docs`, `test`, `refactor`, `build`, `ci`, and `chore`.

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

### Documentation changes

1. Edit the Markdown under `docs/` and preview it with `just doc-serve`
2. Run `just doc-format` to format it
3. Run `just doc-build` to build strictly; warnings fail the build

### CSS changes

If you change the classes used in templates:

1. Add any new layout class to `LAYOUT_CLASSES` in `src/daisy_forms/classes.py`; `tests/test_classes.py` fails when a template class is missing from the registry
2. Run `just css-check` to regenerate the `daisy_forms_css` output, build the Tailwind fixture, and check that every package class is in the compiled CSS
3. Run `just browser-test` to check the layouts in Chromium
4. Note in `CHANGELOG.md` that users must regenerate their `daisy_forms_css` file

## Submitting changes

1. Push your branch to your fork:

    ```bash
    git push origin my-feature
    ```

2. Open a pull request against the `main` branch

3. Describe your changes and link any related issues

4. Run `just verify` locally to run the same checks as CI

5. Wait for CI to pass; `main` requires every check and a squash merge

## Code review

All pull requests are reviewed. The reviewer will check:

- Code quality and style
- Test coverage
- Documentation updates
- Backwards compatibility

## Release process

Releases are managed by the maintainers:

1. Run `just release-notes` to draft the release. It sends the history since
    the latest tag to `claude -p` with all tools disabled and writes a suggested
    version bump, CHANGELOG entries, and GitHub release notes to
    `.release/release.md`.

2. Review the draft and add its entries to `CHANGELOG.md` under a
    `## [X.Y.Z] - YYYY-MM-DD` heading, and update the link references at the
    bottom.

3. Run `just bump-patch`, `just bump-minor`, or `just bump-major`.

4. Open a pull request with the version and changelog changes and merge it.

5. Tag the merge commit and push the tag:

    ```bash
    git tag -a vX.Y.Z -m "django-daisy-forms X.Y.Z"
    git push origin vX.Y.Z
    ```

The release workflow checks that the tag matches the package version and that
`CHANGELOG.md` has a section for it, runs the checks, builds and smoke-tests
both distributions, publishes to PyPI through Trusted Publishing with
provenance attestations, and creates a GitHub Release with the changelog
section and the distribution files.

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
