import tomllib
from pathlib import Path


def test_type_configuration_uses_django_stubs() -> None:
    configuration = tomllib.loads(Path("pyproject.toml").read_text())

    assert configuration["tool"]["mypy"]["plugins"] == ["mypy_django_plugin.main"]
    assert (
        configuration["tool"]["django-stubs"]["django_settings_module"]
        == "tests.settings"
    )
