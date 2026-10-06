"""Optional native widgets used by daisyUI forms."""

from typing import Any

from django.forms.widgets import (
    CheckboxInput,
    DateInput,
    DateTimeBaseInput,
    DateTimeInput,
    TimeInput,
)


class Toggle(CheckboxInput):
    """A checkbox rendered with daisyUI's toggle component class."""


class _NativeFormatInput(DateTimeBaseInput):
    default_format: str

    def __init__(
        self, attrs: dict[str, Any] | None = None, format: str | None = None
    ) -> None:
        super().__init__(attrs=attrs, format=format or self.default_format)


class NativeDateInput(_NativeFormatInput, DateInput):
    input_type = "date"
    default_format = "%Y-%m-%d"


class NativeTimeInput(_NativeFormatInput, TimeInput):
    input_type = "time"
    default_format = "%H:%M"


class NativeDateTimeInput(_NativeFormatInput, DateTimeInput):
    input_type = "datetime-local"
    default_format = "%Y-%m-%dT%H:%M"
