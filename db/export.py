"""Runs the four query series from queries.sql and exports each result to
CSV (tabular data) or JSON (schema introspection), ready to hand to the
HTML/CSS block.

Connection: copy `.env.example` (repo root) to `.env` and fill in your own
Postgres details (see seed.py for the full explanation) — no extra install
needed, and no need to set an environment variable by hand each session.
GUILDOPS_DSN must be set one way or the other; there's no hardcoded
fallback.
"""
from __future__ import annotations

import csv
import json
import os
from pathlib import Path

import psycopg2
import psycopg2.extras


def _load_dotenv(start: Path) -> None:
    """Minimal, dependency-free .env loader — see seed.py for details."""
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
        return


_load_dotenv(Path(__file__).resolve().parent)

DSN = os.environ.get("GUILDOPS_DSN")
if not DSN:
    raise SystemExit(
        "\nGUILDOPS_DSN isn't set.\n\n"
        "Copy .env.example to .env (same folder as this script) and fill "
        "in your own Postgres details, or set the GUILDOPS_DSN environment "
        "variable directly.\n"
    )
OUT = Path(__file__).resolve().parent.parent / "exports"
OUT.mkdir(exist_ok=True)


def export_csv(cur, query, params, filename):
    cur.execute(query, params or ())
    columns = [d.name for d in cur.description]
    rows = cur.fetchall()
    with open(OUT / filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)
    print(f"  {filename}: {len(rows)} rows")


def export_json(cur, query, params, filename):
    cur.execute(query, params or ())
    columns = [d.name for d in cur.description]
    rows = [dict(zip(columns, row)) for row in cur.fetchall()]
    with open(OUT / filename, "w") as f:
        json.dump(rows, f, indent=2, default=str)
    print(f"  {filename}: {len(rows)} rows")


def main():
    # options="-c lc_messages=C" protects anything *after* a successful
    # connection. It can't help if the connection itself is rejected (wrong
    # database, user, or password) — see seed.py for the full explanation
    # of why that specific failure mode needs its own handling below.
    try:
        conn = psycopg2.connect(DSN, options="-c lc_messages=C")
    except UnicodeDecodeError:
        raise SystemExit(
            "\nCould not connect to Postgres, and the server's rejection "
            "message itself couldn't be decoded (this happens on Windows "
            "when the OS locale isn't English).\n\n"
            "This almost always means one of:\n"
            "  1. The 'guildops' database doesn't exist yet -> createdb guildops\n"
            "  2. The user/role in DSN doesn't exist, or the password is wrong\n"
            "  3. Postgres isn't running\n\n"
            f"Current connection string (edit DSN in export.py, or set "
            f"GUILDOPS_DSN): {DSN}\n"
        )
    except psycopg2.OperationalError as exc:
        raise SystemExit(f"\nCould not connect to Postgres: {exc}\n")

    with conn.cursor() as cur:
        print("1. Roster JOIN")
        export_csv(cur, """
            SELECT c.id, c.name, c.role, c.level, c.hp, c.status, g.name AS guild_name
            FROM character c JOIN guild g ON g.id = c.guild_id
            ORDER BY c.id
        """, None, "roster.csv")

        print("2. KPIs")
        export_csv(cur, """
            SELECT g.name AS guild_name,
                   count(c.id) FILTER (WHERE c.status = 'active') AS active_count
            FROM guild g LEFT JOIN character c ON c.guild_id = g.id
            GROUP BY g.name ORDER BY g.name
        """, None, "kpi_active_count.csv")

        export_csv(cur, """
            SELECT c.name
            FROM character c
            LEFT JOIN character_achievement ca ON ca.character_id = c.id
            WHERE ca.character_id IS NULL
            ORDER BY c.name
        """, None, "kpi_zero_achievements.csv")

        export_csv(cur, """
            SELECT c.name, c.hp, c.level
            FROM character c WHERE c.hp < 30
            ORDER BY c.hp ASC
        """, None, "kpi_low_hp.csv")

        print("3. Status / tier lists")
        export_csv(cur, """
            SELECT name, status FROM character
            ORDER BY CASE status WHEN 'active' THEN 1 WHEN 'benched' THEN 2 WHEN 'retired' THEN 3 END, name
        """, None, "list_status.csv")

        print("3.1 Status / active character")
        export_csv(cur, """
            SELECT name, status FROM character
            WHERE status = 'active' OR status = 'benched'
            ORDER BY name
        """, None, 'list_active.csv')

        export_csv(cur, """
            SELECT title, tier FROM achievement
            ORDER BY CASE tier WHEN 'gold' THEN 1 WHEN 'silver' THEN 2 WHEN 'bronze' THEN 3 END, title
        """, None, "list_tier.csv")

        print("4. Schema introspection")
        export_json(cur, """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns WHERE table_name = 'character'
            ORDER BY ordinal_position
        """, None, "schema_columns.json")

        export_json(cur, """
            SELECT tc.constraint_name, tc.constraint_type, ccu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.constraint_column_usage ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.table_name = 'character'
            ORDER BY tc.constraint_type, ccu.column_name
        """, None, "schema_constraints.json")

        export_json(cur, """
            SELECT conname, pg_get_constraintdef(oid) AS definition
            FROM pg_constraint WHERE conrelid = 'character'::regclass AND contype = 'c'
        """, None, "schema_checks.json")

    conn.close()
    print("\nAll exports written to", OUT)


if __name__ == "__main__":
    main()