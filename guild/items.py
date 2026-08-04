"""The Day 1 shared-build target: a class with full comparison, equality,
repr, and set support — analogous to the "Money class" pattern (currency +
amount) from the program, adapted to the guild domain (an inventory item
with a value and a rarity tier).

This is deliberately built with plain attributes (no descriptors yet) —
descriptors are Day 4 content and introducing them here would blur the
two days together.
"""
from __future__ import annotations

from functools import total_ordering
from enum import IntEnum


class Rarity(IntEnum):
    """IntEnum so rarities compare naturally (COMMON < RARE < LEGENDARY)
    without any extra work — this is used by Item.__lt__ below.
    """
    COMMON = 1
    UNCOMMON = 2
    RARE = 3
    EPIC = 4
    LEGENDARY = 5


@total_ordering
class Item:
    """An inventory item, ordered first by rarity then by value.

    __eq__ and __hash__ are defined together and stay consistent with each
    other on purpose: two Items are equal (and hash equal) exactly when
    name, rarity and value all match. Overriding __eq__ without __hash__
    would make Item unusable in sets/dicts (the exact pitfall the program
    calls out) — that's why both are always defined as a pair here, never
    one without the other.
    """

    def __init__(self, name: str, rarity: Rarity, value: int):
        self.name = name
        self.rarity = rarity
        self.value = value

    def __repr__(self) -> str:
        return f"Item(name={self.name!r}, rarity={self.rarity.name}, value={self.value})"

    def __str__(self) -> str:
        # __str__ favors a human-readable line (for display/logging);
        # __repr__ favors an unambiguous, reconstructable representation
        # (for debugging). Odoo's own log lines and shell reprs follow the
        # same split.
        return f"{self.name} ({self.rarity.name.title()}, {self.value}g)"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Item):
            return NotImplemented
        return (self.name, self.rarity, self.value) == (other.name, other.rarity, other.value)

    def __hash__(self) -> int:
        return hash((self.name, self.rarity, self.value))

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Item):
            return NotImplemented
        # Primary sort key: rarity, then value as a tiebreaker.
        return (self.rarity, self.value) < (other.rarity, other.value)

    def __bool__(self) -> bool:
        # An Item is "truthy" if it has any value at all — a zero-value
        # junk item is falsy. Purely illustrative of __bool__, not a rule
        # the domain strictly needs, kept simple on purpose.
        return self.value > 0
