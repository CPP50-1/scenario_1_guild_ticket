import pytest

from guild.models import (
    Character,
    GuildMeta,
    HealerMixin,
    LoggedMage,
    Mage,
    Paladin,
    Rogue,
    TankMixin,
    Warrior,
)


def test_metaclass_registers_concrete_subclasses():
    assert GuildMeta.registry["Warrior"] is Warrior
    assert GuildMeta.registry["Mage"] is Mage
    assert GuildMeta.registry["Rogue"] is Rogue
    assert GuildMeta.registry["Paladin"] is Paladin


def test_metaclass_rejects_non_int_base_hp():
    with pytest.raises(TypeError):
        class Broken2(Character):
            base_hp = "not an int"


def test_dunder_repr_and_str():
    w = Warrior("Grom", level=2)
    assert repr(w) == "Warrior(name='Grom', level=2, hp=30)"
    assert str(w) == "Grom the Warrior (Lv.2, 30 HP)"


def test_dunder_eq_and_hash():
    a = Warrior("Grom", level=2)
    b = Warrior("Grom", level=2)
    c = Warrior("Thok", level=2)
    assert a == b
    assert hash(a) == hash(b)
    assert a != c


def test_dunder_lt_orders_by_level():
    low = Warrior("Grom", level=1)
    high = Warrior("Grommash", level=10)
    assert low < high


def test_dunder_bool_reflects_hp():
    w = Warrior("Grom", level=1)
    assert bool(w) is True
    w.hp = 0
    assert bool(w) is False


def test_paladin_mro_order():
    assert Paladin.__mro__[:5] == (Paladin, HealerMixin, TankMixin, Warrior, Character)


def test_paladin_describe_role_cooperative_chain():
    p = Paladin("Uther", level=1)
    assert p.describe_role() == "Warrior + Tank + Healer"


def test_healer_mixin_heals_target():
    healer = Paladin("Uther", level=5)
    target = Mage("Jaina", level=5)
    target.hp = 1
    new_hp = healer.heal(target)
    assert new_hp == 1 + healer.heal_power


def test_loggable_mixin_tracks_assignments():
    m = LoggedMage("Jaina", level=1)
    m.hp = 5
    assert any("hp = 5" in entry for entry in m.log)
