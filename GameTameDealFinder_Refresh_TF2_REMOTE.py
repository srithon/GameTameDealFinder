from time import sleep, time

#  import pickle
import traceback

import os

import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode

from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException

import sys

import logging

from random import random

import requests

import pickle

from collections import defaultdict  # https://stackoverflow.com/questions/11236006/identify-duplicate-values-in-a-list-in-python





log_formatter = logging.Formatter('%(asctime)s %(levelname)s:%(name)s\t%(message)s',
                                  datefmt='%H:%M:%S')

log_handler = logging.FileHandler(filename='gametame_refresh_tf2.log')
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

proxy_page = 1

proxies = list()

connection = mysql.connector.connect(host='localhost',
                             database='gametamedealfinder',
                             user='root',
                             password='LrD3FZGUz5JXy5c')


def save_cookie(driver, path):
    print('Saving cookies')
    while True:
        try:
            with open(path, 'wb') as filehandler:
                pickle.dump(driver.get_cookies(), filehandler)
            break
        except Exception as e:
            print(e)
            try:
                driver.refresh()
            except Exception as j:
                print(j)



def load_cookie(driver, path):
    with open(path, 'rb') as cookiesfile:
        cookies = pickle.load(cookiesfile)
        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                print(e)
                continue
            print('Added {}'.format(cookie))
    print('Finished adding cookies')


def get_gametame_cookie(site = None):
    try:
        profile = webdriver.FirefoxProfile()
        profile.set_preference('general.useragent.override', 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:66.0) Gecko/20100101 Firefox/66.0')
        options = webdriver.FirefoxOptions()
        options.add_argument("--enable-file-cookies")
        driver1 = webdriver.Firefox(firefox_profile = profile, firefox_options = options)
        driver1.get('https://gametame.com/auth/')
        wait = WebDriverWait(driver1, 640.0)
        wait.until(EC.title_contains('Earn'))
        sleep(10)
        print('Done sleeping')
    except KeyboardInterrupt as e:
        print('Interrupted')
    finally:
        print('Saving cookies...')
        save_cookie(driver1, 'gt.cck')
        print('Saved cookies')


class Scraper:
    def __init__(self):
        global firefox_profile
        global current_page
        global options

        self.browser = self.get_browser()

        self.proxy_num = 0

        self.initialWait = WebDriverWait(self.browser, 120.0)
        self.regularWait = WebDriverWait(self.browser, 1.0)  # was 15.0

        self.current_items = list()
        self.current_point_prices = list()
        self.current_real_prices = list()

        self.counter = 0

        logger.debug('Initalized scraper')
        
        self.login()
        
    def get_browser(self):
        """firefox_profile = webdriver.FirefoxProfile()
        firefox_profile.set_preference('permissions.default.stylesheet', 2)
        # Disable images
        firefox_profile.set_preference('permissions.default.image', 2)
        # Disable Flash
        firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so',
                                       'false')
        firefox_profile.set_preference('javascript.enabled', False)
        firefox_profile.set_preference("general.warnOnAboutConfig", False)
        
        options = webdriver.FirefoxOptions()
        options.add_argument("--enable-file-cookies")
        options.add_argument("--headless")
        
        return webdriver.Firefox(firefox_options = options, firefox_profile = firefox_profile)"""
        
        try:
            return webdriver.Remote(command_executor = 'localhost:9515', desired_capabilities = self.get_capabilities())
        except Exception as e:
            print(e)
            print('Error get browser rip')
            sys.exit(0)
        
    def get_capabilities(self):
        try:
            capabilities = {'browserName': 'MicrosoftEdge', 'platform': 'WINDOWS', 'version': ''}
        except Exception as e:
            print('Error is here _ get_capabilities()')
            print(e)
            sys.exit(0)

    def shutdown(self):
        logger.debug('shutdown() called on Scraper instance')
        self.browser.quit()
        
    def login(self):
        self.browser.get('https://gametame.com/images/invalid')
        sleep(2.0)
        load_cookie(self.browser, 'gt.cck')
        sleep(2.0)
        print('Finished loading cookies')
        self.browser.get('https://google.com')
        sleep(2.0)
        self.browser.get('https://gametame.com')
        print('Refreshed self.browser')

        sleep(3)

    def fillItems(self, page):
        global item_list
        global point_price_list
        global num_iterations

        logger.info('Filling items from page #{}'.format(page))

        try:
            self.browser.get('https://gametame.com/tf2/page/' + str(page))
            self.initialWait.until(EC.title_contains('TF2'))
            col_items_full = self.browser.find_element_by_css_selector('#content > div > div > div.col-xs-12.col-sm-12.col-md-10.col-lg-10 > div.row.products')
            col_items = col_items_full.find_elements_by_class_name('col-md-2')
            #  print(len(col_items))
            
            items = list()
            
            for col in col_items:
                text = col.find_elements_by_xpath('.//div[2]')
                price = text[0].find_elements_by_xpath('.//p')
                link = text[0].find_elements_by_xpath('.//a')
                
                items.append(link[0].get_attribute('href'))

            for item in items:
                self.browser.get(item)
                point_price_elem = self.browser.find_element_by_css_selector('#productMain > div:nth-child(2) > form > p.price')
                item_name_elem = self.browser.find_element_by_css_selector('#productMain > div:nth-child(2) > h2')
                item_list.append(item_name_elem.text)
                point_price_list.append(int(point_price_elem.text[0:point_price_elem.text.find(' ')]))
                sleep(1.0)
            
            items.clear()

            print('Fetched items from page #{}'.format(page))

            if self.counter == 49:
                save_lists()
                self.counter = 0
                sleep(120.0)

            self.counter += 1
            sleep(2.0)
        except KeyboardInterrupt:
            print('Exiting...')
            self.shutdown()
            shutdown()

init_time = time()


def shutdown():
    log_handler.close()
    os.system('taskkill /f /im geckodriver.exe /T')

def clear_lists():
    item_list.clear()
    point_price_list.clear()


def save_lists():
    global item_list
    global point_price_list
    
    print(len(item_list))
    print(item_list)
    print(len(point_price_list))
    print(point_price_list)

    item_name = item_list.pop(0)
    point_price = point_price_list.pop(0)

    cursor = connection.cursor()
    
    print('Saving lists...')

    while len(item_list) != 0:
        sql_update_query = 'UPDATE `ITEM LIST STEAM MARKET TF2` SET PointValue = %s WHERE ItemName = %s'
        cursor.execute(sql_update_query, (point_price, item_name))
        
        item_name = item_list.pop(0)
        point_price = point_price_list.pop(0)
    connection.commit()
    
    item_list.clear()
    point_price_list.clear()

def main():
    s = Scraper()
    for i in range(1, 375):
        try:
            s.fillItems(i)
        except Exception as e:
            print(e)
            logger.error(e)
            break
    
    save_lists()
    clear_lists()


def _main():
    get_gametame_cookie()


try:
    main()
except Exception as e:
    print(e)
finally:
    shutdown()
