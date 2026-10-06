from pathlib import Path

from daisy_forms.classes import all_classes

compiled = Path(__file__).with_name("output.css").read_text()
missing = sorted(
    class_name for class_name in all_classes() if class_name not in compiled
)
if missing:
    raise SystemExit(f"Compiled CSS is missing classes: {', '.join(missing)}")
