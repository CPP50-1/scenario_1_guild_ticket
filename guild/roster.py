"""Day 2 workshop targets, one per developer:

    Dev A -> OrderedSet      (custom unique-item structure)
    Dev B -> StatCalculator  (memoized callable, state held between calls)
    Dev C -> Roster          (full container protocol + iterator protocol
                              from scratch, i.e. __iter__ returning a real
                              iterator object with __next__, not a generator)
"""
from __future__ import annotations

from typing import Any, Dict, Iterator, List

from .models import Character


# --- Dev A: OrderedSet ------------------------------------------------------

class OrderedSet:
    """A set that remembers insertion order — used here for unique quest
    items a party has picked up. Backed by a dict (Python 3.7+ dicts are
    insertion-ordered) purely for its keys, giving O(1) membership and
    O(1) amortized insertion instead of the O(n) membership check a list
    would need.
    """

    def __init__(self, items: Iterator[Any] = ()):
        self._data: Dict[Any, None] = {}
        for item in items:
            self.add(item)

    def add(self, item: Any) -> None:
        self._data[item] = None

    def discard(self, item: Any) -> None:
        self._data.pop(item, None)

    def __contains__(self, item: Any) -> bool:
        return item in self._data

    def __iter__(self) -> Iterator[Any]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"OrderedSet({list(self._data)!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, OrderedSet):
            return list(self._data) == list(other._data)
        return NotImplemented


# --- Dev B: memoized callable ------------------------------------------------

class StatCalculator:
    """A callable object that caches results by argument, for an
    expensive/derived stat computation. Demonstrates __call__ plus state
    held on the instance between calls (a "function with memory") —
    something a plain function can't do without a global or a closure
    workaround.
    """

    def __init__(self):
        self._cache: Dict[tuple, int] = {}
        self.calls = 0  # tracks total calls, cache hits or not — useful
        # for the workshop discussion of *why* memoization saved work.
        self.cache_hits = 0

    def __call__(self, character: Character, difficulty: int) -> int:
        self.calls += 1
        key = (type(character).__name__, character.level, difficulty)
        if key in self._cache:
            self.cache_hits += 1
            return self._cache[key]
        # Deliberately "expensive-looking" formula — the point is that
        # this computation only actually runs once per unique key.
        result = (character.level * 7 + difficulty * 13) % 100
        self._cache[key] = result
        return result


# --- Dev C: full container protocol + iterator protocol from scratch -------

class RosterIterator:
    """A standalone iterator object for Roster, built from scratch rather
    than via a generator function — this is what Day 2's "__iter__ and
    __next__ from scratch" specifically asks for. A generator would hide
    the mechanism; this makes the state (the current index) explicit.
    """

    def __init__(self, characters: List[Character]):
        self._characters = characters
        self._index = 0

    def __iter__(self) -> "RosterIterator":
        # An iterator must itself be iterable (returning itself) so that
        # `for x in some_iterator:` also works, not just `for x in roster:`.
        return self

    def __next__(self) -> Character:
        if self._index >= len(self._characters):
            raise StopIteration
        character = self._characters[self._index]
        self._index += 1
        return character


class Roster:
    """A guild's roster of characters, supporting the full container
    protocol: indexing, assignment, deletion, membership, length, and
    iteration.
    """

    def __init__(self, characters: Iterator[Character] = ()):
        self._characters: List[Character] = list(characters)

    def __getitem__(self, index: int) -> Character:
        return self._characters[index]

    def __setitem__(self, index: int, value: Character) -> None:
        if not isinstance(value, Character):
            raise TypeError(f"Roster only holds Character instances, got {type(value).__name__}")
        self._characters[index] = value

    def __delitem__(self, index: int) -> None:
        del self._characters[index]

    def __contains__(self, item: Character) -> bool:
        return item in self._characters

    def __len__(self) -> int:
        return len(self._characters)

    def __iter__(self) -> RosterIterator:
        return RosterIterator(self._characters)

    def __repr__(self) -> str:
        return f"Roster({self._characters!r})"

    def add(self, character: Character) -> None:
        self._characters.append(character)

    def alive_characters(self) -> Iterator[Character]:
        """A small generator-based query, distinct from the from-scratch
        iterator above: this exists to show the *contrast* between
        "iterator built by hand" (RosterIterator) and "iterator built by
        a generator function" (this method) doing a filtered pass — both
        satisfy the iterator protocol, but the generator version is far
        less code for a simple case.
        """
        for character in self._characters:
            if bool(character):  # relies on Character.__bool__ (Day 1)
                yield character

    def active_characters(self) -> Iterator[Character]:
        """generator-based query to get all character in the roster with the status set to "active"

        Yields:
            Iterator[Character]: The list of active characters
        """
        for character in self._characters:
            if character.status == "active" or character.status == 'benched':
                yield character

    def sorted_by_level(self) -> List[Character]:
        # Relies on Character.__lt__ (Day 1) — no key= needed.
        return sorted(self._characters)
