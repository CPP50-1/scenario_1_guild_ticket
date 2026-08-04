"""Day 3, Dev A: a turn-based combat coroutine.

Combat is naturally a back-and-forth exchange, which is exactly what
generator.send() is for — this is one of the few genuinely natural use
cases for two-way generator communication, not a forced example.

Usage sketch:

    log = []
    fight = battle(character, log)
    state = next(fight)                # prime the generator
    state = fight.send("attack")       # player acts, generator advances
    state = fight.throw(AmbushError()) # simulate an interrupt mid-battle
    fight.close()                      # abandon the fight cleanly
"""
from __future__ import annotations

from typing import Dict, Generator, List

from .exceptions import GuildError
from .models import Character


class AmbushError(GuildError):
    """Raised into the battle generator to simulate a mid-fight ambush —
    exercises Generator.throw() specifically.
    """


def battle(
    character: Character,
    combat_log: List[str],
    enemy_name: str = "Goblin",
    enemy_hp: int = 30,
    enemy_attack: int = 5,
) -> Generator[Dict, str, None]:
    """A generator-based combat loop.

    Yields a dict snapshot of the current state after each turn, and
    receives the player's next action via .send("attack" | "heal" | "flee").

    `combat_log` is a list supplied by the caller (not returned) so its
    contents remain inspectable even after the generator is closed or
    exhausted — generator locals disappear once the frame ends.
    """
    combat_log.append(f"A wild {enemy_name} appears! ({enemy_hp} HP)")
    character_hp = character.hp

    try:
        while character_hp > 0 and enemy_hp > 0:
            action = yield {
                "character_hp": character_hp,
                "enemy_hp": enemy_hp,
                "enemy_name": enemy_name,
            }

            if action == "attack":
                damage = 10
                enemy_hp -= damage
                combat_log.append(f"{character.name} hits {enemy_name} for {damage}")
            elif action == "heal":
                healed = 8
                character_hp = min(character_hp + healed, character.base_hp * character.level)
                combat_log.append(f"{character.name} heals for {healed}")
            elif action == "flee":
                combat_log.append(f"{character.name} flees the battle")
                return
            else:
                combat_log.append(f"Unrecognized action: {action!r} (turn skipped)")

            if enemy_hp > 0:
                character_hp -= enemy_attack
                combat_log.append(f"{enemy_name} hits {character.name} for {enemy_attack}")

        outcome = "victory" if enemy_hp <= 0 else "defeat"
        combat_log.append(f"Battle ended: {outcome}")
        yield {"character_hp": character_hp, "enemy_hp": enemy_hp, "outcome": outcome}

    except AmbushError:
        # Demonstrates Generator.throw(): an exception injected at the
        # currently suspended yield point, handled like any other.
        character_hp -= 15
        combat_log.append(f"Ambush! {character.name} takes 15 damage")
        yield {"character_hp": character_hp, "enemy_hp": enemy_hp, "ambushed": True}

    finally:
        # Runs on natural completion, on `return` above, AND when the
        # caller calls .close() (which injects GeneratorExit at the
        # suspended yield point). No `yield` is allowed in here once
        # GeneratorExit is what triggered it — logging a plain side
        # effect is safe, yielding again is not.
        combat_log.append("Combat generator closed.")
