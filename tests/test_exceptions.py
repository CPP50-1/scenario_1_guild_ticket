import pytest

from guild.exceptions import (
    RequiredFieldError,
    ValidationError,
    ValidationErrorGroup,
    batch_validation,
)


def test_batch_validation_collects_multiple_errors():
    with pytest.raises(ValidationErrorGroup) as exc_info:
        with batch_validation() as errors:
            errors.append(RequiredFieldError("name"))
            errors.append(RequiredFieldError("hp"))
    assert len(exc_info.value.errors) == 2


def test_batch_validation_passes_silently_with_no_errors():
    with batch_validation() as errors:
        pass  # no errors appended
    assert errors == []


def test_error_hierarchy():
    assert issubclass(RequiredFieldError, ValidationError)
