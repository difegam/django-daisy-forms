SECRET_KEY = "django-daisy-forms-test-key"

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.forms",
    "daisy_forms",
]

ROOT_URLCONF = "tests.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "DIRS": [],
        "OPTIONS": {"context_processors": []},
    }
]

USE_TZ = True
