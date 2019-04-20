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


# https://stackoverflow.com/questions/11236006/identify-duplicate-values-in-a-list-in-python
def remove_duplicates():
    global item_list
    global point_price_list

    """i = 0

    while i < len(item_list) - 2:
        i += 1
        if item_list[i] == item_list[i + 1]:
            item_list.pop(i + 1)
            point_price_list.pop(i + 1)
            money_per_point_list.pop(i + 1)
            real_price_list.pop(i + 1)
            i -= 1"""

    D = defaultdict(list)

    for i, item in enumerate(item_list):
        D[item].append(i)
    D = {k:v for k,v in D.items() if len(v)>1}

    indices = list()

    for i in reversed(list(D.values())):
        for j in range(len(i) - 1, 0, -1):
            indices.append(i[j])

    indices.sort(reverse=True)

    print(indices)

    while len(indices) > 0:
        item_list.pop(indices[0])
        point_price_list.pop(indices[0])
        indices.pop(0)


def save_lists():
    global item_list
    global point_price_list

    item_list_file = open("item_list_file.txt", "a+")
    point_price_list_file = open("point_price_list_file.txt", "a+")

    for i in range(0, len(item_list)):
        item_list_file.write(item_list[i] + '\n')
        point_price_list_file.write(str(point_price_list[i]) + '\n')

    item_list_file.close()
    point_price_list_file.close()

    clear_lists()

def load_lists():
    try:
        point_price_list_file = open("point_price_list_file.txt", "r")
        for line in point_price_list_file:
            point_price_list.append(float(line.rstrip()))
    except FileNotFoundError:
        pass

    point_price_list_file.close()

    try:
        item_list_file = open("item_list_file.txt", "r")
        for line in item_list_file:
            item_list.append(line.rstrip())
    except FileNotFoundError:
        pass

    item_list_file.close()

def main():
    s = Scraper()
    for i in range(112, 375):
        try:
            s.fillItems(i)
        except Exception as e:
            print(e)
            break
    clear_lists()
    load_lists()
    remove_duplicates()
    save_lists()

try:
    main()
except Exception as e:
    print(e)

os.system('taskkill /f /im geckodriver.exe /T')

logger_handler.close()
