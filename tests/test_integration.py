"""A small integration test exercising several days' work together — the
kind of thing Day 6 asks trainees to assemble themselves.
"""
from guild.dungeon import guild_transaction
from guild.exceptions import RangeError, ValidationErrorGroup, batch_validation
from guild.models import Mage, Paladin, Warrior
from guild.quests import combined_quest_feed, eligible_assignments
from guild.roster import Roster


def test_full_party_workflow():
    roster = Roster()
    roster.add(Warrior("Grom", level=4))
    roster.add(Mage("Jaina", level=2))
    roster.add(Paladin("Uther", level=6))

    # Day 1/4: dunders + mixins
    assert sorted(c.describe_role() for c in roster) == [
        "Mage",
        "Warrior",
        "Warrior + Tank + Healer",
    ]

    # Day 2: sorting via __lt__, container protocol
    assert roster.sorted_by_level()[0].name == "Jaina"
    assert len(roster) == 3

    # Day 3: itertools quest matching
    quests = list(combined_quest_feed())
    pairs = eligible_assignments(roster, quests)
    assert len(pairs) > 0

    # Day 3: transaction rollback protects the treasury on a bad payout
    treasury = {"gold": 200}
    try:
        with guild_transaction(treasury) as t:
            t["gold"] -= 500  # overdraw
            if t["gold"] < 0:
                raise ValueError("Treasury cannot go negative")
    except ValueError:
        pass
    assert treasury["gold"] == 200  # unchanged, rollback worked

    # Day 3/4: batch validation collecting multiple problems at once
    try:
        with batch_validation() as errors:
            for character in roster:
                if character.level < 3:
                    errors.append(
                        RangeError("level", character.level, minimum=3)
                    )
    except ValidationErrorGroup:
        pass  # expected: Jaina (level 2) triggers this
