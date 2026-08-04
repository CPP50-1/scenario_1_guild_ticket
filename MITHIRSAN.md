# TICKET GLD-142

## Solution

The solution verified the existing *status* column in `db/schemas.sql`, implemented a matching `Status` enum as a `Character` instance attribute with a default value, added a query in `guild/Roster.py` to filter for active characters, created tests in `tests/test_roster.py`, and implemented an export in `db/export.py` that outputs to `exports/active_roster.csv`.
The implmentation uses the status field in both Python and SQL, ensuring the code reflects the database schema.
