import pytest
from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.template import Context, Template
from django.utils.safestring import mark_safe

from daisy_forms.classes import all_classes
from daisy_forms.layout import GRID_CLASSES
from daisy_forms.renderers import DaisyHorizontalFormRenderer


class PlainSignupForm(forms.Form):
    email = forms.EmailField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    plan = forms.ChoiceField(
        choices=[("basic", "Basic"), ("pro", "Pro")], widget=forms.RadioSelect
    )
    notes = forms.CharField(required=False)
    token = forms.CharField(widget=forms.HiddenInput, required=False)


class SignupForm(PlainSignupForm):
    fieldsets = (
        (
            "Account",
            {
                "fields": ["email", ("first_name", "last_name")],
                "description": "Used for <login>.",
            },
        ),
        ("Preferences", {"fields": ["plan"], "classes": ["collapse", "bg-base-100"]}),
    )


class HorizontalSignupForm(SignupForm):
    default_renderer = DaisyHorizontalFormRenderer


def render_form(form: forms.Form) -> str:
    return Template("{{ form }}").render(Context({"form": form}))


def make_form(fieldsets: object) -> forms.Form:
    form = PlainSignupForm()
    setattr(form, "fieldsets", fieldsets)  # noqa: B010
    return form


def test_titled_fieldset_renders_a_legend_and_escaped_description() -> None:
    output = render_form(SignupForm())

    assert '<fieldset class="fieldset">\n<legend class="fieldset-legend">Account' in (
        output
    )
    assert '<p class="label">Used for &lt;login&gt;.</p>' in output


def test_safe_description_is_not_escaped() -> None:
    output = render_form(
        make_form(
            [("Account", {"fields": ["email"], "description": mark_safe("<b>B</b>")})]
        )
    )

    assert "<b>B</b>" in output


def test_untitled_declared_fieldset_keeps_metadata_without_empty_legend() -> None:
    output = render_form(
        make_form(
            [
                (
                    None,
                    {
                        "fields": ["email"],
                        "description": "Used to sign in.",
                        "classes": ["bg-base-100"],
                    },
                )
            ]
        )
    )

    assert '<fieldset class="fieldset bg-base-100">' in output
    assert '<p class="label">Used to sign in.</p>' in output
    assert '<legend class="fieldset-legend"></legend>' not in output


def test_tuple_renders_a_grid_row() -> None:
    output = render_form(SignupForm())

    grid = output.index('<div class="grid gap-4 md:grid-cols-2">')
    assert grid < output.index('id="id_first_name"') < output.index('id="id_last_name"')


def test_collapse_renders_details_with_extra_classes() -> None:
    output = render_form(SignupForm())

    assert (
        '<details class="collapse collapse-arrow border border-base-300 bg-base-100">'
    ) in output
    assert '<summary class="collapse-title font-semibold">Preferences</summary>' in (
        output
    )


def test_collapse_opens_when_a_field_has_errors() -> None:
    output = render_form(SignupForm(data={"email": "a@example.com"}))

    assert 'bg-base-100" open>' in output


def test_unlisted_fields_render_after_the_fieldsets_without_a_wrapper() -> None:
    output = render_form(SignupForm())

    assert output.index("</details>") < output.index('id="id_notes"')
    assert output.count("<fieldset") == 2  # Account plus the plan radio group


def test_hidden_fields_render_once() -> None:
    output = render_form(make_form([("A", {"fields": ["email", "token"]})]))

    assert output.count('name="token"') == 1


def test_row_fields_stay_stacked_in_horizontal_mode() -> None:
    output = render_form(HorizontalSignupForm())
    row = output[output.index("md:grid-cols-2") : output.index('id="id_last_name"')]

    assert "md:w-48" not in row
    assert "md:w-48" in output[: output.index("md:grid-cols-2")]


@pytest.mark.parametrize(
    ("fieldsets", "message"),
    [
        ([("A", {"fields": ["missing"]})], "unknown field: 'missing'"),
        ([("A", {"fields": ["email", "email"]})], "more than once"),
        ([("A",)], r"\(title, options\) pairs"),
        ([("A", {"rows": []})], "mapping with 'fields'"),
        (
            [
                (
                    "A",
                    {"fields": [("email", "first_name", "last_name", "plan", "notes")]},
                )
            ],
            "at most 4",
        ),
    ],
    ids=["unknown", "duplicate", "shape", "no-fields", "row-too-wide"],
)
def test_invalid_fieldsets_raise(fieldsets: object, message: str) -> None:
    with pytest.raises(ImproperlyConfigured, match=message):
        render_form(make_form(fieldsets))


def test_grid_classes_are_in_the_safelist() -> None:
    classes = {name for value in GRID_CLASSES.values() for name in value.split()}

    assert classes <= all_classes()
