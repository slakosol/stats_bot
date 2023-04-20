import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service 
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import bot.constants as c
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
import pandas as pd


class NavBot(webdriver.Chrome):
    """
    An instance of a webdriver object to call Selenium methods on.

    Attributes
    ----------
    driver_path : str
        path to local driver instance

    Methods
    -------
    open_page () :
        opens a connection to the league's webpage, and selects
        the season of interest
        Args:
            league (str) : the league for which the data is to be retrieved
                (default is c.PL_PAGE_URL)
            season (str) : the season for which the data is to be retrieved
                (default is '21/22')

    establish_basic_schema (filter) :
        selects a preset filter type, pulls table headers as dictionary keys
        and row values as a lists for each column header
        Args:
            filter (str) : preset filter type for the table ("Summary", "Attack",
                "Defence", "Passing", "Goalkeeper") (default is None - constructs
                table schema based on columns already present)
        Returns:
            dict: dictionary of column headers as keys and row data as values

    set_detailed_filters(home_away) :
        selects a preset filter, pulls column headers of that data tables
        as dictionary keys, and stores row values in lists.    
        Args:
            home_away (str) : selects the home or away games, or both for the
                filter ("Overall", "Home", "Away") (default is "Overall")
            age_filter_type (str) : selects the age filter type ("All",
                "More than", "Equals", "Less than") (default is "All")
            player_age (int) : if age_filter_type is not None, then a player
                age must be specified (default is None)
            player_position (list of str) : list of desired positions to filter for
                (['G','D','M','F']) (default is ['G','D','M','F'])
            filter_cat (str) : broad category for subfilter selection 
                ("Attack", "Defence", "Passing", "Goalkeeper", "Other")
            sub_filter_list (list) : selects subfilters for each column of the table,
                limit 5 (for list of available subfilters see README)
                (default is ['Goals', 'Shots on target', 'Total shots', 'Rating'])

    scan_remaining_pages(defined_player_stat_dict) :
        takes in an established data schema from the establish_basic_schema() method,
        scans remaining pages of data into the dictionary, converts to pandas DataFrame,
        and saves to a local csv file
        Args:
            defined_player_stat_dict (dict) : dictionary which establishes the data
                schema for the remaining data to be pull from all pages
        Returns:
            pandas.DataFrame: DataFrame of column headers and row values from the
            scanned pages
    """

    def __init__(self, driver_path=r';B:\Code\Projects\Driver\chromedriver_win32'):
        """ driver_path (raw_string) : path to local webdriver """

        self.driver_path = driver_path
        os.environ['PATH'] += self.driver_path
        options = Options()
        options.add_argument('--ignore-certificate-errors')
        super(NavBot, self).__init__(service=Service(ChromeDriverManager().install()), options=options) # instantiates the webdriver.Chrome object
        self.implicitly_wait(5)
        self.maximize_window()
    


    def open_page(self, league="Premier League", season='21/22'):
        """ 
        Opens a connection to the league's webpage, and selects
        the season of interest

        Args:
            league (str) : the league for which the data is to be retrieved
            (default is c.PL_PAGE_URL)
            season (str) : the season for which the data is to be retrieved
            (default is '21/22')
        """
        league_dict = {
            "Premier League": c.PL_PAGE_URL,
            "LaLiga": c.LALIGA_PAGE_URL,
            "Bundesliga": c.BUNDESLIGA_PAGE_URL,
            "Serie A": c.SERIE_A_PAGE_URL,
            "UCL": c.UCL_PAGE_URL
        }
        self.get(league_dict[league])
        self.find_element(By.XPATH, f'//span[text()="{c.CURRENT_SEASON}"]').click()
        WebDriverWait(self, 20).until(EC.presence_of_element_located((By.XPATH, f'//li[text()="{season}"]')))
        self.find_element(By.XPATH, f'//li[text()="{season}"]').click()
        time.sleep(5)



    def establish_schema(self, main_filter=None):
        """
        Selects a preset filter, pulls column headers of that data tables
        as dictionary keys, and stores row values in lists.
        
        Args:
            main_filter (str) : preset filter type for the table ("Summary", "Attack",
                "Defence", "Passing", "Goalkeeper") (default is None - constructs
                table schema based on columns already present)

        Returns:
            dict: dictionary of column headers as keys and row data as values
        """

        # Selects relevant filter
        ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
        self.execute_script("window.scrollTo(0,1800)") # Serie A & LaLiga webpages are tempermental
        # and don't load the filters, even though they are on the page, a work around I found
        # is to scroll to the location of the filters
        if main_filter:
            WebDriverWait(self, 30).until(EC.presence_of_element_located((By.XPATH, f'//div[@class="sc-hLBbgP Hbif"]/button[@data-tabid="{main_filter.lower()}"]')))
            filter_btn = self.find_element(By.XPATH, f'//div[@class="sc-hLBbgP Hbif"]/button[@data-tabid="{main_filter.lower()}"]')
            filter_btn.click()

        # Pulls column headers into a list
        status = True
        header_ind = 4 # Team values start in the 4th table column
        header_names_list = []
        while status: # try to loop through to the next column of data
            try:
                get_header_name_el_id = f'//thead/tr/th[{str(header_ind)}]'
                get_header_name = self.find_element(By.XPATH, get_header_name_el_id).get_attribute('title')
                if get_header_name:
                    header_names_list.append(get_header_name)
                    header_ind += 1
            except:
                status = False

        header_names_list = ['Team', 'Name'] + header_names_list
        player_stat_dict = {}

        # Pulls row data as a list into a dictionary
        table_elements = self.find_element(By.XPATH, '//tbody').get_attribute('innerHTML')
        table_elements_count = table_elements.count('<tr>')
        num_table_elements = table_elements_count + 1
        for col_ind, col_name in enumerate(header_names_list):
            col_ind += 2 
            column_values = []
            if col_ind == 2 or col_ind == 3:
                for row_num in range(1, num_table_elements):
                    el_id = f'//tbody/tr[{str(row_num)}]/td[{str(col_ind)}]'
                    el = WebDriverWait(self, 15, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, el_id)))
                    col_val = self.find_element(By.XPATH, el_id).get_attribute('title')
                    column_values.append(col_val)
                    player_stat_dict[col_name] = column_values
            elif col_name == 'Rating':
                for row_num in range(1, num_table_elements):
                    el_id = f'//tbody/tr[{str(row_num)}]/td[{str(col_ind)}]/span'
                    el = WebDriverWait(self, 15, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, el_id)))
                    col_val = self.find_element(By.XPATH, el_id).get_attribute('innerHTML')
                    column_values.append(col_val)
                    player_stat_dict[col_name] = column_values
            else:
                for row_num in range(1, num_table_elements):
                    el_id = f'//tbody/tr[{str(row_num)}]/td[{str(col_ind)}]'
                    el = WebDriverWait(self, 15, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, el_id)))
                    col_val = self.find_element(By.XPATH, el_id).get_attribute('innerHTML')
                    column_values.append(col_val)
                    player_stat_dict[col_name] = column_values

        return player_stat_dict
    


    def set_detailed_filters(self, home_away='Overall', age_filter_type='All',
                            player_age=None, player_position=['G','D','M','F'],
                            filter_cat='Attack', sub_filter_list=['Goals', 'Shots on target', 'Total shots', 'Rating']):
        """
        Selects a preset filter, pulls column headers of that data tables
        as dictionary keys, and stores row values in lists.
        
        Args:
            home_away (str) : selects the home or away games, or both for the
                filter ("Overall", "Home", "Away") (default is "Overall")
            age_filter_type (str) : selects the age filter type ("All",
                "More than", "Equals", "Less than") (default is "All")
            player_age (int) : if age_filter_type is not None, then a player
                age must be specified (default is None)
            player_position (list of str) : list of desired positions to filter for
                (['G','D','M','F']) (default is ['G','D','M','F'])
            filter_cat (str) : broad category for subfilter selection 
                ("Attack", "Defence", "Passing", "Goalkeeper", "Other")
            sub_filter_list (list) : selects subfilters for each column of the table,
                limit 5 (for list of available subfilters see README)
                (default is ['Goals', 'Shots on target', 'Total shots', 'Rating'])

        """

        self.execute_script("window.scrollTo(0,1800)") # Serie A & LaLiga webpages are tempermental
        # and don't load the filters, even though they are on the page, a work around I found
        # is to scroll to the location of the filters
        WebDriverWait(self, 45).until(EC.presence_of_element_located((By.XPATH, f'//div[@class="sc-hLBbgP Hbif"]/button[text()="Detailed"]')))
        self.find_element(By.XPATH, f'//button[text()="Detailed"]').click()
        # Select home_away filter
        WebDriverWait(self, 30).until(EC.presence_of_element_located((By.XPATH, f'//div[@class="sc-dkrFOg goGQQW"]/button/span[text()="{home_away}"]')))
        home_away_btn = self.find_element(By.XPATH, f'//div[@class="sc-dkrFOg goGQQW"]/button/span[text()="{home_away}"]')
        home_away_btn.click()
        # Select age filter
        if age_filter_type != 'All':
            age_filter_type_el_id = f'//ul[@class="sc-hLBbgP dRtNhU"]/li[text()="{age_filter_type}"]'
            age_filter_dropdown = self.find_element(By.XPATH, '//div[@class="sc-hLBbgP hQYrtA"]/div[3]/div/div/button').click()
            WebDriverWait(self, 10).until(EC.presence_of_element_located((By.XPATH, age_filter_type_el_id)))
            age_dropdown_option = self.find_element(By.XPATH, age_filter_type_el_id).click()
            age_input_field = self.find_element(By.XPATH, '//input[@class="sc-hLBbgP liJFaS"]')       
            age_input_field.send_keys(player_age)
        
        # Select player positions
        positions = ['G','D','M','F']
        for position in positions:
            if position not in player_position:
                # WebDriverWait(self, 10).until(EC.visibility_of_element_located((By.XPATH, f'//div[text()="{position}"]')))
                self.find_element(By.XPATH, f'//label[@for="checkbox-{position}-undefined"]').click()

        # Uncheck all existing filters
        filter_exists = True
        while filter_exists:
            try:
                self.find_element(By.XPATH, '//button[@class="sc-bcXHqe gJZAMC"]').click()
            except:
                filter_exists = False
        
        # Selecting filters
        filter_dict = {
            "Attack": 1,
            "Defence": 2,
            "Passing": 3,
            "Goalkeeper": 4,
            "Other": 5
        }
        self.find_element(By.XPATH, f'//button[@class="sc-bcXHqe lfmpW"][{filter_dict[filter_cat]}]').click()

        for sub_filter in sub_filter_list:
            self.find_element(By.XPATH, f'//div[@class="sc-hLBbgP sc-eDvSVe gjJmZQ jaJHeQ"]/label/div/div/span[text()="{sub_filter}"]').click()

        # Apply filters
        self.find_element(By.XPATH, '//button[@class="sc-bcXHqe ewHKoF"]').click()



    def scan_remaining_pages(self, defined_player_stat_dict):
        """
        Takes in an established data schema from the establish_basic_schema() method,
        scans remaining pages of data into the dictionary, converts to pandas DataFrame,
        and saves to a local csv file.
        
        Args:
            defined_player_stat_dict (dict) : dictionary which establishes the data
                schema for the remaining data to be pull from all pages
        Returns:
            pandas.DataFrame: DataFrame of column headers and row values from the
            scanned pages
        """
        ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
        try:
            # element selector for a page with > 3 pages
            total_page_count = int(self.find_element(By.XPATH, '//div[@class="sc-hLBbgP sc-eDvSVe NWuJg hryjgv"]/div/button[3]/span').get_attribute('innerHTML'))
        except:
            try:
                # element selector for a page with <= 2 pages
                total_page_count = int(self.find_element(By.XPATH, '//div[@class="sc-hLBbgP sc-eDvSVe NWuJg hryjgv"]/div/button[2]/span').get_attribute('innerHTML'))
            except:
                player_stats = pd.DataFrame(defined_player_stat_dict)
                save_time = time.strftime("%m-%d_%H%M")
                player_stats.to_csv(f"player_stats - {save_time}.csv")
                return player_stats


        next_page_btn = self.find_element(By.XPATH, '//div[@class="sc-hLBbgP sc-eDvSVe NWuJg hryjgv"]/button[2]')
        next_page_btn.click()
        time.sleep(5)

        # Loops over each page of data, appending row values to lists
        for page in range(total_page_count - 1):
            table_elements = self.find_element(By.XPATH, '//tbody').get_attribute('innerHTML')
            table_elements_count = table_elements.count('<tr>')
            num_table_elements = table_elements_count + 1
            for col_ind, col_name in enumerate(defined_player_stat_dict.keys()):
                col_ind += 2
                if col_ind == 2 or col_ind == 3:
                    for row_num in range(1, num_table_elements):
                        el_id = f'//tbody/tr[{str(row_num)}]/td[{str(col_ind)}]'
                        el = WebDriverWait(self, 15, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, el_id)))
                        col_val = self.find_element(By.XPATH, el_id).get_attribute('title')
                        defined_player_stat_dict[col_name].append(col_val)
                elif col_name == 'Rating':
                    for row_num in range(1, num_table_elements):
                        el_id = f'//tbody/tr[{str(row_num)}]/td[{str(col_ind)}]/span'
                        el = WebDriverWait(self, 15, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, el_id)))
                        col_val = self.find_element(By.XPATH, el_id).get_attribute('innerHTML')
                        defined_player_stat_dict[col_name].append(col_val)
                else:
                    for row_num in range(1, num_table_elements):
                        el_id = f'//tbody/tr[{str(row_num)}]/td[{str(col_ind)}]'
                        el = WebDriverWait(self, 15, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, el_id)))
                        col_val = self.find_element(By.XPATH, el_id).get_attribute('innerHTML')
                        defined_player_stat_dict[col_name].append(col_val)
            
            next_page_btn = self.find_element(By.XPATH, '//div[@class="sc-hLBbgP sc-eDvSVe NWuJg hryjgv"]/button[2]')
            try:
                WebDriverWait(self, 15, ignored_exceptions=ignored_exceptions).until(EC.element_to_be_clickable(next_page_btn))
                next_page_btn.click()
            except:
                continue
        
        player_stats = pd.DataFrame(defined_player_stat_dict)
        return player_stats
