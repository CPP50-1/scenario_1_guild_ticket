"""The core Character model: metaclass-based registry (Day 5), full dunder
set (Day 1), and a deliberate mixin/MRO conflict resolved via cooperative
super() (Day 4).
"""

from __future__ import annotations

from typing import Dict, Type
from enum import Enum

from .fields import IntField, StringField


class GuildMeta(type):
    """Metaclass that automatically registers every concrete Character
    subclass by name — direct analogue of how Odoo's ORM collects model
    classes (via `_name`) into its model registry at class-creation time,
    not at instantiation time.

    Also enforces validation *at class-definition time*: every concrete
    subclass must provide a `base_hp` (an int), or the class body itself
    fails to evaluate. This is the second workshop target for Day 5
    ("validation at class-definition time — e.g. enforce required class
    attributes").

    Note: `__init_subclass__` is the more modern, lighter-weight way to
    achieve simple cases of this (see the Day 5 theory point) — we use a
    full metaclass here specifically because the registry needs to exist
    *before* any instances are created, and because this is the mechanism
    Odoo itself actually uses, which is the point of the exercise.
    """

    registry: Dict[str, Type["Character"]] = {}

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        if bases:  # skip the base Character class itself (bases == ())
            base_hp = getattr(cls, "base_hp", None)
            if not isinstance(base_hp, int):
                raise TypeError(
                    f"{name} must define an int 'base_hp' class attribute "
                    f"(directly or via inheritance), got {base_hp!r}"
                )
            GuildMeta.registry[name] = cls
        return cls


class Status(Enum):
    ACTIVE = 1
    BENCHED = 2
    RETIRED = 3


class Character(metaclass=GuildMeta):
    """Base class for every playable character.

    Uses Validated descriptors (Day 4) for its fields rather than manual
    `if not isinstance(...)` checks in __init__ — this is the payoff for
    the tedious hand-written validation trainees hit on the pre-project
    afternoon.
    """

    name = StringField(max_length=50)
    hp = IntField(minimum=0)
    level = IntField(minimum=1, maximum=100)

    base_hp: int = 10  # overridden by every concrete subclass; enforced by GuildMeta

    def __init__(self, name: str, level: int = 1, status: Status = Status.ACTIVE):
        self.name = name
        self.level = level
        self.hp = self.base_hp * level
        self.status = status

    def describe_role(self) -> str:
        return "Adventurer"

    # --- Day 1 dunder set -------------------------------------------------

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self.name!r}, level={self.level}, hp={self.hp})"

    def __str__(self) -> str:
        return f"{self.name} the {type(self).__name__} (Lv.{self.level}, {self.hp} HP)"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Character):
            return NotImplemented
        return (type(self), self.name, self.level) == (
            type(other),
            other.name,
            other.level,
        )

    def __hash__(self) -> int:
        return hash((type(self), self.name, self.level))

    def __lt__(self, other: object) -> bool:
        # Ordering by level lets a Roster be sorted() directly (Day 2).
        if not isinstance(other, Character):
            return NotImplemented
        return self.level < other.level

    def __bool__(self) -> bool:
        # A character is "truthy" while alive.
        return self.hp > 0


class Warrior(Character):
    base_hp = 15

    def describe_role(self) -> str:
        return "Warrior"


class Mage(Character):
    base_hp = 8

    def describe_role(self) -> str:
        return "Mage"


class Rogue(Character):
    base_hp = 10

    def describe_role(self) -> str:
        return "Rogue"


# --- Day 4 mixins: horizontal reuse without deep inheritance ---------------


class HealerMixin:
    """Adds healing behavior. Deliberately participates in the
    describe_role() cooperative chain (see Paladin below) rather than
    overriding it outright.
    """

    heal_power: int = 5

    def describe_role(self) -> str:
        return super().describe_role() + " + Healer"

    def heal(self, target: "Character", amount: int = None) -> int:
        amount = self.heal_power if amount is None else amount
        target.hp = min(target.hp + amount, target.base_hp * target.level)
        return target.hp


class TankMixin:
    """Adds taunt/aggro behavior. Also participates cooperatively in
    describe_role() — see the MRO note on Paladin.
    """

    taunt_radius: int = 3

    def describe_role(self) -> str:
        return super().describe_role() + " + Tank"

    def taunt(self, enemies) -> list:
        # Simplified placeholder: in a real combat system this would
        # redirect enemy targeting. Kept intentionally simple — the point
        # of this exercise is the mixin/MRO mechanism, not combat balance.
        return list(enemies)


class Paladin(HealerMixin, TankMixin, Warrior):
    """The deliberate mixin conflict (Day 4, Dev C).

    Both HealerMixin and TankMixin define describe_role(), and both call
    super().describe_role() cooperatively rather than hard-coding a
    return value. C3 linearization for this class is:

        Paladin -> HealerMixin -> TankMixin -> Warrior -> Character -> object

    (Confirm with Paladin.__mro__ at the workshop — don't just take this
    comment's word for it.)

    Calling paladin.describe_role() therefore resolves as:
        HealerMixin.describe_role()   -> super() call goes to TankMixin
        TankMixin.describe_role()     -> super() call goes to Warrior
        Warrior.describe_role()       -> returns "Warrior" (chain ends here)
        ... TankMixin appends        -> "Warrior + Tank"
        ... HealerMixin appends      -> "Warrior + Tank + Healer"

    Trainees should explain *why* the order (Healer, Tank, Warrior) in the
    class declaration produces this specific chain, and what would change
    if TankMixin were listed before HealerMixin.
    """

    base_hp = 20


# --- Day 4 (Dev B): an independent mixin, not part of the conflict above ---


class LoggableMixin:
    """Logs every attribute assignment on the instance. Independent of the
    Healer/Tank conflict above — this mixin is meant to be combined with
    any Character subclass on its own, to show a *clean* mixin (no MRO
    conflict) alongside the deliberately conflicting one.

    Deliberately reads/writes self.__dict__ directly (not through
    getattr/setattr) inside __setattr__ to avoid infinite recursion — a
    common first mistake worth hitting once in review.
    """

    def __init__(self, *args, **kwargs):
        self.__dict__["_log"] = []
        super().__init__(*args, **kwargs)

    def __setattr__(self, name: str, value) -> None:
        log = self.__dict__.get("_log")
        if log is not None and name != "_log":
            log.append(f"{name} = {value!r}")
        super().__setattr__(name, value)

    @property
    def log(self) -> list:
        return list(self._log)


class LoggedMage(LoggableMixin, Mage):
    """Demo combination used by the test suite / workshop walkthrough."""
