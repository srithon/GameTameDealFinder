from time import sleep, time

#  import pickle
import traceback

import os

from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common import desired_capabilities

import logging

from collections import defaultdict  # https://stackoverflow.com/questions/11236006/identify-duplicate-values-in-a-list-in-python





log_formatter = logging.Formatter('%(asctime)s %(levelname)s:%(name)s\t%(message)s',
                                  datefmt='%H:%M:%S')

log_handler = logging.FileHandler(filename='gametame_fetch_items.log')
log_handler.setFormatter(log_formatter)

log_handler.setLevel(logging.DEBUG)

#  logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger('root_logger')

#  logging.getLogger('')
logger.addHandler(log_handler)

logger.setLevel(logging.DEBUG)

logger.info('Starting script...')

handler = None

item_list = list()
point_price_list = list()

firefox_profile = webdriver.FirefoxProfile()
firefox_profile.set_preference("browser.privatebrowsing.autostart", True)
firefox_profile.set_preference('permissions.default.stylesheet', 2)
# Disable images
firefox_profile.set_preference('permissions.default.image', 2)
# Disable Flash
firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so',
                               'false')
firefox_profile.set_preference('javascript.enabled', False)

options = webdriver.FirefoxOptions()

options.add_argument('--headless')



connection = mysql.connector.connect(host='localhost',
                             database='gametamedealfinder',
                             user='root',
                             password='LrD3FZGUz5JXy5c')



class Scraper:
    def __init__(self):
        global firefox_profile
        global current_page
        global options
        #  global proxy_ip

        """proxy = Proxy({
                        'proxyType': ProxyType.MANUAL,
                        'httpProxy': proxy_ip,
                        'ftpProxy': proxy_ip,
                        'sslProxy': proxy_ip,
                        })"""

        self.browser = webdriver.Firefox(firefox_profile=firefox_profile, firefox_options=options)

        self.proxy_num = 0

        self.initialWait = WebDriverWait(self.browser, 120.0)
        self.regularWait = WebDriverWait(self.browser, 1.0)  # was 15.0

        self.current_items = list()
        self.current_point_prices = list()
        self.current_real_prices = list()

        self.counter = 0

        logger.debug('Initalized scraper')

    def shutdown(self):
        logger.debug('shutdown() called on Scraper instance')
        self.browser.quit()

    def fillItems(self, page):
        global item_list
        global point_price_list
        global num_iterations

        logger.info('Filling items from page #{}'.format(page))

        self.browser.get('https://gametame.com/tf2/page/' + str(page))
        self.initialWait.until(EC.title_contains('TF2'))
        col_items_full = self.browser.find_element_by_css_selector('#content > div > div > div.col-xs-12.col-sm-12.col-md-10.col-lg-10 > div.row.products')
        col_items = col_items_full.find_elements_by_class_name('col-md-2')
        #  print(len(col_items))

        for col in col_items:
            text = col.find_elements_by_xpath('.//div[2]')
            price = text[0].find_elements_by_xpath('.//p')
            link = text[0].find_elements_by_xpath('.//a')
            
            item_list.append(link[0].text)
            point_price_list.append(int(price[0].text[0:price[0].text.find(' ')]))

        print('Fetched items from page #{}'.format(page))

        if self.counter == 9:
            save_lists()
            self.counter = 0

        self.counter += 1
        sleep(0.1)

init_time = time()


def clear_lists():
    item_list.clear()
    point_price_list.clear()


def save_lists():
    global item_list
    global point_price_list

    item_list_file = open("item_list_file_complete.txt", "a+")
    point_price_list_file = open("point_price_list_file_complete.txt", "a+")

    item_name = item_list.readline().rstrip()
    point_price = point_list.readline().rstrip()  

    while len(item_name) != 0:
        sql_insert_query = """ INSERT INTO `ITEM LIST`
                          (`ITEM NAME`, `POINT VALUE`) VALUES (\"{}\",{})""".format(item_name, point_price)
        cursor = connection.cursor()
        result  = cursor.execute(sql_insert_query)
        item_name = item_list.readline().rstrip()
        point_price = point_list.readline().rstrip()

    item_list_file.close()
    point_price_list_file.close()

    clear_lists()

def main():
    s = Scraper()
    for i in range(1, 375):
        try:
            s.fillItems(i)
        except Exception as e:
            print(e)
            break
    
    clear_lists()
    save_lists()

try:
    main()
except Exception as e:
    print(e)
finally:
    os.system('taskkill /f /im geckodriver.exe /T')

    logger_handler.close()
