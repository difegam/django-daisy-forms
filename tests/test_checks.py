from django.test import override_settings

from daisy_forms.checks import check_daisy_forms_configuration


@override_settings(
    INSTALLED_APPS=["daisy_forms"],
    FORM_RENDERER="django.forms.renderers.DjangoTemplates",
)
def test_system_checks_report_missing_django_forms_and_renderer() -> None:
    messages = check_daisy_forms_configuration()

    ids = {message.id for message in messages}
    assert "daisy_forms.E001" in ids
    assert "daisy_forms.W001" in ids


@override_settings(
    INSTALLED_APPS=["django.forms", "daisy_forms"],
    FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer",
)
def test_system_checks_accept_valid_configuration() -> None:
    messages = check_daisy_forms_configuration()

    assert not [
        message
        for message in messages
        if message.id is not None and message.id.startswith("daisy_forms.")
    ]


def test_configuration_check_runs_with_the_templates_tag() -> None:
    assert "templates" in getattr(check_daisy_forms_configuration, "tags", ())


@override_settings(
    INSTALLED_APPS=["django.forms", "daisy_forms"],
    FORM_RENDERER="myapp.renderers.DaisyRendr",
)
def test_system_checks_report_unimportable_renderer_cause() -> None:
    messages = check_daisy_forms_configuration()

    warning = next(message for message in messages if message.id == "daisy_forms.W001")
    assert "could not be imported" in warning.msg
    assert "myapp.renderers.DaisyRendr" in warning.msg


@override_settings(
    INSTALLED_APPS=["django.forms", "daisy_forms"],
    FORM_RENDERER="django.forms.renderers.DjangoTemplates",
)
def test_system_checks_report_wrong_renderer_type() -> None:
    messages = check_daisy_forms_configuration()

    warning = next(message for message in messages if message.id == "daisy_forms.W001")
    assert warning.msg == "FORM_RENDERER is not DaisyFormRenderer or a subclass of it."
