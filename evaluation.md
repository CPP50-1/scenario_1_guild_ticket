Added a filter in the roster query to allow filters on c.status

Added a new export method to export results to active_characters_roster.csv
This method uses the new roster query and looks for c.status = 'active'