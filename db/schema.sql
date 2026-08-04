-- Guild Roster Database — schema.sql
-- One CREATE TABLE per entity, one junction table for the N-N relation,
-- explicit ON DELETE choice + FK index on every foreign key.

-- --------------------------------------------------------------------------
-- guild : the 1-N root. A guild holds many characters.
-- --------------------------------------------------------------------------
CREATE TABLE guild (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    founded_on  DATE NOT NULL,
    CONSTRAINT guild_name_key UNIQUE (name)
);

-- --------------------------------------------------------------------------
-- character : belongs to exactly one guild (1-N child).
--
-- role   -> categorical, fixed list (mirrors the Warrior/Mage/Rogue/Paladin
--           subclasses in guild/models.py).
-- status -> categorical, fixed list, DELIBERATELY more than two values.
--           "active" is not simply true/false here — a character can be
--           active, benched (still a member, not currently deployed) or
--           retired. Filtering "by status" therefore still requires a
--           decision about which values count as "active", exactly like a
--           real membership system.
--
-- ON DELETE CASCADE: if a guild is deleted, its characters go with it —
-- there's no such thing as a character without a guild in this domain.
-- --------------------------------------------------------------------------
CREATE TABLE character (
    id         SERIAL PRIMARY KEY,
    guild_id   INTEGER NOT NULL REFERENCES guild(id) ON DELETE CASCADE,
    name       VARCHAR(50) NOT NULL,
    role       VARCHAR(10) NOT NULL
               CHECK (role IN ('Warrior', 'Mage', 'Rogue', 'Paladin')),
    level      INTEGER NOT NULL CHECK (level BETWEEN 1 AND 100),
    hp         INTEGER NOT NULL CHECK (hp >= 0),
    status     VARCHAR(10) NOT NULL DEFAULT 'active'
               CHECK (status IN ('active', 'benched', 'retired')),
    CONSTRAINT character_guild_id_name_key UNIQUE (guild_id, name)
);

CREATE INDEX idx_character_guild_id ON character(guild_id);

-- --------------------------------------------------------------------------
-- achievement : tier is categorical, fixed list.
-- --------------------------------------------------------------------------
CREATE TABLE achievement (
    id     SERIAL PRIMARY KEY,
    title  VARCHAR(100) NOT NULL,
    tier   VARCHAR(10) NOT NULL CHECK (tier IN ('bronze', 'silver', 'gold')),
    CONSTRAINT achievement_title_key UNIQUE (title)
);

-- --------------------------------------------------------------------------
-- character_achievement : N-N junction. A character can earn several
-- achievements; the same achievement can be earned by several characters.
--
-- earned_at is relationship-owned: it belongs to the (character,
-- achievement) pairing itself, not to either side alone — a column here,
-- not on character or achievement.
--
-- ON DELETE CASCADE on both FKs: an earned-achievement record only makes
-- sense in the context of both rows existing; if either is deleted, the
-- join record has nothing left to describe.
-- --------------------------------------------------------------------------
CREATE TABLE character_achievement (
    character_id    INTEGER NOT NULL REFERENCES character(id) ON DELETE CASCADE,
    achievement_id  INTEGER NOT NULL REFERENCES achievement(id) ON DELETE CASCADE,
    earned_at       DATE NOT NULL DEFAULT CURRENT_DATE,
    PRIMARY KEY (character_id, achievement_id)
);

CREATE INDEX idx_character_achievement_character_id ON character_achievement(character_id);
CREATE INDEX idx_character_achievement_achievement_id ON character_achievement(achievement_id);

-- --------------------------------------------------------------------------
-- item : belongs to at most one character (1-N child), or sits unclaimed
-- in the guild vault (owner_character_id IS NULL).
--
-- rarity -> categorical, fixed list (mirrors guild/items.py's Rarity IntEnum).
--
-- ON DELETE SET NULL (not CASCADE): if a character is deleted, their items
-- don't vanish — they fall back into the shared, unclaimed loot pool. This
-- is a deliberately different choice from the two CASCADEs above, worth
-- contrasting out loud: an item has a life of its own independent of who
-- (if anyone) currently holds it.
-- --------------------------------------------------------------------------
CREATE TABLE item (
    id                 SERIAL PRIMARY KEY,
    owner_character_id INTEGER REFERENCES character(id) ON DELETE SET NULL,
    name               VARCHAR(50) NOT NULL,
    rarity             VARCHAR(10) NOT NULL
                       CHECK (rarity IN ('common', 'uncommon', 'rare', 'epic', 'legendary')),
    value              INTEGER NOT NULL CHECK (value >= 0)
);

CREATE INDEX idx_item_owner_character_id ON item(owner_character_id);
