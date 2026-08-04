"""Seed script for the Guild Roster database.

- Only %s placeholders, never string concatenation / f-strings into a query.
- Iterates the real domain objects (guild/models.py, guild/items.py) via the
  container/iterator protocol built during the OOP part, rather than
  hand-writing disconnected SQL literals.
- Every insert another insert depends on captures its new id with RETURNING.
- The whole seed is wrapped in one transaction.

Connection: copy `.env.example` (repo root) to `.env` and fill in your own
Postgres details, e.g.:

    GUILDOPS_DSN=host=localhost dbname=guildops user=postgres password=yourpassword

`.env` is read automatically (no extra install needed) — no need to set an
environment variable by hand each session. An actual environment variable
named GUILDOPS_DSN, if already set, always takes priority over `.env`.
GUILDOPS_DSN must be set one way or the other — there's no hardcoded
fallback, since a silent default pointing at credentials that don't exist
on your machine is exactly what caused the confusing crash this replaced.
Either way, the database and role must already exist (createdb /
createuser, or your own existing Postgres user) before running this
script.
"""
from __future__ import annotations

import os
import random
import sys
from pathlib import Path


def _load_dotenv(start: Path) -> None:
    """Minimal, dependency-free .env loader. Looks for a `.env` file next
    to this script, then in the repo root, and sets os.environ from it —
    without ever overwriting a variable that's already set for real.
    """
    for candidate in (start / ".env", start.parent / ".env"):
        if not candidate.is_file():
            continue
        for line in candidate.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)
        return  # first .env found wins


_load_dotenv(Path(__file__).resolve().parent)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import psycopg2

from guild.models import Mage, Paladin, Rogue, Warrior
from guild.roster import Roster

DB_DSN = os.environ.get("GUILDOPS_DSN")
if not DB_DSN:
    raise SystemExit(
        "\nGUILDOPS_DSN isn't set.\n\n"
        "Copy .env.example to .env (same folder as this script) and fill "
        "in your own Postgres details, or set the GUILDOPS_DSN environment "
        "variable directly.\n"
    )

ACHIEVEMENTS = [
    ("First Blood", "bronze"),
    ("Iron Will", "silver"),
    ("Undefeated", "gold"),
    ("Dungeon Delver", "bronze"),
    ("Guild Legend", "gold"),
]

ITEM_NAMES = [
    ("Iron Sword", "common", 10),
    ("Steel Shield", "uncommon", 25),
    ("Ember Blade", "rare", 120),
    ("Dragon Scale Armor", "epic", 480),
    ("Crown of Ashfall", "legendary", 2000),
]


def build_roster() -> Roster:
    """The real domain objects, built through the OOP package — this is
    what gets iterated below, not a hand-rolled list of dicts.
    """
    roster = Roster()
    roster.add(Warrior("Grom", level=12))
    roster.add(Warrior("Thane", level=7))
    roster.add(Mage("Jaina", level=15))
    roster.add(Mage("Finn", level=3))
    roster.add(Rogue("Sly", level=9))
    roster.add(Rogue("Vex", level=22))
    roster.add(Paladin("Uther", level=18))
    roster.add(Paladin("Seris", level=1))
    return roster


# Deliberate, named status per character (mix of active/benched/retired) so
# the "filter by active" ticket has real, varied data to run against —
# rather than everyone conveniently being active.
STATUS_BY_NAME = {
    "Grom": "active",
    "Thane": "benched",
    "Jaina": "active",
    "Finn": "active",
    "Sly": "retired",
    "Vex": "active",
    "Uther": "benched",
    "Seris": "active",
}


