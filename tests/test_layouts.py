from django import forms
from django.template import Context, Template
from django.test import override_settings

from daisy_forms.checks import check_daisy_forms_configuration
from daisy_forms.renderers import DaisyHorizontalFormRenderer

GROUPED_CHOICES = [
    ("Monthly", [("basic", "Basic"), ("pro", "Pro")]),
    ("Yearly", [("team", "Team")]),
]


class GroupedForm(forms.Form):
    plan = forms.ChoiceField(choices=GROUPED_CHOICES, widget=forms.RadioSelect)
    features = forms.MultipleChoiceField(
        choices=GROUPED_CHOICES, widget=forms.CheckboxSelectMultiple, required=False
    )


class FlatForm(forms.Form):
    plan = forms.ChoiceField(
        choices=[("basic", "Basic"), ("pro", "Pro")], widget=forms.RadioSelect
    )


class ContactForm(forms.Form):
    email = forms.EmailField()


class HorizontalContactForm(ContactForm):
    default_renderer = DaisyHorizontalFormRenderer


def render(source: str, **context: object) -> str:
    return Template(source).render(Context(context))


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_radio_optgroups_are_labelled_groups() -> None:
    output = render("{{ form.plan }}", form=GroupedForm())

    assert (
        '<div role="group" aria-labelledby="id_plan_group_0" '
        'class="flex flex-col gap-2">'
        '<span id="id_plan_group_0" class="fieldset-legend text-sm w-full">'
        "Monthly</span>"
    ) in output
    assert 'aria-labelledby="id_plan_group_1"' in output
    assert output.count('role="group"') == 2


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_checkbox_optgroups_are_labelled_groups() -> None:
    output = render("{{ form.features }}", form=GroupedForm())

    assert 'aria-labelledby="id_features_group_0"' in output
    assert output.count('role="group"') == 2


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_inline_optgroups_wrap_their_options() -> None:
    output = render(
        '{% load daisy_forms %}{% daisy_field form.plan choices="inline" %}',
        form=GroupedForm(),
    )

    assert (
        '<div role="group" aria-labelledby="id_plan_group_0" '
        'class="flex flex-row flex-wrap gap-2">'
    ) in output


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_optgroups_without_ids_use_an_aria_label() -> None:
    output = render("{{ form.plan }}", form=GroupedForm(auto_id=False))

    assert '<div role="group" aria-label="Monthly"' in output
    assert "aria-labelledby" not in output


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_flat_choices_render_no_groups() -> None:
    output = render("{{ form.plan }}", form=FlatForm())

    assert 'role="group"' not in output


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyHorizontalFormRenderer")
def test_horizontal_renderer_applies_to_every_field() -> None:
    output = render("{{ form }}", form=ContactForm())

    assert "md:w-48" in output


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_horizontal_renderer_can_be_set_per_form() -> None:
    assert "md:w-48" in render("{{ form }}", form=HorizontalContactForm())
    assert "md:w-48" not in render("{{ form }}", form=ContactForm())


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyHorizontalFormRenderer")
def test_daisy_field_template_overrides_the_horizontal_renderer() -> None:
    output = render(
        "{% load daisy_forms %}"
        '{% daisy_field form.email template="daisy_forms/field.html" %}',
        form=ContactForm(),
    )

    assert "md:w-48" not in output


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyHorizontalFormRenderer")
def test_horizontal_renderer_passes_the_renderer_check() -> None:
    messages = check_daisy_forms_configuration()

    assert not [m for m in messages if m.id == "daisy_forms.W001"]
