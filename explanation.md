Guild ticket assignment by Mickael

I noticed in list_status.csv and in roster.csv that "status" was a field that exists there.
However, that field doesn't exist in the Python code that creates a Character.

I then found this in the schema of the database, which explains what the field is and how it works:
-- status -> categorical, fixed list, DELIBERATELY more than two values.
--           "active" is not simply true/false here — a character can be
--           active, benched (still a member, not currently deployed) or
--           retired. Filtering "by status" therefore still requires a
--           decision about which values count as "active", exactly like a
--           real membership system.

Therefore, I chose to add a status attribute to the Character class in models.py, with a default as 'active'.
I then added a method into roster.py that simply returns a list of Characters based on whether that attribute reads 'active' through a list comprehension instruction.

The test I added in test_roster.py seems to work:
active_one receives 'active' by default from how I adapted the signature of the Character class;
active_two receives 'active' by direct attribution in the test;
inactive_one and inactive_two receive different statuses.
The test asserts that only active_one and active_two should be returned, and the test runs successfully.