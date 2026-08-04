import pytest

from guild.dungeon import dungeon_floors, guild_transaction


def test_dungeon_is_effectively_endless_until_retreat():
    log = []
    dungeon = dungeon_floors(log)

    encounter = next(dungeon)
    assert encounter["floor"] == 1

    # Advance through several floors without ever retreating.
    for _ in range(10):
        encounter = dungeon.send("continue")
    assert encounter["floor"] >= 4  # multiple floors have passed
    assert "Entering floor 1" in log


def test_dungeon_retreat_ends_generator_cleanly():
    log = []
    dungeon = dungeon_floors(log)
    next(dungeon)
    with pytest.raises(StopIteration):
        dungeon.send("retreat")
    assert any("retreats mid-floor" in line for line in log)
    assert "Party returns to town." in log
    assert "Dungeon generator closed." in log


def test_dungeon_close_triggers_cleanup_via_generator_exit():
    log = []
    dungeon = dungeon_floors(log)
    next(dungeon)
    dungeon.close()
    assert "Dungeon generator closed." in log


def test_guild_transaction_commits_on_success():
    treasury = {"gold": 100}
    with guild_transaction(treasury) as t:
        t["gold"] -= 30
    assert treasury["gold"] == 70


def test_guild_transaction_rolls_back_on_error():
    treasury = {"gold": 100}
    with pytest.raises(ValueError):
        with guild_transaction(treasury) as t:
            t["gold"] -= 30
            raise ValueError("insufficient permissions")
    assert treasury["gold"] == 100  # rolled back
