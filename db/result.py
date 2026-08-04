import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DB = os.environ["GUILDOPS_DSN"]

conn = psycopg2.connect(DB)
cur = conn.cursor()
cur.execute("""
SELECT
    c.id,
    c.name,
    g.name AS guild_name,
    c.role,
    c.level,
    c.hp,
    c.status
FROM character c
JOIN guild g
    ON c.guild_id = g.id
WHERE c.status = 'active'
ORDER BY c.name;
""")

for row in cur.fetchall():
    print(row)

cur.close()