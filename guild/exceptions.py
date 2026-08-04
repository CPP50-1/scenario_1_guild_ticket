"""Custom exception hierarchy and a context manager that batches validation
errors instead of raising on the first one.

Day 3 target: build your own context manager (as a reminder of __enter__/
__exit__, which trainees have already seen once) and the modern
contextlib.contextmanager style (new).
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, List


class GuildError(Exception):
    """Base class for every error raised by this package.

    Kept broad on purpose: catching GuildError at an integration boundary
    should catch anything this package can raise, without callers needing
    to know the full hierarchy.
    """


class ValidationError(GuildError):
    """Base class for all field-validation failures."""


class RequiredFieldError(ValidationError):
    """Raised when a required field is missing or None."""

    def __init__(self, field_name: str):
        self.field_name = field_name
        super().__init__(f"'{field_name}' is required and cannot be None")


class TypeMismatchError(ValidationError):
    """Raised when a value's type does not match the field's declared type."""

    def __init__(self, field_name: str, expected: type, got: object):
        self.field_name = field_name
        self.expected = expected
        self.got = got
        super().__init__(
            f"'{field_name}' expected {expected.__name__}, "
            f"got {type(got).__name__} ({got!r})"
        )


class RangeError(ValidationError):
    """Raised when a numeric value falls outside its allowed range."""

    def __init__(self, field_name: str, value: object, minimum=None, maximum=None):
        self.field_name = field_name
        self.value = value
        self.minimum = minimum
        self.maximum = maximum
        bounds = []
        if minimum is not None:
            bounds.append(f">= {minimum}")
        if maximum is not None:
            bounds.append(f"<= {maximum}")
        bound_text = " and ".join(bounds) if bounds else "in range"
        super().__init__(f"'{field_name}' must be {bound_text}, got {value!r}")


class InvalidChoiceError(ValidationError):
    """Raised when a value is not one of a field's allowed choices."""

    def __init__(self, field_name: str, value: object, choices):
        self.field_name = field_name
        self.value = value
        self.choices = choices
        super().__init__(
            f"'{field_name}' must be one of {choices}, got {value!r}"
        )


class ValidationErrorGroup(GuildError):
    """Raised by batch_validation() once the block exits, if any errors were
    collected. Holds every individual error rather than just the first one.
    """

    def __init__(self, errors: List[ValidationError]):
        self.errors = errors
        summary = "; ".join(str(e) for e in errors)
        super().__init__(f"{len(errors)} validation error(s): {summary}")


@contextmanager
def batch_validation() -> Iterator[List[ValidationError]]:
    """Context manager that collects ValidationErrors raised inside the
    block instead of stopping at the first one.

    Usage:
        with batch_validation() as errors:
            for character in candidates:
                try:
                    character.validate()
                except ValidationError as exc:
                    errors.append(exc)
        # after the `with` block: if errors were collected, a single
        # ValidationErrorGroup is raised summarizing all of them.

    This is written with @contextlib.contextmanager (generator style) rather
    than a full __enter__/__exit__ class, since that's the new content for
    Day 3 — trainees already built a class-based context manager once
    before (the reminder), this is the alternative form.
    """
    errors: List[ValidationError] = []
    yield errors
    if errors:
        raise ValidationErrorGroup(errors)
