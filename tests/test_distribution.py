import subprocess
import tarfile
from pathlib import Path
from zipfile import ZipFile

from django.conf import LazySettings


def test_django_uses_project_test_settings(settings: LazySettings) -> None:
    assert settings.ROOT_URLCONF == "tests.urls"


def test_wheel_contains_typed_package(dist_path: Path) -> None:
    with ZipFile(next(dist_path.glob("*.whl"))) as archive:
        assert any(name.endswith("daisy_forms/py.typed") for name in archive.namelist())


def test_wheel_contains_renderer_templates(dist_path: Path) -> None:
    with ZipFile(next(dist_path.glob("*.whl"))) as archive:
        names = archive.namelist()
        assert "daisy_forms/templates/daisy_forms/form.html" in names
        assert "daisy_forms/templates/daisy_forms/widgets/radio.html" in names


def test_source_distribution_contains_typed_package(dist_path: Path) -> None:
    with tarfile.open(next(dist_path.glob("*.tar.gz"))) as archive:
        assert any(name.endswith("daisy_forms/py.typed") for name in archive.getnames())


def test_wheel_imports_in_an_isolated_environment(dist_path: Path) -> None:
    wheel = next(dist_path.glob("*.whl"))

    result = subprocess.run(
        [
            "uv",
            "run",
            "--isolated",
            "--no-project",
            "--with",
            str(wheel),
            "python",
            "-c",
            "import daisy_forms; print(daisy_forms.__name__)",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip() == "daisy_forms"
