"""Descriptors used as typed, validated class attributes.

Day 4 target: understand __get__/__set__/__delete__, the difference between
data and non-data descriptors, and build a `Validated` descriptor that
type-checks assignment. This module is also the direct anchor for the
"spot it" checkpoint that morning: Odoo's fields.Char / fields.Integer are
descriptors in exactly this sense — this is a from-scratch version of the
same mechanism, not an analogy.
"""
from __future__ import annotations

from typing import Any, Optional, Type

from .exceptions import RangeError, RequiredFieldError, TypeMismatchError


class Field:
    """Base descriptor: a data descriptor (defines both __get__ and __set__,
    so it always takes priority over instance __dict__ entries — this is
    what makes it a *data* descriptor rather than a non-data one).

    Each Field instance is shared across all instances of the owning class,
    but stores each instance's value in that instance's own __dict__ under
    a private name, so values don't leak between instances.
    """

    def __set_name__(self, owner: Type, name: str) -> None:
        # Called automatically by the class machinery at class-creation
        # time. This is how the descriptor learns the attribute name it
        # was assigned to, without the caller having to repeat it.
        self.name = name
        self.private_name = f"_{name}"

    def __get__(self, instance: Any, owner: Type) -> Any:
        if instance is None:
            # Accessed on the class itself (e.g. Character.hp) rather than
            # an instance — return the descriptor for introspection.
            return self
        return instance.__dict__.get(self.private_name)

    def __set__(self, instance: Any, value: Any) -> None:
        self.validate(value)
        instance.__dict__[self.private_name] = value

    def __delete__(self, instance: Any) -> None:
        instance.__dict__.pop(self.private_name, None)

    def validate(self, value: Any) -> None:
        """Subclasses override this to add type/range checks. Base Field
        accepts anything (no constraint) except it still refuses to store
        an assignment silently — this hook is what Validated overrides.
        """


class Validated(Field):
    """A descriptor that type-checks (and optionally range-checks) any
    value assigned to it. This is the Day 4 workshop target: one reusable
    mechanism instead of hand-written `if not isinstance(...)` checks
    repeated in every __init__ (which is exactly what trainees hit and
    found tedious on the pre-project afternoon).
    """

    def __init__(
        self,
        expected_type: Type,
        required: bool = True,
        minimum: Optional[float] = None,
        maximum: Optional[float] = None,
    ):
        self.expected_type = expected_type
        self.required = required
        self.minimum = minimum
        self.maximum = maximum

    def validate(self, value: Any) -> None:
        if value is None:
            if self.required:
                raise RequiredFieldError(self.name)
            return
        if not isinstance(value, self.expected_type):
            raise TypeMismatchError(self.name, self.expected_type, value)
        if self.minimum is not None and value < self.minimum:
            raise RangeError(self.name, value, minimum=self.minimum, maximum=self.maximum)
        if self.maximum is not None and value > self.maximum:
            raise RangeError(self.name, value, minimum=self.minimum, maximum=self.maximum)


class StringField(Validated):
    """A Validated shortcut for non-empty strings."""

    def __init__(self, required: bool = True, max_length: Optional[int] = None):
        super().__init__(expected_type=str, required=required)
        self.max_length = max_length

    def validate(self, value: Any) -> None:
        super().validate(value)
        if value is not None and self.max_length is not None and len(value) > self.max_length:
            raise RangeError(self.name, value, maximum=self.max_length)
        if value is not None and value.strip() == "" and self.required:
            raise RequiredFieldError(self.name)


class IntField(Validated):
    """A Validated shortcut for integers, with optional min/max bounds."""

    def __init__(self, required: bool = True, minimum: Optional[int] = None, maximum: Optional[int] = None):
        super().__init__(expected_type=int, required=required, minimum=minimum, maximum=maximum)
