"""Bound-field behavior for daisyUI controls."""

from __future__ import annotations

import copy
from collections.abc import Mapping
from types import MappingProxyType
from typing import Any, Final, cast

from django.forms.boundfield import BoundField
from django.forms.widgets import Widget
from django.template import TemplateDoesNotExist
from django.utils.safestring import SafeString

from .classes import WIDGET_CLASSES, daisy_class_for

_SIZED_CLASSES: Final = frozenset({"input", "textarea", "select", "file-input"})

# stock widget template -> (stock option, daisy template, daisy option)
_DAISY_TEMPLATES: Final[Mapping[str, tuple[str | None, str, str | None]]] = {
    "django/forms/widgets/radio.html": (
        "django/forms/widgets/radio_option.html",
        "daisy_forms/widgets/radio.html",
        "daisy_forms/widgets/radio_option.html",
    ),
    "django/forms/widgets/checkbox_select.html": (
        "django/forms/widgets/checkbox_option.html",
        "daisy_forms/widgets/checkbox_select.html",
        "daisy_forms/widgets/checkbox_option.html",
    ),
    "django/forms/widgets/clearable_file_input.html": (
        None,
        "daisy_forms/widgets/clearable_file_input.html",
        None,
    ),
}


def merge_class(existing: str | None, extra: str) -> str:
    return " ".join(part for part in (existing, extra) if part)


def _uses_stock_template(widget: Widget) -> bool:
    template_name = widget.template_name or ""
    if template_name.startswith("daisy_forms/"):
        return True
    if template_name in _DAISY_TEMPLATES:
        stock_option, _, _ = _DAISY_TEMPLATES[template_name]
        return getattr(widget, "option_template_name", None) == stock_option
    if type(widget).__module__ == "django.forms.widgets":
        return True
    for widget_type in type(widget).__mro__:
        if widget_type in WIDGET_CLASSES:
            return template_name == getattr(widget_type, "template_name", None)
    return False


class DaisyBoundField(BoundField):
    """A Django bound field that adds daisyUI classes without mutating widgets."""

    template_override: str | None = None

    extra_attrs: Mapping[str, str] = MappingProxyType({})

    @property
    def template_name(self) -> str:
        if self.template_override is not None:
            if not self.template_override.strip():
                raise TemplateDoesNotExist(
                    "Daisy field template overrides cannot be blank."
                )
            return self.template_override
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

        classes = list(
            dict.fromkeys(
                token
                for token in (
                    base_class,
                    f"{base_class}-error" if self.errors else None,
                    *str(widget.attrs.get("class", "")).split(),
                    *str(built.get("class", "")).split(),
                )
                if token
            )
        )
        if base_class in _SIZED_CLASSES and "w-full" not in classes:
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
        daisy_templates = _DAISY_TEMPLATES.get(widget.template_name or "")
        if daisy_templates is not None:
            stock_option, daisy_template, option_template = daisy_templates
            current_option = getattr(widget, "option_template_name", None)
            if current_option == stock_option:
                widget.template_name = daisy_template
                if option_template:
                    cast(Any, widget).option_template_name = option_template
        merged_attrs = cast(dict[str, str | bool], dict(attrs or {}))
        for key, value in self.extra_attrs.items():
            merged_attrs[key] = (
                merge_class(cast(str | None, merged_attrs.get("class")), value)
                if key == "class"
                else value
            )
        return super().as_widget(widget, merged_attrs, only_initial)
