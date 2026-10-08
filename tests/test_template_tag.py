import pytest
from django import forms
from django.template import Context, Template, TemplateSyntaxError
from django.test import override_settings


class TagForm(forms.Form):
    email = forms.EmailField()


class LayoutTagForm(forms.Form):
    email = forms.EmailField()
    plan = forms.ChoiceField(
        choices=[("basic", "Basic"), ("pro", "Pro")],
        widget=forms.RadioSelect,
    )
    features = forms.MultipleChoiceField(
        choices=[("reports", "Reports"), ("exports", "Exports")],
        widget=forms.CheckboxSelectMultiple,
    )
    price = forms.DecimalField()


class CustomTemplateRadio(forms.RadioSelect):
    option_template_name = "custom/radio_option.html"


class CustomTemplateInput(forms.TextInput):
    template_name = "custom/text_input.html"


class UnsupportedAddonForm(forms.Form):
    checkbox = forms.BooleanField(required=False)
    hidden = forms.CharField(widget=forms.HiddenInput)
    textarea = forms.CharField(widget=forms.Textarea)
    upload = forms.FileField(required=False)
    plan = forms.ChoiceField(choices=[("basic", "Basic")], widget=forms.RadioSelect)
    custom = forms.CharField(widget=CustomTemplateInput)


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


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_daisy_field_tag_renders_horizontal_field_layout() -> None:
    output = Template(
        "{% load daisy_forms %}{% daisy_field form.email "
        'template="daisy_forms/field_horizontal.html" %}'
    ).render(Context({"form": LayoutTagForm()}))

    assert "md:flex md:flex-row" in output
    assert '<label class="fieldset-legend md:w-48 md:shrink-0"' in output


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_daisy_field_tag_renders_inline_choices_without_mutating_widgets() -> None:
    form = LayoutTagForm()
    original_templates = {
        name: field.widget.template_name for name, field in form.fields.items()
    }

    output = Template(
        '{% load daisy_forms %}{% daisy_field form.plan choices="inline" %}'
        '{% daisy_field form.features choices="inline" %}'
    ).render(Context({"form": form}))

    assert output.count('class="flex flex-row flex-wrap gap-2"') == 2
    assert 'type="radio"' in output
    assert 'type="checkbox"' in output
    assert form.fields["plan"].widget.template_name == original_templates["plan"]
    assert (
        form.fields["features"].widget.template_name == original_templates["features"]
    )


@pytest.mark.parametrize("layout", ["stacked", "columns"])
@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_daisy_field_tag_rejects_unknown_choice_layout(layout: str) -> None:
    template = Template(
        f'{{% load daisy_forms %}}{{% daisy_field form.plan choices="{layout}" %}}'
    )

    with pytest.raises(TemplateSyntaxError, match="choices must be set"):
        template.render(Context({"form": LayoutTagForm()}))


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_daisy_field_tag_rejects_inline_choices_on_unsupported_widgets() -> None:
    template = Template(
        '{% load daisy_forms %}{% daisy_field form.email choices="inline" %}'
    )

    with pytest.raises(TemplateSyntaxError, match="stock RadioSelect"):
        template.render(Context({"form": LayoutTagForm()}))


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_daisy_field_tag_rejects_inline_custom_option_templates() -> None:
    class FormWithCustomRadio(forms.Form):
        plan = forms.ChoiceField(
            choices=[("basic", "Basic")], widget=CustomTemplateRadio
        )

    template = Template(
        '{% load daisy_forms %}{% daisy_field form.plan choices="inline" %}'
    )

    with pytest.raises(TemplateSyntaxError, match="stock RadioSelect"):
        template.render(Context({"form": FormWithCustomRadio()}))


