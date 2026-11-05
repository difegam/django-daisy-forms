"""Resolve a form's ``fieldsets`` declaration into groups of bound fields."""

from __future__ import annotations

import copy
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Final

from django.core.exceptions import ImproperlyConfigured
from django.forms import BoundField
from django.forms.forms import BaseForm

from .boundfield import DaisyBoundField

STACKED_TEMPLATE: Final = "daisy_forms/field.html"
MAX_ROW_FIELDS: Final = 4
GRID_CLASSES: Final[Mapping[int, str]] = {
    2: "grid gap-4 md:grid-cols-2",
    3: "grid gap-4 md:grid-cols-3",
    4: "grid gap-4 md:grid-cols-4",
}


@dataclass(frozen=True)
class Row:
    fields: Sequence[BoundField]

    @property
    def grid_class(self) -> str | None:
        return GRID_CLASSES.get(len(self.fields))


@dataclass(frozen=True)
class Fieldset:
    title: str | None
    rows: Sequence[Row]
    description: str | None = None
    classes: Sequence[str] = field(default_factory=tuple)

    @property
    def collapsible(self) -> bool:
        return "collapse" in self.classes

    @property
    def extra_class(self) -> str:
        return " ".join(name for name in self.classes if name != "collapse")

    @property
    def has_errors(self) -> bool:
        return any(bound.errors for row in self.rows for bound in row.fields)


def _stacked(bound: BoundField) -> BoundField:
    """Return a row field that keeps the stacked template unless overridden."""

    if not isinstance(bound, DaisyBoundField) or bound.template_override is not None:
        return bound
    clone = copy.copy(bound)
    clone.template_override = STACKED_TEMPLATE
    return clone


def resolve_fieldsets(form: BaseForm) -> list[Fieldset] | None:
    """Group a form's visible fields by its ``fieldsets`` attribute.

    Returns ``None`` when the form declares no fieldsets.
    """

    declared = getattr(form, "fieldsets", None)
    if not declared:
        return None
    form_name = type(form).__name__
    seen: set[str] = set()

    def bound_field(name: object) -> BoundField:
        if not isinstance(name, str) or name not in form.fields:
            raise ImproperlyConfigured(
                f"{form_name}.fieldsets names an unknown field: {name!r}."
            )
        if name in seen:
            raise ImproperlyConfigured(
                f"{form_name}.fieldsets lists {name!r} more than once."
            )
        seen.add(name)
        return form[name]

    fieldsets: list[Fieldset] = []
    for entry in declared:
        try:
            title, options = entry
        except (TypeError, ValueError):
            raise ImproperlyConfigured(
                f"{form_name}.fieldsets entries must be (title, options) pairs."
            ) from None
        if not isinstance(options, Mapping) or "fields" not in options:
            raise ImproperlyConfigured(
                f"{form_name}.fieldsets options must be a mapping with 'fields'."
            )
        rows: list[Row] = []
        for item in options["fields"]:
            if isinstance(item, (tuple, list)):
                if len(item) > MAX_ROW_FIELDS:
                    raise ImproperlyConfigured(
                        f"{form_name}.fieldsets rows hold at most "
                        f"{MAX_ROW_FIELDS} fields."
                    )
                bound_row = [bound_field(name) for name in item]
                visible = [bound for bound in bound_row if not bound.is_hidden]
                if len(visible) > 1:
                    rows.append(Row([_stacked(bound) for bound in visible]))
                elif visible:
                    rows.append(Row(visible))
            else:
                bound = bound_field(item)
                if not bound.is_hidden:
                    rows.append(Row([bound]))
        fieldsets.append(
            Fieldset(
                title=str(title) if title else None,
                rows=rows,
                description=options.get("description"),
                classes=tuple(options.get("classes", ())),
            )
        )

    remaining = [
        Row([bound]) for bound in form.visible_fields() if bound.name not in seen
    ]
    if remaining:
        fieldsets.append(Fieldset(title=None, rows=remaining))
    return fieldsets
