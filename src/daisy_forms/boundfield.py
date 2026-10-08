"""Bound-field behavior for daisyUI controls."""

from __future__ import annotations

import copy
from collections.abc import Mapping
from types import MappingProxyType
from typing import Any, Final, cast

from django.forms.boundfield import BoundField
from django.forms.widgets import CheckboxSelectMultiple, Input, RadioSelect, Widget
from django.template import TemplateDoesNotExist, TemplateSyntaxError
from django.utils.html import format_html
from django.utils.safestring import SafeString

from .classes import WIDGET_CLASSES, daisy_class_for

_SIZED_CLASSES: Final = frozenset({"input", "textarea", "select", "file-input"})
_NON_TEXT_INPUT_TYPES: Final = frozenset(
    {"button", "checkbox", "file", "hidden", "image", "radio", "reset", "submit"}
)

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

_INLINE_DAISY_TEMPLATES: Final[Mapping[str, str]] = {
    "daisy_forms/widgets/radio.html": "daisy_forms/widgets/radio_inline.html",
    "daisy_forms/widgets/checkbox_select.html": (
        "daisy_forms/widgets/checkbox_select_inline.html"
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


def _uses_registered_stock_template(widget: Widget) -> bool:
    """Return whether a registered widget still uses its stock template."""

    template_name = widget.template_name or ""
    if template_name in _DAISY_TEMPLATES:
        stock_option, _, _ = _DAISY_TEMPLATES[template_name]
        return getattr(widget, "option_template_name", None) == stock_option
    for widget_type in type(widget).__mro__:
        if widget_type in WIDGET_CLASSES:
            return template_name == getattr(widget_type, "template_name", None)
        if (
            widget_type.__module__ == "django.forms.widgets"
            and "template_name" in widget_type.__dict__
        ):
            return template_name == cast(
                str | None, getattr(widget_type, "template_name", None)
            )
    return False


class DaisyBoundField(BoundField):
    """A Django bound field that adds daisyUI classes without mutating widgets."""

    template_override: str | None = None

    extra_attrs: Mapping[str, str] = MappingProxyType({})

    choice_layout: str | None = None
    prefix: str | None = None
    suffix: str | None = None

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
        has_addons = bool(self.prefix or self.suffix)
        if base_class == "input" and has_addons:
            classes = [class_name for class_name in classes if class_name != "w-full"]
            if "join-item" not in classes:
                classes.append("join-item")
            if "flex-1" not in classes:
                classes.append("flex-1")
        if (
            base_class in _SIZED_CLASSES
            and "w-full" not in classes
            and not (base_class == "input" and has_addons)
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
        if self.choice_layout is not None:
            if self.choice_layout != "inline":
                raise TemplateSyntaxError("choices must be set to 'inline'.")
            if not isinstance(widget, (RadioSelect, CheckboxSelectMultiple)) or not (
                _uses_registered_stock_template(widget)
            ):
                raise TemplateSyntaxError(
                    "choices='inline' requires a stock RadioSelect or "
                    "CheckboxSelectMultiple widget."
                )

        has_addons = bool(self.prefix or self.suffix)
        if has_addons:
            effective_attrs = dict(attrs or {})
            effective_attrs.update(self.extra_attrs)
            input_type = effective_attrs.get("type")
            if input_type is None:
                input_type = widget.attrs.get("type") or getattr(
                    widget, "input_type", None
                )
            base_class = daisy_class_for(
                widget, str(input_type) if input_type is not None else None
            )
            is_non_text_input = (
                isinstance(widget, Input)
                and str(input_type or "") in _NON_TEXT_INPUT_TYPES
            )
            if (
                not _uses_registered_stock_template(widget)
                or widget.is_hidden
                or base_class != "input"
                or is_non_text_input
            ):
                raise TemplateSyntaxError(
                    "prefix and suffix require a stock widget rendered with "
                    "daisyUI's input component."
                )

        daisy_templates = _DAISY_TEMPLATES.get(widget.template_name or "")
        if daisy_templates is not None:
            stock_option, daisy_template, option_template = daisy_templates
            current_option = getattr(widget, "option_template_name", None)
            if current_option == stock_option:
                widget.template_name = daisy_template
                if option_template:
                    cast(Any, widget).option_template_name = option_template
        if self.choice_layout == "inline":
            inline_template = _INLINE_DAISY_TEMPLATES.get(widget.template_name or "")
            if inline_template is None:
                raise TemplateSyntaxError(
                    "choices='inline' requires a stock RadioSelect or "
                    "CheckboxSelectMultiple widget."
                )
            widget.template_name = inline_template
        merged_attrs = cast(dict[str, str | bool], dict(attrs or {}))
        for key, value in self.extra_attrs.items():
            merged_attrs[key] = (
                merge_class(cast(str | None, merged_attrs.get("class")), value)
                if key == "class"
                else value
            )
        rendered_widget = super().as_widget(widget, merged_attrs, only_initial)
        if not has_addons:
            return rendered_widget

        prefix = (
            format_html('<span class="input join-item">{}</span>', self.prefix)
            if self.prefix
            else ""
        )
        suffix = (
            format_html('<span class="input join-item">{}</span>', self.suffix)
            if self.suffix
            else ""
        )
        return format_html(
            '<div class="join w-full">{}{}{}</div>',
            prefix,
            rendered_widget,
            suffix,
        )
