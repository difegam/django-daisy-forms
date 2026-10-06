"""Django system checks for renderer setup."""

from collections.abc import Sequence

from django.apps import AppConfig
from django.conf import settings
from django.core import checks
from django.utils.module_loading import import_string


@checks.register(checks.Tags.templates)
def check_daisy_forms_configuration(
    app_configs: Sequence[AppConfig] | None = None, **kwargs: object
) -> list[checks.CheckMessage]:
    messages: list[checks.CheckMessage] = []
    if "django.forms" not in settings.INSTALLED_APPS:
        messages.append(
            checks.Error(
                '"django.forms" must be in INSTALLED_APPS for DaisyFormRenderer.',
                id="daisy_forms.E001",
            )
        )

    renderer_path = getattr(settings, "FORM_RENDERER", "")
    from .renderers import DaisyFormRenderer

    try:
        renderer = import_string(renderer_path)
    except ImportError as exc:
        messages.append(
            checks.Warning(
                f"FORM_RENDERER {renderer_path!r} could not be imported: {exc}",
                id="daisy_forms.W001",
            )
        )
    else:
        if not (isinstance(renderer, type) and issubclass(renderer, DaisyFormRenderer)):
            messages.append(
                checks.Warning(
                    "FORM_RENDERER is not DaisyFormRenderer or a subclass of it.",
                    id="daisy_forms.W001",
                )
            )
    return messages
