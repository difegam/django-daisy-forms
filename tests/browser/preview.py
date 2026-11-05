from pathlib import Path

from django import forms
from django.forms import formset_factory
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

TAILWIND_OUTPUT = Path(__file__).parent.parent / "tailwind" / "preview-output.css"
FORMSET_JS = (
    Path(__file__).parents[2] / "src/daisy_forms/static/daisy_forms/js/formset.js"
)


class FormPreview(forms.Form):
    email = forms.EmailField(help_text="Used for account notifications.")
    plan = forms.ChoiceField(
        choices=[
            ("starter", "Starter"),
            ("team", "Team"),
            ("enterprise", "Enterprise"),
        ],
        widget=forms.RadioSelect,
    )
    features = forms.MultipleChoiceField(
        choices=[("reports", "Reports"), ("exports", "Exports"), ("api", "API")],
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    price = forms.DecimalField(help_text="Billed monthly.")


def preview_form(request: HttpRequest) -> HttpResponse:
    form = FormPreview(request.POST if request.method == "POST" else None)
    if request.method == "POST":
        form.is_valid()
    return render(request, "browser/form_preview.html", {"form": form})


def preview_css(request: HttpRequest) -> HttpResponse:
    if not TAILWIND_OUTPUT.is_file():
        return HttpResponse(
            "Run `just css-preview` before opening the browser preview.",
            status=503,
            content_type="text/plain; charset=utf-8",
        )
    return HttpResponse(TAILWIND_OUTPUT.read_text(), content_type="text/css")


class ItemForm(forms.Form):
    name = forms.CharField()
    quantity = forms.IntegerField(min_value=1)


SavedItemFormSet = formset_factory(ItemForm, extra=0, can_delete=True)
LineFormSet = formset_factory(
    ItemForm, extra=1, min_num=1, max_num=3, validate_min=True, validate_max=True
)


def preview_formset(request: HttpRequest) -> HttpResponse:
    data = request.POST if request.method == "POST" else None
    saved = SavedItemFormSet(
        data,
        prefix="saved",
        initial=[{"name": "Apples", "quantity": 2}, {"name": "Pears", "quantity": 1}],
    )
    lines = LineFormSet(data, prefix="lines")
    if data is not None:
        saved.is_valid()
        lines.is_valid()
    return render(
        request,
        "browser/formset_preview.html",
        {
            "saved": saved,
            "lines": lines,
            "fragment": LineFormSet(prefix="swapped"),
            "nojs": "nojs" in request.GET,
        },
    )


def preview_formset_js(request: HttpRequest) -> HttpResponse:
    return HttpResponse(FORMSET_JS.read_text(), content_type="text/javascript")
