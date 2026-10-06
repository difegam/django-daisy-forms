"""Optional native widgets used by daisyUI forms."""

from typing import Any

from django.forms.widgets import CheckboxInput, DateInput, DateTimeInput, TimeInput


class Toggle(CheckboxInput):
    """A checkbox rendered with daisyUI's toggle component class."""


class NativeDateInput(DateInput):
    input_type = "date"
    format = "%Y-%m-%d"

    def __init__(
        self, attrs: dict[str, Any] | None = None, format: str | None = None
    ) -> None:
        super().__init__(attrs=attrs, format=format or self.format)


class NativeTimeInput(TimeInput):
    input_type = "time"
    format = "%H:%M"

    def __init__(
        self, attrs: dict[str, Any] | None = None, format: str | None = None
    ) -> None:
        super().__init__(attrs=attrs, format=format or self.format)


class NativeDateTimeInput(DateTimeInput):
    input_type = "datetime-local"
    format = "%Y-%m-%dT%H:%M"

    def __init__(
        self, attrs: dict[str, Any] | None = None, format: str | None = None
    ) -> None:
        super().__init__(attrs=attrs, format=format or self.format)
