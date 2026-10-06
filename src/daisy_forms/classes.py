"""The daisyUI classes used by the package's renderer."""

from collections.abc import Mapping
from typing import Final

from django.forms.widgets import (
    CheckboxInput,
    CheckboxSelectMultiple,
    DateInput,
    DateTimeInput,
    FileInput,
    HiddenInput,
    Input,
    RadioSelect,
    Select,
    Textarea,
    TimeInput,
    Widget,
)

from .widgets import Toggle

WIDGET_CLASSES: Final[Mapping[type[Widget], str | None]] = {
    HiddenInput: None,
    Textarea: "textarea",
    Select: "select",
    CheckboxInput: "checkbox",
    Toggle: "toggle",
    CheckboxSelectMultiple: "checkbox",
    RadioSelect: "radio",
    DateInput: "input",
    DateTimeInput: "input",
    TimeInput: "input",
    FileInput: "file-input",
    Input: "input",
}

LAYOUT_CLASSES: Final[frozenset[str]] = frozenset(
    {
        "fieldset",
        "fieldset-legend",
        "label",
        "text-error",
        "text-sm",
        "w-full",
        "flex",
        "flex-col",
        "gap-2",
        "alert",
        "alert-error",
        "alert-soft",
    }
)


def daisy_class_for(widget: Widget) -> str | None:
    """Return the first registered class for a widget's method-resolution order."""

    for widget_type in type(widget).__mro__:
        if widget_type in WIDGET_CLASSES:
            return WIDGET_CLASSES[widget_type]
    return None


def all_classes() -> frozenset[str]:
    """Return every class emitted by the package templates and renderer."""

    classes = set(LAYOUT_CLASSES)
    for base_class in WIDGET_CLASSES.values():
        if base_class:
            classes.add(base_class)
            classes.add(f"{base_class}-error")
    classes.update({"radio", "radio-error", "checkbox-error", "toggle-error"})
    return frozenset(classes)
