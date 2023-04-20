=================
### stats_bot ###
=================

A browser bot built using the Selenium package in Python to navigate
sofascore.com to scrape the website for player statistics, flipping through
all the pages of data (updated with API calls and thus unavailable) in plain
HTML all at once (otherwise a beautifulsoup scrape would have been sufficient),
and apply various filters to select different statistics.The project will
aggregate the data into a pandas dataframe, and save the results
on a local PostgreSQL server.


Major file components and directories:

1. run.py - contains the main executable script
2. bot (directory) - contains the classes and methods
	associated with navigating the webpage, and pulling
	the data
3. data (directory) - contains the code for saving the data into
	a pandas dataframe and to a local PostgreSQL server.


# TODO: ***finish documentation for new method*** (then make commit)
- Write input methods for detailed filters (documentation)
- Decide on the kind of data im pulling
- Load data into PostgreSQL
- Build a new, enhanced table with AGG funcs
- Load table back into Python
- Do some data visualization (comp on AGG funcs within PL clubs 
and some cross league comps)


if Serie A and LaLiga establish schema ever works, change the method
selector in detailed filter too