TLDR : Added an export query to a new file, no changes to existing code/results

First I checked how the "views" were working :

I first went into queries.sql, but none seemed relevant, so I checked export as we have a roster.csv that seems to be what the user have for now.

I saw in export that all the queries were there, separated by print by categories.

I then wondered if the client would prefer to change the current roster.csv or add a new one. 
In my opinion, for both cases it would have been best to have 2 queries as explained below :

- Here, as the client wanted, the old roster.csv stayed the same and I created roster_active.csv with the new query
- If the client wanted the new query as roster.csv, i'd have created a roster_all.csv with the old results.

The change in the SQL query was a simple condition `WHERE c.status = 'active'` to limit it to the active members only.

I did not add the file in the commit as it's created on export and the user needs to do it once to have his own results.