from django.apps import AppConfig


class DaisyFormsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "daisy_forms"

    def ready(self) -> None:
        from . import checks  # noqa: F401
