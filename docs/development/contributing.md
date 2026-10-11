# Contributing

Thank you for your interest in contributing to django-daisy-forms! This guide will help you get started.

## Getting started

Fork the repository on GitHub and clone your fork:

```bash
git clone https://github.com/your-username/django-daisy-forms.git
cd django-daisy-forms
```

Set up the development environment:

```bash
just init
```

Create a branch for your changes:

```bash
git checkout -b my-feature
```

## Making changes

### Code style

The project uses Ruff for formatting and linting, mypy for type checking in strict mode with django-stubs, and prek for Git hooks (see [Git hooks](index.md#git-hooks)). Run checks before committing:

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

Write tests first (TDD approach). Ensure the feature works across all supported Django versions (5.2, 6.0, 6.1). Update documentation and add an entry to CHANGELOG.md under Unreleased.

### Bug fixes

Write a test that reproduces the bug, fix it, ensure the test passes, and run the full check suite.

### Documentation changes

Edit the Markdown under `docs/` and preview with `just doc-serve`. Format with `just doc-format` and build strictly with `just doc-build`; warnings fail the build.

### CSS changes

If you change template classes, add new layout classes to `LAYOUT_CLASSES` in `src/daisy_forms/classes.py`. Run `just css-check` to regenerate output and verify all classes are in compiled CSS. Run `just browser-test` to check layouts. Note in CHANGELOG.md that users must regenerate their CSS file.

## Submitting changes

Push your branch to your fork:

```bash
git push origin my-feature
```

Open a pull request against main, describing your changes and linking related issues. Run `just verify` locally to run the same checks as CI. Wait for CI to pass; main requires every check and a squash merge.

## Code review

All pull requests are reviewed for code quality, style, test coverage, documentation updates, and backwards compatibility.

## Release process

Releases are managed by the maintainers. Run `just release-notes` to draft the release with Claude Code CLI. It sends commits, diffs, and CHANGELOG sections to generate suggested changes and write them to `.release/release.md`. Review the draft and add its entries to CHANGELOG.md under a `## [X.Y.Z] - YYYY-MM-DD` heading.

Run `just bump-patch`, `just bump-minor`, or `just bump-major` to update the version and lockfile. Run `just skill-refresh` to update the agent skill. Open a pull request with version, changelog, and skill changes and merge it.

Tag the merge commit and push:

```bash
git tag -a vX.Y.Z -m "django-daisy-forms X.Y.Z"
git push origin vX.Y.Z
```

The release workflow verifies the tag matches the package version, runs all checks, builds and smoke-tests distributions, publishes to PyPI through Trusted Publishing, and creates a GitHub Release. Before the first release, configure a PyPI trusted publisher for this repository.

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
