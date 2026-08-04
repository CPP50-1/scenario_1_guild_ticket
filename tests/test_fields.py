import pytest

from guild.exceptions import RangeError, RequiredFieldError, TypeMismatchError
from guild.fields import IntField, StringField, Validated


class Dummy:
    label = StringField(max_length=10)
    count = IntField(minimum=0, maximum=5)


def test_valid_assignment_roundtrips():
    d = Dummy()
    d.label = "ok"
    d.count = 3
    assert d.label == "ok"
    assert d.count == 3


def test_required_field_rejects_none():
    d = Dummy()
    with pytest.raises(RequiredFieldError):
        d.label = None


def test_type_mismatch_rejects_wrong_type():
    d = Dummy()
    with pytest.raises(TypeMismatchError):
        d.count = "not an int"


def test_range_error_on_upper_bound():
    d = Dummy()
    with pytest.raises(RangeError):
        d.count = 100


def test_range_error_on_string_max_length():
    d = Dummy()
    with pytest.raises(RangeError):
        d.label = "way too long for this field"


def test_two_instances_do_not_share_values():
    a, b = Dummy(), Dummy()
    a.label, a.count = "a", 1
    b.label, b.count = "b", 2
    assert a.label == "a" and b.label == "b"
    assert a.count == 1 and b.count == 2


def test_optional_field_accepts_none():
    class Optional:
        note = Validated(str, required=False)

    o = Optional()
    o.note = None
    assert o.note is None