@pytest.mark.parametrize(
    "field_name",
    ["checkbox", "hidden", "textarea", "upload", "plan", "custom"],
)
@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_daisy_field_tag_rejects_addons_for_unsupported_widgets(
    field_name: str,
) -> None:
    template = Template(
        f'{{% load daisy_forms %}}{{% daisy_field form.{field_name} prefix="$" %}}'
    )

    with pytest.raises(TemplateSyntaxError, match="require a stock widget"):
        template.render(Context({"form": UnsupportedAddonForm()}))


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_daisy_field_tag_rejects_non_input_type_override_for_addons() -> None:
    template = Template(
        '{% load daisy_forms %}{% daisy_field form.email prefix="$" type="range" %}'
    )

    with pytest.raises(TemplateSyntaxError, match="require a stock widget"):
        template.render(Context({"form": LayoutTagForm()}))


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_daisy_field_tag_renders_escaped_prefix_and_suffix_addons() -> None:
    output = Template(
        "{% load daisy_forms %}{% daisy_field form.price prefix=prefix suffix=suffix %}"
    ).render(
        Context(
            {
                "form": LayoutTagForm(),
                "prefix": "<strong>$</strong>",
                "suffix": "USD",
            }
        )
    )

    assert '<div class="join w-full">' in output
    assert (
        '<span class="input join-item w-auto">&lt;strong&gt;$&lt;/strong&gt;</span>'
        in output
    )
    assert '<span class="input join-item w-auto">USD</span>' in output
    assert 'class="input join-item flex-1"' in output
    assert "<strong>" not in output


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_daisy_field_tag_addons_mirror_input_error_state() -> None:
    form = LayoutTagForm(data={"price": "not-a-number"})
    form.is_valid()

    output = Template(
        '{% load daisy_forms %}{% daisy_field form.price prefix="$" suffix="USD" %}'
    ).render(Context({"form": form}))

    assert '<span class="input input-error join-item w-auto">$</span>' in output
    assert '<span class="input input-error join-item w-auto">USD</span>' in output
    assert 'class="input input-error join-item flex-1"' in output
    assert 'aria-invalid="true"' in output


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_daisy_field_tag_addons_mirror_size_and_color_modifiers() -> None:
    output = Template(
        '{% load daisy_forms %}{% daisy_field form.price prefix="$" suffix="USD" '
        'class+="input-sm input-primary rounded-none" hx-post="/price/" %}'
    ).render(Context({"form": LayoutTagForm()}))

    assert (
        '<span class="input input-sm input-primary join-item w-auto">$</span>' in output
    )
    assert (
        '<span class="input input-sm input-primary join-item w-auto">USD</span>'
        in output
    )
    assert output.count("rounded-none") == 1
    assert output.count('hx-post="/price/"') == 1


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


class LabelClassForm(forms.Form):
    email = forms.EmailField()
    agree = forms.BooleanField()
    plan = forms.ChoiceField(
        choices=[("basic", "Basic"), ("pro", "Pro")],
        widget=forms.RadioSelect,
    )


@pytest.mark.parametrize(
    ("field_name", "template_name", "expected"),
    [
        ("email", "", '<label class="fieldset-legend font-semibold" for="id_email">'),
        (
            "email",
            "daisy_forms/field_horizontal.html",
            '<label class="fieldset-legend md:w-48 md:shrink-0 font-semibold" '
            'for="id_email">',
        ),
        ("agree", "", '<label class="label font-semibold" for="id_agree">'),
        (
            "agree",
            "daisy_forms/field_horizontal.html",
            '<label class="label md:w-48 md:shrink-0 font-semibold" for="id_agree">',
        ),
        ("plan", "", '<legend class="fieldset-legend font-semibold">'),
        (
            "plan",
            "daisy_forms/field_horizontal.html",
            '<legend class="fieldset-legend md:w-48 md:shrink-0 font-semibold">',
        ),
    ],
    ids=[
        "label",
        "horizontal-label",
        "checkbox",
        "horizontal-checkbox",
        "legend",
        "horizontal-legend",
    ],
)
@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_daisy_field_tag_appends_label_class(
    field_name: str, template_name: str, expected: str
) -> None:
    template_option = f' template="{template_name}"' if template_name else ""
    output = Template(
        f"{{% load daisy_forms %}}{{% daisy_field form.{field_name} "
        f'label_class="font-semibold"{template_option} %}}'
    ).render(Context({"form": LabelClassForm()}))

    assert expected in output
    assert "label_class" not in output


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_daisy_field_tag_escapes_label_class() -> None:
    output = Template(
        "{% load daisy_forms %}{% daisy_field form.email label_class=extra %}"
    ).render(Context({"form": LabelClassForm(), "extra": '"><script>'}))

    assert "<script>" not in output
    assert "&quot;&gt;&lt;script&gt;" in output


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_daisy_field_tag_without_label_class_keeps_default_label() -> None:
    form = LabelClassForm()
    output = Template("{% load daisy_forms %}{% daisy_field form.email %}").render(
        Context({"form": form})
    )

    assert '<label class="fieldset-legend" for="id_email">' in output
    assert output == str(form["email"].as_field_group())
