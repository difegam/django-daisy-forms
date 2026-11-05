"""Template tags and filters for daisyUI fields, fieldsets, and formsets."""

from __future__ import annotations

import copy
import re
from dataclasses import dataclass
from typing import Any

from django import template
from django.forms import BoundField
from django.forms.forms import BaseForm
from django.forms.formsets import BaseFormSet
from django.template import TemplateSyntaxError
from django.template.base import FilterExpression, Parser, Token
from django.utils.translation import gettext

from ..boundfield import DaisyBoundField, is_allowed_attribute, option_text
from ..layout import Fieldset, resolve_fieldsets

register = template.Library()

_ATTRIBUTE_RE = re.compile(
    r"^(?P<name>[A-Za-z_][A-Za-z0-9_:.-]*)(?P<op>\+=|=)(?P<value>.+)$"
)


@dataclass
class DaisyFieldNode(template.Node):
    field: FilterExpression
    attributes: list[tuple[str, FilterExpression]]

    def render(self, context: template.Context) -> str:
        bound_field = self.field.resolve(context)
        if not isinstance(bound_field, BoundField):
            raise ValueError(
                f"{{% daisy_field %}} expected a bound field, got {bound_field!r}."
            )
        if not isinstance(bound_field, DaisyBoundField):
            raise TemplateSyntaxError(
                "{% daisy_field %} cannot be used on a field that opts out of "
                "DaisyBoundField (a plain BoundField opts out); render it with "
                "{{ field }} instead."
            )

        clone = copy.copy(bound_field)
        clone.apply_options(
            (name, option_text(expression.resolve(context)))
            for name, expression in self.attributes
        )
        return clone.as_field_group()


@register.tag("daisy_field")
def daisy_field(parser: Parser, token: Token) -> DaisyFieldNode:
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("daisy_field requires a bound field")

    attributes: list[tuple[str, FilterExpression]] = []
    for bit in bits[2:]:
        match = _ATTRIBUTE_RE.match(bit)
        if match is None:
            raise TemplateSyntaxError(f"Invalid daisy_field attribute: {bit}")
        name = match.group("name")
        operator = match.group("op")
        if not is_allowed_attribute(name):
            raise TemplateSyntaxError(f"Attribute is not allowed: {name}")
        if operator == "+=" and name != "class":
            raise TemplateSyntaxError("Only class supports +=")
        attributes.append((name, parser.compile_filter(match.group("value"))))

    return DaisyFieldNode(parser.compile_filter(bits[1]), attributes)


@register.filter
def daisy_fieldsets(form: BaseForm) -> list[Fieldset] | None:
    """Return the form's resolved fieldsets, or ``None`` when it declares none."""

    return resolve_fieldsets(form)


@register.filter
def daisy_formset_noun(formset: BaseFormSet[Any]) -> str | None:
    """Return the verbose name of a model formset's model, if any."""

    model = getattr(formset, "model", None)
    return str(model._meta.verbose_name) if model is not None else None


@register.filter
def daisy_hidden_errors(form: BaseForm) -> list[str]:
    """Return a form's hidden-field errors, labelled the way Django does."""

    return [
        gettext("(Hidden field %(name)s) %(error)s")
        % {"name": field.name, "error": str(error)}
        for field in form.hidden_fields()
        for error in field.errors
    ]


@register.inclusion_tag("daisy_forms/_formset_cell.html")
def daisy_cell(field: BoundField, formset_prefix: str) -> dict[str, object]:
    """Render a field as a table cell labelled by its column header."""

    label_id = f"{formset_prefix}-{field.name}-label"
    attrs: dict[str, str | bool] | None = (
        None if field.use_fieldset else {"aria-labelledby": label_id}
    )
    widget = field.as_widget(attrs=attrs)
    return {"field": field, "label_id": label_id, "widget": widget}


@register.filter
def daisy_column_count(formset: BaseFormSet[Any]) -> int:
    """Return the number of columns in a table formset, including actions."""

    fields = formset.empty_form.visible_fields()
    return sum(1 for field in fields if field.name != "DELETE") + 1
