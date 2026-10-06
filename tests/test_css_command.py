from pathlib import Path

import pytest
from django.core.management import CommandError, call_command

from daisy_forms.classes import all_classes


def test_daisy_forms_css_writes_sorted_tailwind_source(tmp_path: Path) -> None:
    output = tmp_path / "daisy-forms.css"

    call_command("daisy_forms_css", "--output", str(output))

    contents = output.read_text()
    assert '@source inline("' in contents
    assert " ".join(sorted(all_classes())) in contents


def test_daisy_forms_css_check_detects_drift(tmp_path: Path) -> None:
    output = tmp_path / "daisy-forms.css"
    output.write_text("stale")

    with pytest.raises(CommandError, match="out of date"):
        call_command("daisy_forms_css", "--output", str(output), "--check")


def test_daisy_forms_css_print_source_path_emits_tailwind_directive(
    capsys: pytest.CaptureFixture[str],
) -> None:
    call_command("daisy_forms_css", "--print-source-path")

    output = capsys.readouterr().out.strip()
    assert output.startswith('@source "')
    assert output.endswith('/templates";')


def test_generated_css_header_marks_unknown_version_when_not_installed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from importlib.metadata import PackageNotFoundError

    from daisy_forms.management.commands import daisy_forms_css

    def missing(name: str) -> str:
        raise PackageNotFoundError(name)

    monkeypatch.setattr(daisy_forms_css, "version", missing)

    assert "django-daisy-forms unknown." in daisy_forms_css.generated_css()
