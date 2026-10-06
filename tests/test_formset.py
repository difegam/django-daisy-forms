from django import forms
from django.forms import formset_factory
from django.template import Context, Template
from django.test import override_settings


class RowForm(forms.Form):
    value = forms.CharField()


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_formset_keeps_management_form_and_prefixed_ids() -> None:
    formset = formset_factory(RowForm, extra=2)(prefix="rows")

    output = Template("{{ formset }}").render(Context({"formset": formset}))

    assert 'name="rows-TOTAL_FORMS"' in output
    assert 'id="id_rows-0-value"' in output
    assert 'id="id_rows-1-value"' in output
