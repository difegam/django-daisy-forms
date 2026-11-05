import pytest
from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.template import Context, Template


class PricingForm(forms.Form):
    email = forms.EmailField()
    price = forms.DecimalField()
    plan = forms.ChoiceField(
        choices=[("basic", "Basic"), ("pro", "Pro")], widget=forms.RadioSelect
    )

    daisy_fields = {  # noqa: RUF012
        "email": {"class": "input-sm", "hx-post": "/validate/", "label": "Work email"},
        "price": {"prefix": "$", "suffix": "USD"},
        "plan": {"choices": "inline", "label_class": "font-semibold"},
    }


class PlainForm(forms.Form):
    email = forms.EmailField()


def render(source: str, form: forms.Form) -> str:
    return Template(source).render(Context({"form": form}))


def make_form(daisy_fields: object) -> forms.Form:
    form = PlainForm()
    setattr(form, "daisy_fields", daisy_fields)  # noqa: B010
    return form


def test_declared_options_apply_to_plain_form_rendering() -> None:
    output = render("{{ form }}", PricingForm())

    assert 'hx-post="/validate/"' in output
    assert "input-sm" in output
    assert "Work email" in output
    assert '<div class="join w-full">' in output
    assert "flex flex-row flex-wrap gap-2" in output
    assert "fieldset-legend font-semibold" in output


def test_daisy_field_tag_merges_with_declared_options() -> None:
    output = render(
        '{% load daisy_forms %}{% daisy_field form.email class+="input-primary" %}',
        PricingForm(),
    )

    assert 'class="input input-sm input-primary w-full"' in output
    assert 'hx-post="/validate/"' in output


@pytest.mark.parametrize(
    ("daisy_fields", "message"),
    [
        ({"missing": {}}, "unknown fields: missing"),
        ({"email": {"onclick": "x()"}}, "not allowed: onclick"),
        ({"email": {"aria-invalid": "true"}}, "not allowed: aria-invalid"),
        ({"email": "input-sm"}, "must be a mapping"),
        (["email"], "must be a mapping"),
    ],
    ids=["unknown-field", "handler", "managed-aria", "options-type", "dict-type"],
)
def test_invalid_daisy_fields_raise(daisy_fields: object, message: str) -> None:
    with pytest.raises(ImproperlyConfigured, match=message):
        render("{{ form }}", make_form(daisy_fields))
