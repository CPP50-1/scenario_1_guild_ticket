# Ticket #GLD-142: Active Roster Filter
**Developer:** Théophile

## Solution Chosen
1. **SQL/Exports:** Updated the database queries and `export.py` to generate a pre-filtered `active_roster.csv` containing only characters where `status != 'retired'`.
2. **OOP Domain:** Added a `status` field to the `Character` model and introduced an `active_characters()` generator method to the `Roster` class to mirror the database logic.
3. **Tests:** Verified that all 48 existing tests continue to pass.

## Why this approach?
* **Business Logic:** The Product Owner clarified that an "active" member is specifically someone who is "not retired." The filtering logic (`status != 'retired'`) safely includes both 'active' and 'benched' members, fulfilling the business requirement.
* **Database Efficiency:** I chose server-side/database filtering (outputting a focused CSV) rather than sending the full roster and filtering on the client side. This keeps the data payload small and fetching times fast, which will scale much better if the guild roster grows to thousands of records. 
* **Domain Sync:** Adding the generator to the Python `Roster` class ensures our in-memory domain objects remain feature-equivalent to our database capabilities.