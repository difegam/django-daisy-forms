from pathlib import Path

from django import forms
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

TAILWIND_OUTPUT = Path(__file__).parent.parent / "tailwind" / "output.css"


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
            "Run `just css-check` before opening the browser preview.",
            status=503,
            content_type="text/plain; charset=utf-8",
        )
    return HttpResponse(TAILWIND_OUTPUT.read_text(), content_type="text/css")
