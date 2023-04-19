"""
Script Docstring

Documentation for the calls made within the script

Prompts for filters:
If not detailed, go into an if clause, if detailed, go into the
else clause to get remaining filter specs
"""
from bot.nav_bot import NavBot

def run():
    with NavBot() as bot:
        bot.open_page()
        # bot.establish_schema()
        stat_dict = bot.establish_basic_schema("Goalkeeper")
        #bot.set_detailed_filters()
        stats_df = bot.scan_remaining_pages(stat_dict)


if __name__ == '__main__':
    run()