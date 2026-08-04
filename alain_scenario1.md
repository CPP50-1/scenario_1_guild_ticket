Scenario 1 'Active Members' ticket
----------------------------------

Clarification: An active member is one whose status is 'active' or 'benched' (character status can be 'active', 'benched', 'retired').

Solution: Added an sql query similar to the "Full roster" query but that will filter on status IN ('active', 'benched')
Query tested OK on a local database.

This is deemed sufficient at this stage, so no python code modification needed.
All tests passed.
