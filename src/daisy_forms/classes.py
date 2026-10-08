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
        "flex-row",
        "flex-wrap",
        "flex-1",
        "min-w-0",
        "gap-2",
        "join",
        "join-item",
        "w-auto",
        "md:flex-row",
        "md:flex",
        "md:items-start",
        "md:gap-6",
        "md:w-48",
        "md:shrink-0",
        "alert",
        "alert-error",
        "alert-soft",
    }
)


INPUT_TYPE_CLASSES: Final[Mapping[str, str | None]] = {
    "range": "range",
    "color": None,
}


def daisy_class_for(widget: Widget, input_type: str | None = None) -> str | None:
    """Return the first registered class for a widget's method-resolution order.

    daisyUI styles some input types with their own component class, so the
    effective ``type`` (the rendered attribute, then the widget's) wins first.
    """

    effective_type = (
        input_type or widget.attrs.get("type") or getattr(widget, "input_type", None)
    )
    if (
        isinstance(widget, Input)
        and effective_type is not None
        and effective_type in INPUT_TYPE_CLASSES
    ):
        return INPUT_TYPE_CLASSES[effective_type]
    for widget_type in type(widget).__mro__:
        if widget_type in WIDGET_CLASSES:
            return WIDGET_CLASSES[widget_type]
    return None


def all_classes() -> frozenset[str]:
    """Return every class emitted by the package templates and renderer."""

    classes = set(LAYOUT_CLASSES)
    for base_class in (*WIDGET_CLASSES.values(), *INPUT_TYPE_CLASSES.values()):
        if base_class:
            classes.update((base_class, f"{base_class}-error"))
    return frozenset(classes)
