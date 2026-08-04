from guild.items import Item, Rarity
from guild.models import Mage, Rogue, Warrior
from guild.roster import OrderedSet, Roster, RosterIterator, StatCalculator


# --- OrderedSet -------------------------------------------------------------

def test_ordered_set_preserves_insertion_order():
    items = [Item("Sword", Rarity.COMMON, 1), Item("Shield", Rarity.COMMON, 2)]
    s = OrderedSet(items)
    s.add(items[0])  # duplicate, should not change order or length
    assert list(s) == items
    assert len(s) == 2


def test_ordered_set_membership_and_discard():
    sword = Item("Sword", Rarity.COMMON, 1)
    s = OrderedSet([sword])
    assert sword in s
    s.discard(sword)
    assert sword not in s
    assert len(s) == 0


# --- StatCalculator (memoized callable) -------------------------------------

def test_stat_calculator_is_callable_and_caches():
    calc = StatCalculator()
    w = Warrior("Grom", level=3)
    first = calc(w, difficulty=2)
    second = calc(w, difficulty=2)
    assert first == second
    assert calc.calls == 2
    assert calc.cache_hits == 1


def test_stat_calculator_distinguishes_different_keys():
    calc = StatCalculator()
    w = Warrior("Grom", level=3)
    r = Rogue("Sly", level=3)
    result_w = calc(w, difficulty=2)
    result_r = calc(r, difficulty=2)
    # Different type name in the key -> not guaranteed equal, but at least
    # independently cached (no cache hit across different characters).
    assert calc.cache_hits == 0
    calc(w, difficulty=2)
    assert calc.cache_hits == 1


# --- Roster: container protocol + from-scratch iterator --------------------

def test_roster_container_protocol():
    w, m = Warrior("Grom", level=1), Mage("Jaina", level=1)
    roster = Roster([w])
    roster.add(m)
    assert roster[0] is w
    assert m in roster
    assert len(roster) == 2

    replacement = Rogue("Sly", level=1)
    roster[0] = replacement
    assert roster[0] is replacement

    del roster[0]
    assert len(roster) == 1
    assert roster[0] is m


def test_roster_iter_returns_from_scratch_iterator():
    roster = Roster([Warrior("Grom", level=1)])
    iterator = iter(roster)
    assert isinstance(iterator, RosterIterator)
    assert next(iterator).name == "Grom"


def test_roster_alive_characters_generator():
    alive = Warrior("Grom", level=1)
    dead = Mage("Jaina", level=1)
    dead.hp = 0
    roster = Roster([alive, dead])
    assert list(roster.alive_characters()) == [alive]


def test_roster_sorted_by_level_uses_character_lt():
    low = Warrior("Grom", level=1)
    high = Mage("Jaina", level=9)
    roster = Roster([high, low])
    assert roster.sorted_by_level() == [low, high]
