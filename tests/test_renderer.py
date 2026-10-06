from django import forms
from django.template import Context, Template
from django.test import override_settings


class ContactForm(forms.Form):
    email = forms.EmailField(help_text="We never share it.")


class StyledForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "w-full custom"}))
    accepted = forms.BooleanField()


class ChoiceForm(forms.Form):
    plan = forms.ChoiceField(
        choices=[("basic", "Basic"), ("pro", "Pro")],
        widget=forms.RadioSelect,
        help_text="Change any time.",
    )
    features = forms.MultipleChoiceField(
        choices=[("a", "A"), ("b", "B")],
        widget=forms.CheckboxSelectMultiple,
    )


class CustomTemplateInput(forms.TextInput):
    template_name = "django/forms/widgets/textarea.html"


class CustomWidgetForm(forms.Form):
    value = forms.CharField(widget=CustomTemplateInput)


class FileForm(forms.Form):
    upload = forms.FileField(required=False)


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_plain_form_rendering_uses_daisy_field_markup() -> None:
    form = ContactForm(data={"email": "invalid"})

    output = Template("{{ form }}").render(Context({"form": form}))

    assert '<div class="fieldset">' in output
    assert '<label class="fieldset-legend" for="id_email">Email' in output
    assert 'class="input input-error w-full"' in output
    assert 'aria-invalid="true"' in output
    assert 'aria-describedby="id_email_helptext id_email_error"' in output
    assert '<p class="label" id="id_email_helptext">We never share it.</p>' in output
    assert '<ul class="text-error text-sm" id="id_email_error">' in output


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_renderer_merges_widget_classes_without_duplicates() -> None:
    form = StyledForm()

    output = Template("{{ form.email }}{{ form.accepted }}").render(
        Context({"form": form})
    )

    assert 'class="input w-full custom"' in output
    assert 'class="checkbox"' in output


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_choice_widgets_render_daisy_classes_and_fieldset_semantics() -> None:
    form = ChoiceForm(data={"plan": "", "features": []})

    output = Template("{{ form }}").render(Context({"form": form}))

    assert '<fieldset class="fieldset"' in output
    assert '<legend class="fieldset-legend">Plan' in output
    assert 'class="radio radio-error"' in output
    assert 'class="checkbox checkbox-error"' in output
    assert 'id="id_plan_helptext"' in output
    assert 'id="id_plan_error"' in output


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_checkbox_fields_put_control_and_label_in_one_label() -> None:
    form = StyledForm()

    output = Template("{{ form.accepted.as_field_group }}").render(
        Context({"form": form})
    )

    assert '<label class="label" for="id_accepted">' in output
    assert '<input type="checkbox"' in output
    assert "Accepted" in output


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_custom_widget_template_is_not_replaced_or_styled() -> None:
    form = CustomWidgetForm()

    output = Template("{{ form.value }}").render(Context({"form": form}))

    assert 'class="input' not in output


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_clearable_file_input_uses_daisy_file_classes() -> None:
    class InitialFile:
        url = "/uploads/report.pdf"

        def __str__(self) -> str:
            return "report.pdf"

    form = FileForm(initial={"upload": InitialFile()})

    output = Template("{{ form.upload.as_field_group }}").render(
        Context({"form": form})
    )

    assert 'class="file-input w-full"' in output
    assert 'href="/uploads/report.pdf"' in output
    assert 'class="checkbox"' in output
