"""
This script is intended to be run from a command line.

First, the script collects input data from the user on desire filters,
and then calls the relevant methods for pulling the data in __main__.
"""
from bot.nav_bot import NavBot
import time

# Console input for filters
print("Please specify the desired parameters for the search:")
league = input("Select a league.\nOptions: (Premier League, LaLiga, Bundesliga, Serie A, UCL)\n")
season = input("For which season would you like to pull data?\nFormat: ('YY/YY')\n")
print("Select a data filter.")
print("Options: ('Detailed', 'Summary', 'Defence', 'Passing', 'Goalkeeper')" )
main_filter = input()
if main_filter == 'Detailed':
    print("Select venue.")
    home_away = input("Options: ('Overall', 'Home', 'Away')\n")
    print("Select age filter type.")
    age_filter_type = input("Options: ('All', 'More than', 'Equals', 'Less than')\n")
    if age_filter_type != 'All':
        player_age = int(input("Type in player age for age filter.\n"))
    else:
        player_age = None
    print("Select player positions. Type in as a comma-seperated list.")
    player_positions_input = input("Options: ('G','D','M','F')\n")
    player_position = player_positions_input.split(",")
    player_position = [position.strip() for position in player_position]
    print("Select a filter category.")
    filter_cat = input("Options: ('Attack', 'Defence', 'Passing', 'Goalkeeper', 'Other')\n")
    print("Select up to 5 subfilters. Type in as a comma-seperated list.")
    print("For options by filter category, see README.")
    sub_filter_list_input = input()
    sub_filter_list = sub_filter_list_input.split(",")
    sub_filter_list = [sub_filter.strip() for sub_filter in sub_filter_list]



def run():
    with NavBot() as bot:
        bot.open_page(league, season)
        if main_filter == 'Detailed':
            bot.set_detailed_filters(home_away=home_away, age_filter_type=age_filter_type,
                                     player_age=player_age, player_position=player_position,
                                     filter_cat=filter_cat, sub_filter_list=sub_filter_list)
            stat_dict = bot.establish_schema()
            stats_df = bot.scan_remaining_pages(stat_dict)
        else:
            stat_dict = bot.establish_schema(main_filter)
            stats_df = bot.scan_remaining_pages(stat_dict)
            
        save_time = time.strftime("%m-%d_%H%M")
        stats_df.to_csv(f"{league} - player_stats - {save_time}.csv")
        time.sleep(5)




if __name__ == '__main__':
    run()