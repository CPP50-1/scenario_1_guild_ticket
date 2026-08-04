-- Guild Roster Database — queries.sql
-- Four series, each one feeding a specific part of the HTML/CSS block.

-- ============================================================================
-- 1. Full roster — JOIN across the 1-N relation (guild -> character)
--    Feeds: semantic refactor of the roster table (+ Flexbox/Grid)
-- ============================================================================
SELECT
    c.id,
    c.name,
    c.role,
    c.level,
    c.hp,
    c.status,
    g.name AS guild_name
FROM character c
JOIN guild g ON g.id = c.guild_id
ORDER BY c.id;


-- ============================================================================
-- 2. KPI-style aggregates — one query per KPI
--    Feeds: dashboard layout + SCSS theme, built together
-- ============================================================================

-- 2a. Active character count per guild (LEFT JOIN so a guild with zero
--     active characters still appears, at 0 — not silently dropped).
SELECT
    g.name AS guild_name,
    count(c.id) FILTER (WHERE c.status = 'active') AS active_count
FROM guild g
LEFT JOIN character c ON c.guild_id = g.id
GROUP BY g.name
ORDER BY g.name;

-- 2b. Characters with zero achievements (anti-join via LEFT JOIN ... IS NULL).
SELECT c.name
FROM character c
LEFT JOIN character_achievement ca ON ca.character_id = c.id
WHERE ca.character_id IS NULL
ORDER BY c.name;

-- 2c. Low-HP alert: characters below a flat safety threshold.
SELECT c.name, c.hp, c.level
FROM character c
WHERE c.hp < 30
ORDER BY c.hp ASC;


-- ============================================================================
-- 3. Status / tier lists — entity + category together, custom-ranked
--    Feeds: SCSS state-based styling (rarity/status -> visual)
-- ============================================================================

-- 3a. Characters by status, with 'active' ranked first on purpose
--     (it deserves the most attention in the UI).
SELECT name, status
FROM character
ORDER BY
    CASE status
        WHEN 'active'  THEN 1
        WHEN 'benched' THEN 2
        WHEN 'retired' THEN 3
    END,
    name;

-- 3b. Achievements by tier, gold first (natural alphabetical order would
--     give bronze/gold/silver — CASE lets us choose the order ourselves).
SELECT title, tier
FROM achievement
ORDER BY
    CASE tier
        WHEN 'gold'   THEN 1
        WHEN 'silver' THEN 2
        WHEN 'bronze' THEN 3
    END,
    title;


-- select only active characters

SELECT name
FROM character
WHERE status != 'retired'
ORDER BY name;

-- ============================================================================
-- 4. Schema introspection — 3 queries, against the `character` table
--    Feeds: Bootstrap form where every field mirrors a real constraint
-- ============================================================================

-- 4a. Columns, types, nullability, defaults (information_schema — ANSI standard).
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'character'
ORDER BY ordinal_position;

-- 4b. Constraints overview: PK, FK, CHECK, UNIQUE on the table.
--     constraint_column_usage (not key_column_usage) is what's needed here —
--     key_column_usage only covers PK/FK/UNIQUE and silently drops CHECK
--     constraints from the result entirely.
SELECT
    tc.constraint_name,
    tc.constraint_type,
    ccu.column_name
FROM information_schema.table_constraints tc
JOIN information_schema.constraint_column_usage ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.table_name = 'character'
ORDER BY tc.constraint_type, ccu.column_name;

-- 4c. The actual allowed values behind each CHECK constraint — this text
--     only lives in Postgres's own catalog (pg_constraint), not in the
--     ANSI-standard information_schema views, which only tell you a CHECK
--     exists, not what it checks.
SELECT
    conname,
    pg_get_constraintdef(oid) AS definition
FROM pg_constraint
WHERE conrelid = 'character'::regclass
  AND contype = 'c';
