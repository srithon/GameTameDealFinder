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
from selenium.webdriver.common import desired_capabilities

from requests.exceptions import ProxyError

import logging

from random import random

import requests

from collections import defaultdict  # https://stackoverflow.com/questions/11236006/identify-duplicate-values-in-a-list-in-python





log_formatter = logging.Formatter('%(asctime)s %(levelname)s:%(name)s\t%(message)s',
                                  datefmt='%H:%M:%S')

log_handler = logging.FileHandler(filename='gametame_refresh_dota2.log')
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



def test_proxies(s = None):
    global proxies
    
    if s == None:
        s = Session()
    
    ping_threshold = 0.35
    ping_max = 2.0
    min_ping = 10.0
    min_prox = None
    
    i = 0
    
    while i < len(proxies):
        prox = proxies[i]
        try:
            start = time()
            s.get('https://gametame.com', proxies = get_proxy_dict(prox))
            end = time()
            
            ping = end - start
            
            if ping < min_ping:
                min_ping = ping
                min_prox = prox
            
            
            print('{} took {} seconds to load gametame'.format(prox, end - start))
            
            if ping > ping_max:
                proxies.pop(i)
                i -= 1
            
            if ping < ping_threshold:
                return prox
            
            i += 1
            # return prox
        except:
            print('{} is bad'.format(prox))
            proxies.pop(i)

    # print('All proxies were bad')
    return min_prox


def get_proxies(driver = None):
    global proxy_page

    close_driver = False

    if driver == None:
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        
        close_driver = True
        
        driver = webdriver.Firefox(firefox_options=options)
    
    while True:
        try:
            driver.get('https://free-proxy-list.net/anonymous-proxy.html')
            break
        except Exception as e:
            print(e)
            logger.error(e)
        
    search = driver.find_element_by_css_selector('#proxylisttable_filter > label:nth-child(1) > input:nth-child(1)')
    search.send_keys('elite proxy')
    sort_by_https = driver.find_element_by_css_selector('th.sorting:nth-child(7)') 
    sort_by_https.click()
    sleep(0.5)
    sort_by_https.click()
    sleep(1.0)

    current_page = 1

    while current_page < proxy_page:
        next_button = driver.find_element_by_css_selector('#proxylisttable_next > a:nth-child(1)')
        sleep(0.5)
        driver.execute_script('"window.scrollTo(0, document.body.scrollHeight);"')
        next_button.click()
        current_page += 1

    proxy_page += 1
    
    proxies_body = driver.find_element_by_css_selector('#proxylisttable > tbody:nth-child(2)')
    proxies = proxies_body.find_elements_by_xpath('.//tr')
    print('{} proxies found in total'.format(len(proxies)))
    if len(proxies) == 0:
          print('No Proxies Found!')
          logger.error('No Proxies Found!')
          return None
    proxy_list = list()
    for proxy_element in proxies:
        ip = proxy_element.find_element_by_xpath('.//td[1]').text
        port = proxy_element.find_element_by_xpath('.//td[2]').text
        print('{}:{}'.format(ip, port))
        logger.info('{}:{}'.format(ip, port))
        proxy_list.append('{}:{}'.format(ip, port))
    # os.system('taskkill /f /im geckodriver.exe /T')
    
    if close_driver:
        try:
            driver.quit()
        except Exception as e:
            print(e)
            logger.error(e)
    
    return proxy_list
    
def get_new_proxy(driver = None):
    global proxies
    print('{} proxies remaining'.format(len(proxies)))
    if len(proxies) == 0:
        logger.debug('Used up all proxies! Refreshing')
        proxies = get_proxies(driver)
    return proxies.pop(int(random() * len(proxies)))
    

def get_proxy_dict(current_proxy):
    return { "https" : str(current_proxy) }


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

        self.browser = webdriver.Firefox(firefox_profile=firefox_profile)#, firefox_options=options)

        self.proxy_num = 0

        self.initialWait = WebDriverWait(self.browser, 120.0)
        self.regularWait = WebDriverWait(self.browser, 1.0)  # was 15.0

        self.current_items = list()
        self.current_point_prices = list()
        self.current_real_prices = list()

        self.counter = 0
        
        self.s = requests.Session()
        
        self.rotate_proxy()

        logger.debug('Initalized scraper')

    def shutdown(self):
        logger.debug('shutdown() called on Scraper instance')
        self.browser.quit()
        
    def rotate_proxy(self):
        global proxies
        if len(proxies) == 0:
            proxies = get_proxies(self.browser)
        
        self.proxy = get_proxy_dict(test_proxies(self.s))

    def fillItems(self, page):
        global item_list
        global point_price_list
        global num_iterations

        logger.info('Filling items from page #{}'.format(page))

        try:
            for i in range(2):
                self.browser.get('https://gametame.com/dota2/page/' + str(page))
                self.initialWait.until(EC.title_contains('DOTA 2'))
                col_items_full = self.browser.find_element_by_css_selector('#content > div > div > div.col-xs-12.col-sm-12.col-md-10.col-lg-10 > div.row.products')
                col_items = col_items_full.find_elements_by_class_name('col-md-2')
                #  print(len(col_items))

                if i == 0:
                    for col in col_items:
                        text = col.find_elements_by_xpath('.//div[2]')
                        #  price = text[0].find_elements_by_xpath('.//p')
                        link = text[0].find_elements_by_xpath('.//a')
                        while True:
                            try:
                                self.s.get(link[0].get_attribute('href'), proxies = self.proxy)
                                break
                            except KeyboardInterrupt:
                                print('Exiting...')
                                self.shutdown()
                                shutdown()
                            except:
                                self.rotate_proxy()
                                print('Rotated proxy')
                                logger.debug('Rotated proxy')
                    sleep(0.1)
                else:
                    for col in col_items:
                        text = col.find_elements_by_xpath('.//div[2]')
                        price = text[0].find_elements_by_xpath('.//p')
                        link = text[0].find_elements_by_xpath('.//a')
                        
                        item_list.append(link[0].text)
                        point_price_list.append(int(price[0].text[0:price[0].text.find(' ')]))

            print('Fetched items from page #{}'.format(page))

            if self.counter == 29:
                save_lists()
                self.counter = 0

            self.counter += 1
            sleep(0.1)
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

    item_name = item_list.pop(0)
    point_price = point_price_list.pop(0)

    cursor = connection.cursor()
    
    print('Saving lists...')

    while len(item_list) != 0:
        sql_update_query = 'UPDATE `ITEM LIST STEAM MARKET DOTA2` SET pointPrice = %s WHERE name = %s'

        cursor.execute(sql_update_query, (point_price, item_name))
        
        item_name = item_list.pop(0)
        point_price = point_price_list.pop(0)
    connection.commit()

def main():
    s = Scraper()
    for i in range(1, 717):
        try:
            s.fillItems(i)
        except Exception as e:
            print(e)
            logger.error(e)
            break
    
    save_lists()
    clear_lists()

try:
    main()
except Exception as e:
    print(e)
finally:
    shutdown()
