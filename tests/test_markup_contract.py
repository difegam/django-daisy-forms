from pathlib import Path

from django import forms
from django.template import Context, Template
from django.test import SimpleTestCase, override_settings

GOLDEN_DIR = Path(__file__).parent / "golden"


class ScalarContractForm(forms.Form):
    email = forms.EmailField(help_text="We never share it.")


class GroupContractForm(forms.Form):
    plan = forms.ChoiceField(
        choices=[("basic", "Basic")],
        widget=forms.RadioSelect,
        help_text="Change any time.",
    )


class CheckboxContractForm(forms.Form):
    terms = forms.BooleanField(help_text="Required to continue.")


class FileContractForm(forms.Form):
    upload = forms.FileField(required=False)


class InitialFile:
    url = "/uploads/report.pdf"

    def __str__(self) -> str:
        return "report.pdf"


def assert_matches_golden(actual: str, name: str) -> None:
    expected = (GOLDEN_DIR / name).read_text()

    SimpleTestCase().assertHTMLEqual(actual, expected)


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_invalid_scalar_field_matches_the_markup_contract() -> None:
    output = Template("{{ form.email.as_field_group }}").render(
        Context({"form": ScalarContractForm(data={"email": "invalid"})})
    )

    assert_matches_golden(output, "invalid_scalar.html")


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_invalid_grouped_field_matches_the_markup_contract() -> None:
    output = Template("{{ form.plan.as_field_group }}").render(
        Context({"form": GroupContractForm(data={"plan": ""})})
    )

    assert_matches_golden(output, "invalid_grouped.html")


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_checkbox_field_matches_the_markup_contract() -> None:
    output = Template("{{ form.terms.as_field_group }}").render(
        Context({"form": CheckboxContractForm()})
    )

    assert_matches_golden(output, "checkbox.html")


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_clearable_file_field_matches_the_markup_contract() -> None:
    output = Template("{{ form.upload.as_field_group }}").render(
        Context({"form": FileContractForm(initial={"upload": InitialFile()})})
    )

    assert_matches_golden(output, "clearable_file.html")
