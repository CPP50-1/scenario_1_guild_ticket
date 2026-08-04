A short explanation in a .md file with your name of which solution you choose and why.

I'm assuming Coaches use the csv files to pull up info from db.
I created a new query in the export.py file that creates a new csv file named filtered_roster(actives).csv, which shows
only active and benched characters per guild.

For that, I modified the following files:
    - export.py:
            ADDED : 
                export_csv(cur, """
                        SELECT c.id, c.name, c.role, c.level, c.hp, c.status, g.name AS guild_name
                        FROM character c JOIN guild g ON g.id = c.guild_id
                        WHERE c.status <> 'retired'
                        ORDER BY c.id
                    """, None, "filtered_roster(actives).csv")
