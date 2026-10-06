import pytest
from django import forms
from django.template import Context, Template, TemplateSyntaxError
from django.test import override_settings


class TagForm(forms.Form):
    email = forms.EmailField()


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_daisy_field_tag_adds_attributes_without_mutating_form() -> None:
    form = TagForm()
    original_attrs = dict(form.fields["email"].widget.attrs)

    output = Template(
        '{% load daisy_forms %}{% daisy_field form.email class+="input-sm" '
        'hx-post="/validate/email/" label="Work email" %}'
    ).render(Context({"form": form}))

    assert 'class="input input-sm w-full"' in output
    assert 'hx-post="/validate/email/"' in output
    assert "Work email" in output
    assert form.fields["email"].widget.attrs == original_attrs


@pytest.mark.parametrize(
    "attribute",
    [
        "onclick",
        "onfocus",
        "aria-invalid",
        "aria-describedby",
        "ARIA-DESCRIBEDBY",
        "Aria-Invalid",
        "hx-on:click",
        "hx-on::after-request",
        "x-on:click",
        "x-init",
        "data-hx-on:click",
    ],
)
def test_daisy_field_tag_rejects_unsafe_or_authoritative_attributes(
    attribute: str,
) -> None:
    with pytest.raises(TemplateSyntaxError):
        Template(
            "{% load daisy_forms %}{% daisy_field form.email "
            f'{attribute}="value" %}}'
        )


@pytest.mark.parametrize("attribute", ["hx-post", "hx-trigger", "x-data", "data-id"])
@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_daisy_field_tag_accepts_safe_passthrough_attributes(attribute: str) -> None:
    output = Template(
        f'{{% load daisy_forms %}}{{% daisy_field form.email {attribute}="v" %}}'
    ).render(Context({"form": TagForm()}))

    assert f'{attribute}="v"' in output


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_daisy_field_tag_reports_unresolved_field_as_value_error() -> None:
    template = Template("{% load daisy_forms %}{% daisy_field form.emial %}")

    with pytest.raises(ValueError, match="bound field"):
        template.render(Context({"form": TagForm()}))


class OptOutForm(forms.Form):
    plain = forms.CharField()
    plain.bound_field_class = forms.BoundField


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_daisy_field_tag_explains_opt_out_fields_are_unsupported() -> None:
    template = Template("{% load daisy_forms %}{% daisy_field form.plain %}")

    with pytest.raises(TemplateSyntaxError, match="opts out"):
        template.render(Context({"form": OptOutForm()}))
