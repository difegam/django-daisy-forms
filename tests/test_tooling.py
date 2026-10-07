import tomllib
from pathlib import Path

from packaging.requirements import Requirement


def test_type_configuration_uses_django_stubs() -> None:
    configuration = tomllib.loads(Path("pyproject.toml").read_text())

    assert configuration["tool"]["mypy"]["plugins"] == ["mypy_django_plugin.main"]
    assert (
        configuration["tool"]["django-stubs"]["django_settings_module"]
        == "tests.settings"
    )


def test_django_dependency_excludes_unverified_releases() -> None:
    configuration = tomllib.loads(Path("pyproject.toml").read_text())
    requirement = Requirement(configuration["project"]["dependencies"][0])

    assert "6.1" in requirement.specifier
    assert "6.2" not in requirement.specifier


def test_ci_declares_each_supported_django_series() -> None:
    workflow = Path(".github/workflows/ci.yml").read_text()

    for version in ("5.2", "6.0", "6.1"):
        assert f'"{version}"' in workflow


def test_readme_documents_tailwind_source_contract() -> None:
    readme = Path("README.md").read_text()

    assert "Tailwind CSS 4.1" in readme
    assert "daisy_forms_css" in readme


def test_readme_documents_quality_entry_point() -> None:
    assert "just check" in Path("README.md").read_text()
