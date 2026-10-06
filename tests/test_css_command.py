from pathlib import Path

import pytest
from django.core.management import call_command

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

    with pytest.raises(SystemExit) as exc_info:
        call_command("daisy_forms_css", "--output", str(output), "--check")

    assert exc_info.value.code == 1


def test_daisy_forms_css_print_source_path_emits_tailwind_directive(
    capsys: pytest.CaptureFixture[str],
) -> None:
    call_command("daisy_forms_css", "--print-source-path")

    output = capsys.readouterr().out.strip()
    assert output.startswith('@source "')
    assert output.endswith('/templates";')
