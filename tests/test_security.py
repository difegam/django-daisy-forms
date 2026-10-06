from django import forms
from django.template import Context, Template
from django.test import override_settings


class UnsafeForm(forms.Form):
    name = forms.CharField(
        label='<script>alert("label")</script>',
        help_text='<img src=x onerror="alert(1)">',
    )

    def clean_name(self) -> None:
        raise forms.ValidationError('<script>alert("error")</script>')


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_form_content_is_escaped_by_default() -> None:
    form = UnsafeForm(data={"name": '<img src=x onerror="alert(2)">'})

    output = Template("{{ form }}").render(Context({"form": form}))

    assert "<script>" not in output
    assert 'onerror="alert(1)"' not in output
    assert "&lt;script&gt;" in output
    assert "&lt;img" in output


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_tag_attribute_values_are_escaped() -> None:
    form = forms.Form()
    form.fields["name"] = forms.CharField()

    output = Template(
        "{% load daisy_forms %}{% daisy_field form.name "
        'data-note="&quot;&gt;&lt;img src=x onerror=alert(1)&gt;" %}'
    ).render(Context({"form": form}))

    assert "<img src=x onerror=" not in output
