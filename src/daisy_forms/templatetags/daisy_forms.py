"""Template tags for rendering individual daisyUI fields."""

from __future__ import annotations

import copy
import re
from dataclasses import dataclass

from django import template
from django.core.exceptions import FieldError
from django.template import TemplateSyntaxError
from django.template.base import FilterExpression, Parser, Token

from ..boundfield import DaisyBoundField

register = template.Library()

_ATTRIBUTE_RE = re.compile(
    r"^(?P<name>[A-Za-z_][A-Za-z0-9_:.-]*)(?P<op>\+=|=)(?P<value>.+)$"
)


@dataclass
class DaisyFieldNode(template.Node):
    field: FilterExpression
    attributes: list[tuple[str, str, FilterExpression]]

    def render(self, context: template.Context) -> str:
        bound_field = self.field.resolve(context)
        if not isinstance(bound_field, DaisyBoundField):
            raise FieldError("daisy_field requires a Django BoundField")

        clone = copy.copy(bound_field)
        clone.extra_attrs = dict(getattr(bound_field, "extra_attrs", {}))
        clone.label_override = getattr(bound_field, "label_override", None)
        clone.template_override = getattr(bound_field, "template_override", None)

        for name, _operator, expression in self.attributes:
            value = expression.resolve(context)
            if value is None:
                value = ""
            value = str(value)
            if name == "label":
                clone.label_override = value
                clone.label = value
            elif name == "template":
                clone.template_override = value
            elif name == "class":
                existing = clone.extra_attrs.get("class")
                clone.extra_attrs["class"] = " ".join(
                    part for part in (existing, value) if part
                )
            else:
                clone.extra_attrs[name] = value

        return clone.as_field_group()


@register.tag("daisy_field")
def daisy_field(parser: Parser, token: Token) -> DaisyFieldNode:
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("daisy_field requires a bound field")

    attributes: list[tuple[str, str, FilterExpression]] = []
    for bit in bits[2:]:
        match = _ATTRIBUTE_RE.match(bit)
        if match is None:
            raise TemplateSyntaxError(f"Invalid daisy_field attribute: {bit}")
        name = match.group("name")
        operator = match.group("op")
        if name.lower().startswith("on") or name in {
            "aria-invalid",
            "aria-describedby",
        }:
            raise TemplateSyntaxError(f"Attribute is not allowed: {name}")
        if operator == "+=" and name != "class":
            raise TemplateSyntaxError("Only class supports +=")
        attributes.append((name, operator, parser.compile_filter(match.group("value"))))

    return DaisyFieldNode(parser.compile_filter(bits[1]), attributes)
