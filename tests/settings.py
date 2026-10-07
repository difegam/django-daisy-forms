from pathlib import Path

SECRET_KEY = "django-daisy-forms-test-key"
TESTS_DIR = Path(__file__).parent

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.forms",
    "daisy_forms",
]

ROOT_URLCONF = "tests.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "DIRS": [TESTS_DIR / "templates"],
        "OPTIONS": {"context_processors": []},
    }
]

USE_TZ = True
FORM_RENDERER = "daisy_forms.renderers.DaisyFormRenderer"