def main():
    # options="-c lc_messages=C" forces plain English/ASCII server messages
    # for anything that happens *after* a successful connection. It cannot
    # help if the connection itself is rejected (wrong database, wrong user,
    # wrong password) — that rejection ("FATAL: ...") is sent by the server
    # before it ever processes session-level options from a failed
    # authentication attempt. On Windows, that FATAL text can be localized
    # to the OS codepage rather than UTF-8, which is what turns a plain
    # "wrong password" into an unreadable UnicodeDecodeError instead. The
    # try/except below turns that back into an actionable message.
    try:
        conn = psycopg2.connect(DB_DSN, options="-c lc_messages=C")
    except UnicodeDecodeError:
        raise SystemExit(
            "\nCould not connect to Postgres, and the server's rejection "
            "message itself couldn't be decoded (this happens on Windows "
            "when the OS locale isn't English).\n\n"
            "This almost always means one of:\n"
            "  1. The 'guildops' database doesn't exist yet -> createdb guildops\n"
            "  2. The user/role in DB_DSN doesn't exist, or the password is wrong\n"
            "  3. Postgres isn't running\n\n"
            f"Current connection string (edit DB_DSN in seed.py, or set "
            f"GUILDOPS_DSN): {DB_DSN}\n"
        )
    except psycopg2.OperationalError as exc:
        raise SystemExit(f"\nCould not connect to Postgres: {exc}\n")

    try:
        with conn:
            with conn.cursor() as cur:
                # Safe to re-run: clear any previous seed data first, rather
                # than relying on nobody ever running this twice. Re-running
                # without this was exactly what surfaced the Windows/locale
                # bug above, via a duplicate-key error on the second run.
                cur.execute(
                    "TRUNCATE guild, character, achievement, character_achievement, item "
                    "RESTART IDENTITY CASCADE"
                )
                # --- guild (1-N root) -------------------------------------
                cur.execute(
                    "INSERT INTO guild (name, founded_on) VALUES (%s, %s) RETURNING id",
                    ("Ashfall Company", "2024-03-01"),
                )
                guild_id = cur.fetchone()[0]

                # A second guild with no active members at all — this is what
                # makes the "active count per guild" KPI query need a LEFT
                # JOIN rather than a plain JOIN: without it, this guild simply
                # wouldn't appear in the result instead of showing up at 0.
                cur.execute(
                    "INSERT INTO guild (name, founded_on) VALUES (%s, %s) RETURNING id",
                    ("Embercrest Vanguard", "2023-11-20"),
                )
                empty_guild_id = cur.fetchone()[0]
                cur.execute(
                    "INSERT INTO character (guild_id, name, role, level, hp, status) VALUES (%s,%s,%s,%s,%s,%s)",
                    (empty_guild_id, "Old Marrow", "Warrior", 40, 5, "retired"),
                )

                # --- characters, iterated from the real Roster object ----
                character_ids = {}
                for character in build_roster():
                    cur.execute(
                        """
                        INSERT INTO character (guild_id, name, role, level, hp, status)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (
                            guild_id,
                            character.name,
                            type(character).__name__,
                            character.level,
                            character.hp,
                            STATUS_BY_NAME[character.name],
                        ),
                    )
                    character_ids[character.name] = cur.fetchone()[0]

                # --- achievements ------------------------------------------
                achievement_ids = {}
                for title, tier in ACHIEVEMENTS:
                    cur.execute(
                        "INSERT INTO achievement (title, tier) VALUES (%s, %s) RETURNING id",
                        (title, tier),
                    )
                    achievement_ids[title] = cur.fetchone()[0]

                # --- character_achievement (N-N, with earned_at) -----------
                # Deliberately uneven: some characters have several, some
                # (Thane, Finn) have none at all — this is what the "characters
                # with zero achievements" KPI query is for.
                earned = [
                    ("Grom", "First Blood", "2024-04-02"),
                    ("Grom", "Iron Will", "2024-06-15"),
                    ("Jaina", "First Blood", "2024-04-02"),
                    ("Jaina", "Undefeated", "2024-09-10"),
                    ("Vex", "Dungeon Delver", "2024-05-20"),
                    ("Uther", "Guild Legend", "2024-11-01"),
                    ("Uther", "Iron Will", "2024-06-15"),
                    ("Seris", "First Blood", "2025-01-05"),
                ]
                for char_name, ach_title, earned_at in earned:
                    cur.execute(
                        """
                        INSERT INTO character_achievement (character_id, achievement_id, earned_at)
                        VALUES (%s, %s, %s)
                        """,
                        (character_ids[char_name], achievement_ids[ach_title], earned_at),
                    )

                # --- items: some owned, some sitting unclaimed -------------
                random.seed(7)
                owned_names = list(character_ids)
                for name, rarity, value in ITEM_NAMES:
                    owner = random.choice(owned_names + [None, None])  # some unclaimed
                    owner_id = character_ids[owner] if owner else None
                    cur.execute(
                        "INSERT INTO item (owner_character_id, name, rarity, value) VALUES (%s, %s, %s, %s)",
                        (owner_id, name, rarity, value),
                    )

                # --- synthetic volume: enough rows for pagination/filtering
                # to be non-trivial later, via generate_series -------------
                cur.execute(
                    """
                    INSERT INTO character (guild_id, name, role, level, hp, status)
                    SELECT
                        %s,
                        'Recruit #' || gs,
                        (ARRAY['Warrior','Mage','Rogue','Paladin'])[1 + (gs %% 4)],
                        1 + (gs %% 30),
                        10 + (gs %% 50),
                        (ARRAY['active','active','active','benched','retired'])[1 + (gs %% 5)]
                    FROM generate_series(1, 40) AS gs
                    """,
                    (guild_id,),
                )

        print("Seed complete.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()