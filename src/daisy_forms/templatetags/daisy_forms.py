"""Template tags for rendering individual daisyUI fields."""

from __future__ import annotations

import copy
import re
from dataclasses import dataclass

from django import template
from django.forms import BoundField
from django.template import TemplateSyntaxError
from django.template.base import FilterExpression, Parser, Token

from ..boundfield import DaisyBoundField, merge_class

register = template.Library()

_ATTRIBUTE_RE = re.compile(
    r"^(?P<name>[A-Za-z_][A-Za-z0-9_:.-]*)(?P<op>\+=|=)(?P<value>.+)$"
)
_RESERVED_ATTRIBUTES = frozenset({"aria-invalid", "aria-describedby"})
_INLINE_HANDLER_RE = re.compile(r"^(?:data-)?(?:on|hx-on|x-on|x-init)")


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
        extra_attrs = dict(bound_field.extra_attrs)

        for name, expression in self.attributes:
            resolved = expression.resolve(context)
            value = "" if resolved is None else str(resolved)
            if name == "label":
                clone.label = value
            elif name == "template":
                clone.template_override = value
            elif name == "class":
                extra_attrs["class"] = merge_class(extra_attrs.get("class"), value)
            else:
                extra_attrs[name] = value

        clone.extra_attrs = extra_attrs
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
        lowered = name.lower()
        if _INLINE_HANDLER_RE.match(lowered) or lowered in _RESERVED_ATTRIBUTES:
            raise TemplateSyntaxError(f"Attribute is not allowed: {name}")
        if operator == "+=" and name != "class":
            raise TemplateSyntaxError("Only class supports +=")
        attributes.append((name, parser.compile_filter(match.group("value"))))

    return DaisyFieldNode(parser.compile_filter(bits[1]), attributes)
