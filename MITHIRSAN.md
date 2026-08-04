# TICKET GLD-142

## Solution

1. Looked into `db/schemas.sql`, find out status already exist in characters;
1. `Status` enum matching that schema, so `Character` can have an instance attribut realted to his status;
1. Status added to `Character.__init__` with default value;
1. Query into `guild/Roaster.py` to retrive all *active* character from roster;
1. New test into `tests/test_roatser`.
