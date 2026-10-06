"""Bound-field behavior for daisyUI controls."""

from __future__ import annotations

import copy
from typing import Any, cast

from django.forms.boundfield import BoundField
from django.forms.widgets import Widget
from django.utils.safestring import SafeString

from .classes import WIDGET_CLASSES, daisy_class_for


def _uses_stock_template(widget: Widget) -> bool:
    template_name = widget.template_name or ""
    if template_name.startswith("daisy_forms/"):
        return True
    if type(widget).__module__ == "django.forms.widgets":
        return True
    for widget_type in type(widget).__mro__:
        if widget_type in WIDGET_CLASSES:
            return template_name == getattr(widget_type, "template_name", None)
    return False


class DaisyBoundField(BoundField):
    """A Django bound field that adds daisyUI classes without mutating widgets."""

    extra_attrs: dict[str, str]
    template_override: str | None
    label_override: str | None

    @property
    def template_name(self) -> str:
        template_override = getattr(self, "template_override", None)
        if isinstance(template_override, str):
            return template_override
        return super().template_name

    def build_widget_attrs(
        self, attrs: dict[str, str | bool], widget: Widget | None = None
    ) -> dict[str, str | bool]:
        widget = widget or self.field.widget
        built = super().build_widget_attrs(attrs, widget)
        if not _uses_stock_template(widget):
            return built
        base_class = daisy_class_for(widget, str(built.get("type") or "") or None)
        if base_class is None or widget.is_hidden:
            return built

        classes: list[str] = []
        for token in (
            base_class,
            f"{base_class}-error" if self.errors else None,
            *(str(widget.attrs.get("class", "")).split()),
            *(str(built.get("class", "")).split()),
        ):
            if token and token not in classes:
                classes.append(token)
        if (
            base_class in {"input", "textarea", "select", "file-input"}
            and "w-full" not in classes
        ):
            classes.append("w-full")
        built["class"] = " ".join(classes)
        return built

    def as_widget(
        self,
        widget: Widget | None = None,
        attrs: dict[str, str | bool] | None = None,
        only_initial: bool = False,
    ) -> SafeString:
        widget = copy.copy(widget or self.field.widget)
        if widget.template_name == "django/forms/widgets/radio.html":
            widget.template_name = "daisy_forms/widgets/radio.html"
            widget_any = cast(Any, widget)
            widget_any.option_template_name = "daisy_forms/widgets/radio_option.html"
        elif widget.template_name == "django/forms/widgets/checkbox_select.html":
            widget.template_name = "daisy_forms/widgets/checkbox_select.html"
            widget_any = cast(Any, widget)
            widget_any.option_template_name = "daisy_forms/widgets/checkbox_option.html"
        elif widget.template_name == "django/forms/widgets/clearable_file_input.html":
            widget.template_name = "daisy_forms/widgets/clearable_file_input.html"
        merged_attrs = cast(dict[str, str | bool], dict(attrs or {}))
        for key, value in getattr(self, "extra_attrs", {}).items():
            if key == "class" and merged_attrs.get("class"):
                merged_attrs["class"] = f"{merged_attrs['class']} {value}"
            else:
                merged_attrs[key] = value
        return super().as_widget(widget, merged_attrs, only_initial)
