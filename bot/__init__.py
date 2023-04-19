"""
nav_bot

Contains the NavBot class for the webdriver object and
the relevant methods for filtering and pulling the data
from the webpage into a pandas DataFrame.

Classes:
  NavBot: An instance of a webdriver object to call Selenium methods on

Methods:
  establish_basic_schema (filter) :
        selects a preset filter type, pulls table headers as dictionary keys
        and row values as a lists for each column header

    set_detailed_filters(home_away) :
        in progress...

    scan_remaining_pages(defined_player_stat_dict) :
        takes in an established data schema from the establish_basic_schema() method,
        scans remaining pages of data into the dictionary, converts to pandas DataFrame,
        and saves to a local csv file
"""