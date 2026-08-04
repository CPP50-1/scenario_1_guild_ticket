"""Day 3, Dev B: a quest pipeline built almost entirely from itertools.

Quests, rewards, and rosters are naturally filterable/groupable/combinable
collections, so each itertools function below maps onto a real
reporting/matching need rather than a toy list of numbers.
"""
from __future__ import annotations

import itertools
from typing import Dict, Iterable, Iterator, List

from .models import Character

Quest = Dict[str, object]


# --- Static quest sources, combined with itertools.chain -------------------

def daily_quests() -> Iterator[Quest]:
    yield {"name": "Clear the Rat Cellar", "reward_gold": 20, "min_level": 1}
    yield {"name": "Escort the Merchant", "reward_gold": 35, "min_level": 2}


def guild_quests() -> Iterator[Quest]:
    yield {"name": "Retrieve the Lost Banner", "reward_gold": 60, "min_level": 3}
    yield {"name": "Defend the Outpost", "reward_gold": 90, "min_level": 5}


def event_quests() -> Iterator[Quest]:
    yield {"name": "Harvest Festival Errand", "reward_gold": 15, "min_level": 1}


def combined_quest_feed() -> Iterator[Quest]:
    """itertools.chain: treats three separate generators as one continuous
    stream, without materializing any of them into a combined list first.
    """
    return itertools.chain(daily_quests(), guild_quests(), event_quests())


# --- An infinite source, paired with itertools.islice ----------------------

def endless_bounty_quests() -> Iterator[Quest]:
    """An intentionally infinite generator — bounty postings that never
    stop being generated, with a slowly increasing reward. Only useful in
    combination with something that limits how much of it gets consumed.
    """
    for i in itertools.count(start=1):
        yield {
            "name": f"Bounty Contract #{i}",
            "reward_gold": 10 + i * 5,
            "min_level": 1 + i // 3,
        }


def first_n_bounties(n: int) -> List[Quest]:
    """itertools.islice: pulls exactly n items from an infinite generator
    without ever asking it to produce more than that, and without needing
    any manual "if count >= n: break" bookkeeping.
    """
    return list(itertools.islice(endless_bounty_quests(), n))


# --- itertools.takewhile: budget-limited quest selection --------------------

def quests_under_budget(quests: Iterable[Quest], budget: int) -> List[Quest]:
    """itertools.takewhile stops at the *first* item that fails the
    predicate — it does not filter the whole stream like `filter()` would.
    That means the input must already be sorted by reward_gold for this to
    return "all quests under budget" rather than "quests under budget
    until the first expensive one, then nothing else is even looked at."
    This distinction (takewhile vs filter) is the actual teaching point —
    demonstrate what happens if you skip the sort.
    """
    ordered = sorted(quests, key=lambda q: q["reward_gold"])
    return list(itertools.takewhile(lambda q: q["reward_gold"] < budget, ordered))


# --- itertools.groupby: roster reporting -----------------------------------

def group_roster_by_role(characters: Iterable[Character]) -> Dict[str, List[Character]]:
    """itertools.groupby only groups *consecutive* runs of the same key —
    it is not a general-purpose "group by" like SQL's GROUP BY unless the
    input is pre-sorted on that same key first. Sorting first is what
    makes this correct rather than accidentally correct.
    """
    ordered = sorted(characters, key=lambda c: c.describe_role())
    return {
        role: list(group)
        for role, group in itertools.groupby(ordered, key=lambda c: c.describe_role())
    }


# --- itertools.product: eligibility matching --------------------------------

def eligible_assignments(
    characters: Iterable[Character], quests: Iterable[Quest]
) -> List[tuple]:
    """itertools.product builds every (character, quest) pairing without a
    nested for-loop; filtering afterwards keeps the level-eligibility rule
    as a single readable expression rather than buried in loop logic.
    """
    characters = list(characters)
    quests = list(quests)
    return [
        (character, quest)
        for character, quest in itertools.product(characters, quests)
        if character.level >= quest["min_level"]
    ]
