import os
import sys
from pathlib import Path

import django
from django.apps import apps

sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")
django.setup()

assert apps.is_installed("daisy_forms")
print("daisy_forms smoke test passed")
