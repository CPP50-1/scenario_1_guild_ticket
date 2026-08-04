# Active Characters Query

## Solution

The solution to this ticket is in **`db/result.py`**.

It connects to the database (reusing the same `GUILDOPS_DSN` / `.env`
setup as `seed.py`) and runs:

```sql
SELECT * FROM character WHERE status = 'active'
```
to show actives members (characters) in the roster

I display the result in the console, you just have to run the file **`db/result.py`**
## Possible improvements

For the sake of this ticket, the query is run directly in a single
script. In a larger codebase, it would be cleaner to introduce:

- A **repository** layer (e.g. `CharacterRepository`) responsible for
  all SQL related to the `character` table, so the query logic isn't
  scattered across scripts.
- A **service** layer (e.g. `CharacterService`) that calls the
  repository method.