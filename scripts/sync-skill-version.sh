#!/usr/bin/env bash
# Write the package version into the agent skill so the two never drift.
# tests/test_skill.py fails when they differ; the just bump-* recipes run this.
set -euo pipefail

cd "$(dirname "$0")/.."

version="$(uv version --short)"

python3 - "skills/django-daisy-forms/SKILL.md" "$version" <<'PY'
import re
import sys
from pathlib import Path

path, version = Path(sys.argv[1]), sys.argv[2]
text = path.read_text()
patterns = (
    (r'(?m)^(  version: )"[^"]*"$', rf'\g<1>"{version}"'),
    (r"(describes django-daisy-forms \*\*)[^*]+(\*\*)", rf"\g<1>{version}\g<2>"),
)
for pattern, replacement in patterns:
    text, count = re.subn(pattern, replacement, text, count=1)
    if count != 1:
        raise SystemExit(f"{path}: no match for {pattern!r}")
path.write_text(text)
print(f"{path}: version {version}")
PY
