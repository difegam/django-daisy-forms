from datetime import date, datetime, time

from django import forms
from django.template import Context, Template
from django.test import override_settings

from daisy_forms.widgets import (
    NativeDateInput,
    NativeDateTimeInput,
    NativeTimeInput,
    Toggle,
)


class WidgetForm(forms.Form):
    enabled = forms.BooleanField(widget=Toggle)
    day = forms.DateField(widget=NativeDateInput)
    moment = forms.DateTimeField(widget=NativeDateTimeInput)
    at = forms.TimeField(widget=NativeTimeInput)


@override_settings(FORM_RENDERER="daisy_forms.renderers.DaisyFormRenderer")
def test_package_widgets_render_native_types_and_daisy_classes() -> None:
    form = WidgetForm(
        initial={
            "enabled": True,
            "day": date(2026, 10, 6),
            "moment": datetime(2026, 10, 6, 14, 30),
            "at": time(14, 30),
        }
    )

    output = Template("{{ form }}").render(Context({"form": form}))

    assert 'class="toggle"' in output
    assert 'type="date"' in output
    assert 'type="datetime-local"' in output
    assert 'type="time"' in output


def test_native_widgets_define_explicit_formats() -> None:
    assert NativeDateInput().format == "%Y-%m-%d"
    assert NativeDateTimeInput().format == "%Y-%m-%dT%H:%M"
    assert NativeTimeInput().format == "%H:%M"
