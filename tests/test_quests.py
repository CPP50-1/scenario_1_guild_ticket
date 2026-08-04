from guild.models import Mage, Rogue, Warrior
from guild.quests import (
    combined_quest_feed,
    eligible_assignments,
    endless_bounty_quests,
    first_n_bounties,
    group_roster_by_role,
    quests_under_budget,
)


def test_chain_combines_all_sources():
    feed = list(combined_quest_feed())
    names = {q["name"] for q in feed}
    assert "Clear the Rat Cellar" in names  # daily
    assert "Defend the Outpost" in names  # guild
    assert "Harvest Festival Errand" in names  # event
    assert len(feed) == 5


def test_islice_limits_infinite_generator():
    bounties = first_n_bounties(3)
    assert len(bounties) == 3
    assert bounties[0]["name"] == "Bounty Contract #1"
    # Confirm the underlying generator truly is unbounded by taking a
    # larger slice directly.
    gen = endless_bounty_quests()
    first_ten_names = [next(gen)["name"] for _ in range(10)]
    assert len(first_ten_names) == 10


def test_takewhile_requires_presorted_input():
    quests = list(combined_quest_feed())
    under_40 = quests_under_budget(quests, budget=40)
    assert all(q["reward_gold"] < 40 for q in under_40)
    # every quest actually under budget should be present, since
    # quests_under_budget sorts internally before takewhile
    all_under_40 = [q for q in quests if q["reward_gold"] < 40]
    assert len(under_40) == len(all_under_40)


def test_groupby_roster_by_role():
    party = [Warrior("Grom", level=1), Warrior("Thok", level=2), Mage("Jaina", level=1)]
    grouped = group_roster_by_role(party)
    assert set(grouped["Warrior"]) == {party[0], party[1]}
    assert grouped["Mage"] == [party[2]]


def test_product_eligible_assignments():
    party = [Warrior("Grom", level=1), Rogue("Sly", level=5)]
    quests = list(combined_quest_feed())
    pairs = eligible_assignments(party, quests)
    # Grom (level 1) should only be eligible for min_level <= 1 quests
    grom_pairs = [q for c, q in pairs if c.name == "Grom"]
    assert all(q["min_level"] <= 1 for q in grom_pairs)
    # Sly (level 5) should be eligible for everything
    sly_pairs = [q for c, q in pairs if c.name == "Sly"]
    assert len(sly_pairs) == len(quests)
