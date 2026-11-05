from __future__ import annotations

import re
from typing import Any

import pytest
from django import forms
from django.contrib.auth.models import User
from django.forms import BaseFormSet, formset_factory

from daisy_forms.renderers import DaisyFormRenderer

TABLE = "daisy_forms/formset_table.html"
DYNAMIC = "daisy_forms/formset_dynamic.html"


class ItemForm(forms.Form):
    name = forms.CharField(help_text="Shown on the invoice.")
    size = forms.ChoiceField(
        choices=[("s", "Small"), ("l", "Large")], widget=forms.RadioSelect
    )
    note = forms.CharField(widget=forms.HiddenInput, required=False)

    def clean(self) -> dict[str, Any]:
        cleaned = super().clean() or {}
        if cleaned.get("name") == "bad":
            raise forms.ValidationError("Row is invalid.")
        return cleaned


class HiddenInitialForm(forms.Form):
    name = forms.CharField(show_hidden_initial=True)


class HiddenInitialOptionsForm(forms.Form):
    amount = forms.DecimalField(show_hidden_initial=True)
    plan = forms.ChoiceField(
        choices=[("basic", "Basic"), ("pro", "Pro")],
        show_hidden_initial=True,
        widget=forms.RadioSelect,
    )

    daisy_fields = {  # noqa: RUF012
        "amount": {"prefix": "$"},
        "plan": {"choices": "inline"},
    }


class HiddenOnlyForm(forms.Form):
    token = forms.CharField(widget=forms.HiddenInput)


def make_formset(
    *,
    data: dict[str, str] | None = None,
    extra: int = 1,
    can_delete: bool = False,
    can_delete_extra: bool = True,
) -> BaseFormSet[ItemForm]:
    formset_class = formset_factory(
        ItemForm, extra=extra, can_delete=can_delete, can_delete_extra=can_delete_extra
    )
    return formset_class(data, prefix="items")


def row_data(**rows: str) -> dict[str, str]:
    data = {
        "items-TOTAL_FORMS": "1",
        "items-INITIAL_FORMS": "0",
        "items-MIN_NUM_FORMS": "0",
        "items-MAX_NUM_FORMS": "1000",
    }
    data.update({f"items-0-{key}": value for key, value in rows.items()})
    return data


@pytest.mark.parametrize("template_name", [TABLE, DYNAMIC], ids=["table", "dynamic"])
def test_templates_wrap_the_formset_for_the_script(template_name: str) -> None:
    output = make_formset(can_delete=True).render(template_name)

    assert '<div data-daisy-formset data-prefix="items"' in output
    assert 'name="items-TOTAL_FORMS"' in output
    assert "<template data-daisy-formset-template>" in output
    assert 'name="items-__prefix__-name"' in output
    assert 'role="status" aria-live="polite"' in output
    assert re.search(r"<button [^>]*data-daisy-formset-add hidden>", output)
    assert re.search(r"<button [^>]*data-daisy-formset-remove hidden>", output)


@pytest.mark.parametrize("template_name", [TABLE, DYNAMIC], ids=["table", "dynamic"])
def test_delete_checkbox_stays_visible_without_javascript(template_name: str) -> None:
    output = make_formset(can_delete=True).render(template_name)

    assert 'name="items-0-DELETE"' in output


def test_add_button_names_the_model_when_there_is_one() -> None:
    formset = make_formset()
    formset.model = User  # type: ignore[attr-defined]

    assert "Add user</button>" in formset.render(DYNAMIC)
    assert "Add another</button>" in make_formset().render(DYNAMIC)


def test_table_headers_label_their_column_cells() -> None:
    output = make_formset(can_delete=True).render(TABLE)

    assert '<th scope="col" id="items-name-label">Name' in output
    assert 'aria-labelledby="items-name-label"' in output
    assert '<div role="group" aria-labelledby="items-size-label"' in output
    assert '<span class="label block font-normal">Shown on the invoice.</span>' in (
        output
    )
    assert '<span class="sr-only" id="id_items-0-name_helptext">' in output


def test_table_renders_hidden_initial_widgets() -> None:
    formset_class = formset_factory(HiddenInitialForm, extra=1)
    output = formset_class(prefix="items", initial=[{"name": "Alice"}]).render(TABLE)

    assert 'name="items-0-name"' in output
    assert 'name="initial-items-0-name"' in output
    assert 'value="Alice"' in output


def test_table_renders_hidden_initial_widgets_with_visible_options() -> None:
    formset_class = formset_factory(HiddenInitialOptionsForm, extra=1)
    output = formset_class(
        prefix="items", initial=[{"amount": "12.50", "plan": "pro"}]
    ).render(TABLE)

    assert 'name="initial-items-0-amount"' in output
    assert 'name="initial-items-0-plan"' in output
    assert 'value="12.50"' in output
    assert 'value="pro"' in output


def test_table_renders_hidden_fields_without_visible_data_columns() -> None:
    formset_class = formset_factory(HiddenOnlyForm, extra=1, can_delete=True)
    output = formset_class(prefix="hidden", initial=[{"token": "secret"}]).render(TABLE)

    assert output.count('name="hidden-0-token"') == 1
    assert 'value="secret"' in output
    assert 'name="hidden-0-DELETE"' in output


def test_table_keeps_an_action_column_without_can_delete() -> None:
    output = make_formset(can_delete=True, can_delete_extra=False).render(TABLE)
    header = output[output.index("<thead>") : output.index("</thead>")]
    row = output[output.index("<tbody") : output.index("</tbody>")]

    assert header.count("<th ") == 3
    assert row.count("<td") == 3


def test_table_renders_cell_and_row_errors() -> None:
    formset = make_formset(data=row_data(name="bad", size="s"))
    formset.is_valid()
    output = formset.render(TABLE)

    assert '<td colspan="3"><div role="alert"' in output
    assert "<li>Row is invalid.</li>" in output

    formset = make_formset(data=row_data(name="", size="s"))
    formset.is_valid()
    output = formset.render(TABLE)

    assert '<ul class="text-error text-sm" id="id_items-0-name_error">' in output
    assert 'aria-invalid="true"' in output


def test_dynamic_template_renders_each_form_in_a_card() -> None:
    output = make_formset(extra=2).render(DYNAMIC)

    assert output.count('<div class="card card-border bg-base-100"') == 3
    assert output.count("data-daisy-formset-body") == 3


class TableRenderer(DaisyFormRenderer):
    formset_template_name = TABLE


def test_templates_can_be_set_through_a_renderer() -> None:
    formset_class = formset_factory(ItemForm, renderer=TableRenderer())

    assert "<table" in str(formset_class(prefix="items"))
