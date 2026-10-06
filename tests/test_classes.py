import re
from pathlib import Path

from daisy_forms.classes import all_classes, daisy_class_for
from daisy_forms.widgets import Toggle


def test_registry_covers_literal_template_classes() -> None:
    template_root = Path("src/daisy_forms/templates/daisy_forms")
    literals: set[str] = set()
    for template in template_root.rglob("*.html"):
        for value in re.findall(r'class="([^"]+)"', template.read_text()):
            literals.update(value.split())

    assert literals <= all_classes()


def test_widget_registry_uses_mro_specificity() -> None:
    assert daisy_class_for(Toggle()) == "toggle"


def test_range_classes_are_in_the_safelist() -> None:
    assert {"range", "range-error"} <= all_classes()
