"""Day 3, Dev C: two pieces.

1. An infinite dungeon generator built from yield-from delegation to a
   per-floor sub-generator — the clearest vehicle for "the generator
   execution model" and lazy infinite sequences: a dungeon is conceptually
   endless until the party decides otherwise.
2. A contextlib.contextmanager-style transaction — folded in here since
   the class-based __enter__/__exit__ protocol itself is only a reminder
   for this group (they built one before); the new content is the
   generator-based decorator form.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Dict, Iterator, List


# --- Dungeon: yield-from delegation + lazy infinite sequence ---------------

def floor_encounters(floor_number: int, dungeon_log: List[str]) -> Iterator[Dict]:
    """One floor's worth of encounters. A generator in its own right —
    dungeon_floors() below delegates to it via `yield from` rather than
    inlining its logic, which is what lets each floor's structure stay
    readable on its own.

    Accepts a "retreat" command via .send() at any yield point; if
    received, ends the floor early and returns "retreated" instead of
    "cleared" — that return value is what `yield from` hands back to the
    caller once this generator is exhausted.
    """
    dungeon_log.append(f"Entering floor {floor_number}")
    encounters = [
        {"type": "monster", "name": f"Floor {floor_number} Guardian", "floor": floor_number},
        {"type": "loot", "name": f"Chest #{floor_number}", "floor": floor_number},
    ]
    if floor_number % 3 == 0:
        encounters.append({"type": "trap", "name": "Spike Trap", "floor": floor_number})

    try:
        for encounter in encounters:
            action = yield encounter
            if action == "retreat":
                dungeon_log.append(f"Party retreats mid-floor {floor_number}")
                return "retreated"
        dungeon_log.append(f"Floor {floor_number} cleared")
        return "cleared"
    finally:
        dungeon_log.append(f"Leaving floor {floor_number}")


def dungeon_floors(dungeon_log: List[str]) -> Iterator[Dict]:
    """An intentionally endless generator: there is no fixed last floor,
    only a floor the party chooses to stop at (via "retreat") or a caller
    that stops pulling from it (or calls .close()).

    `yield from floor_encounters(...)` does two things at once here:
    forwards every .send() call straight through to the current floor's
    sub-generator, and captures that sub-generator's return value once it
    finishes — this is what lets the outer loop know *why* the floor
    ended without any extra signalling mechanism.
    """
    floor_number = 0
    try:
        while True:
            floor_number += 1
            result = yield from floor_encounters(floor_number, dungeon_log)
            if result == "retreated":
                dungeon_log.append("Party returns to town.")
                return
    finally:
        # Reached either by the `return` above, or by GeneratorExit when
        # the caller calls .close() (e.g. simulating a disconnect instead
        # of a deliberate retreat) — both end up here, which is the point:
        # cleanup runs regardless of *why* the dungeon run ended.
        dungeon_log.append("Dungeon generator closed.")


# --- Guild treasury transaction ---------------------------------------------

@contextmanager
def guild_transaction(treasury: Dict[str, int]) -> Iterator[Dict[str, int]]:
    """Simulates a database transaction over an in-memory treasury dict:
    mutations inside the `with` block are kept if the block completes
    without error, and rolled back to the pre-block snapshot if it raises.

    This version deliberately re-raises after rollback (it does not
    suppress the exception) — matching real transaction semantics, where
    a failed transaction still needs the caller to know it failed. Contrast
    with __exit__ returning True to *suppress* an exception (the "exception
    suppression" point from the Day 3 theory) — that would be the wrong
    choice here, which is worth discussing explicitly in the workshop.
    """
    snapshot = dict(treasury)
    try:
        yield treasury
    except Exception:
        treasury.clear()
        treasury.update(snapshot)
        raise
