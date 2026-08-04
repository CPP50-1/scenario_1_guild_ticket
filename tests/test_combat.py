import pytest

from guild.combat import AmbushError, battle
from guild.models import Warrior


def test_battle_priming_and_send():
    w = Warrior("Grom", level=3)  # hp = 45
    log = []
    fight = battle(w, log, enemy_name="Goblin", enemy_hp=15, enemy_attack=1)

    state = next(fight)  # prime
    assert state["enemy_hp"] == 15

    state = fight.send("attack")
    assert state["enemy_hp"] == 5  # 15 - 10
    assert "hits Goblin" in log[-2] or any("hits Goblin" in line for line in log)


def test_battle_flee_ends_generator():
    w = Warrior("Grom", level=3)
    log = []
    fight = battle(w, log, enemy_hp=999)  # unwinnable, forces a flee
    next(fight)
    with pytest.raises(StopIteration):
        fight.send("flee")
    assert any("flees" in line for line in log)
    assert "Combat generator closed." in log


def test_battle_throw_ambush():
    w = Warrior("Grom", level=3)
    log = []
    fight = battle(w, log, enemy_hp=999)
    next(fight)
    state = fight.throw(AmbushError())
    assert state["ambushed"] is True
    assert any("Ambush!" in line for line in log)


def test_battle_close_runs_finally():
    w = Warrior("Grom", level=3)
    log = []
    fight = battle(w, log, enemy_hp=999)
    next(fight)
    fight.close()
    assert "Combat generator closed." in log
