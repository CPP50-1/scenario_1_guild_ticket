# Guild Roster - reference package

This is the reference solution for both the OOP project and the SQL prep
block that follows it (`sql_prep.md`), combined into one repo.

## Structure

- `guild/` - the Python OOP package (models, fields, roster, items, quests,
  combat, dungeon, exceptions). Pure in-memory domain objects, no database
  access. This is what the Day 1–6 OOP project built.
- `tests/` - the OOP package's own test suite (48 tests).
- `db/`
  - `schema.sql` - the DDL: `guild` (1-N root) -> `character`, `achievement`
    <-> `character` (N-N via `character_achievement`, with `earned_at` as
    the relationship-owned attribute), `item` (owned by at most one
    character, `ON DELETE SET NULL`).
  - `seed.py` - seeds the database, iterating real `guild.roster.Roster`
    objects (not hand-written dicts), parameterized (`%s`) throughout,
    wrapped in one transaction, plus synthetic volume via
    `generate_series`.
  - `queries.sql` - the four query series from `sql_prep.md`, each
    commented with which part of the HTML/CSS block it feeds.
  - `export.py` - runs those four series and writes the results to
    `exports/`.
- `exports/` - the actual query outputs (CSV for tabular data, JSON for
  schema introspection), ready to hand to the HTML/CSS block.

## Setting up the database locally

```
createdb -U postgres guildops
psql -U postgres -d guildops -f db/schema.sql
python3 db/seed.py    # edit the DSN at the top of seed.py if needed
python3 db/export.py  # regenerates everything in exports/
```

## Running the Python test suite

```
pytest
```

## A note on where "the roster" lives

There are two representations of the same domain here, and they are NOT
wired together:

- `guild.roster.Roster` -> in-memory Python objects, from the OOP project.
- The `character` table in Postgres -> what the SQL block populated, and
  what `sql_prep.md` explicitly says is "most of what a light ORM needs to
  know about your schema" for what comes next.

