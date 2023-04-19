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
        opens connection to the webpage

    establish_basic_schema (filter) :
        selects a preset filter type, pulls table headers as dictionary keys
        and row values as a lists for each column header
        Args:
            filter (str) : preset filter type for the table ("Summary", "Attack",
                "Defence", "Passing", "Goalkeeper") (default is "Summary")
        Returns:
            dict: dictionary of column headers as keys and row data as values

    set_detailed_filters(home_away) :
        in progress...

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
    


    def open_page(self):
        """ Opens a connection to the website. """

        self.get(c.PL_PAGE_URL)
        time.sleep(5)



    def establish_basic_schema(self, filter="Summary"):
        """
        Selects a preset filter, pulls column headers of that data tables
        as dictionary keys, and stores row values in lists.
        
        Args:
            filter (str) : preset filter type for the table ("Summary", "Attack",
                "Defence", "Passing", "Goalkeeper") (default is "Summary")

        Returns:
            dict: dictionary of column headers as keys and row data as values
        """

        # Selects relevant filter
        ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
        filter_btn = self.find_element(By.XPATH, f'//div[@class="sc-hLBbgP Hbif"]/button[text()="{filter}"]')
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
    

    def set_detailed_filters(self, home_away='Home'):
        """
        In progress...
        """
        self.find_element(By.XPATH, f'//div[@class="sc-hLBbgP Hbif"]/button[text()="Detailed"]').click()
        home_away_btn = self.find_element(By.XPATH, f'//div[@class="sc-dkrFOg goGQQW"]/button/span[text()="{home_away}"]')
        home_away_btn.click()


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
                print("Only one page of data exists.")

        next_page_btn = self.find_element(By.XPATH, '//div[@class="sc-hLBbgP sc-eDvSVe NWuJg hryjgv"]/button[2]')
        next_page_btn.click()
        time.sleep(5)

        # Loops over each page of data, appending row values to lists
        for page in range(total_page_count - 2):
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
            WebDriverWait(self, 15, ignored_exceptions=ignored_exceptions).until(EC.element_to_be_clickable(next_page_btn))
            next_page_btn.click()
        
        player_stats = pd.DataFrame(defined_player_stat_dict)
        save_time = time.strftime("%m-%d_%H%M")
        player_stats.to_csv(f"player_stats - {save_time}.csv")
        return player_stats
