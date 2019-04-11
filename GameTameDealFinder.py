from time import sleep, time

#  import pickle

import traceback

#  import unidecode

import os
# from time import time
#  from random import random

# import threading
#  import os

from selenium import webdriver
from selenium.webdriver.common.by import By
#  from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.keys import Keys

#  from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common import desired_capabilities

import logging

from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException

from collections import defaultdict  # https://stackoverflow.com/questions/11236006/identify-duplicate-values-in-a-list-in-python

from selenium.webdriver.common.proxy import Proxy, ProxyType

log_formatter = logging.Formatter('%(asctime)s %(levelname)s:%(name)s\t%(message)s',
                                  datefmt='%H:%M:%S')

log_handler = logging.FileHandler(filename='gametame_logger.log')
log_handler.setFormatter(log_formatter)

log_handler.setLevel(logging.DEBUG)

#  logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger('root_logger')

#  logging.getLogger('')
logger.addHandler(log_handler)

logger.setLevel(logging.DEBUG)

logger.info('Starting script...')

DISPLAY = False
SORT = False

current_page = 100
num_iterations = 100
query_count = 0
handler = None

item_list = list()
money_per_point_list = list()
real_price_list = list()
point_price_list = list()

proxy_list = ['66.172.114.113:43100', '177.103.223.155:3128']

logger.debug('DISPLAY={}, SORT={}, current_page={}, num_iterations={}'.format(DISPLAY, SORT, current_page, num_iterations))

if not DISPLAY:
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
else:
    try:
        item_list_file = open("item_list_file.txt", "r")
        for line in item_list_file:
            item_list.append(line.rstrip())
    except FileNotFoundError:
        pass

    item_list_file.close()

    try:
        money_per_point_list_file = open("money_per_point_list_file.txt", "r")
        for line in money_per_point_list_file:
            money_per_point_list.append(float(line.rstrip()))
    except FileNotFoundError:
        pass

    money_per_point_list_file.close()

    try:
        real_price_list_file = open("real_price_list_file.txt", "r")
        for line in real_price_list_file:
            real_price_list.append(float(line.rstrip()))
    except FileNotFoundError:
        pass

    real_price_list_file.close()

    try:
        point_price_list_file = open("point_price_list_file.txt", "r")
        for line in point_price_list_file:
            point_price_list.append(int(line.rstrip()))
    except FileNotFoundError:
        pass

        point_price_list_file.close()

    logger.debug('Finished loading lists.')
    logger.debug('Total items in list - {}'.format(len(item_list)))
#  proxy_ip = '36.37.134.3:8080'


class Handler:
    def __init__(self, num_iterations, iterations_per_save):
        self.num_iterations = num_iterations / iterations_per_save
        self.iterations_per_save = iterations_per_save

    def start(self):
        global money_per_point_list
        self.scrap = Scraper()
        while (self.num_iterations > 0):
            try:
                if not self.scrap.iterate(self.iterations_per_save):
                    try:
                        self.scrap.shutdown()
                    except Exception:
                        pass
                    return False
            except Exception:
                print(traceback.format_exc())

            print('Handler ~ Completed')

            money_per_point_list.extend(get_money_per_point())

            sort_lists()
            save_lists()

            print('Handler ~ Saved')

            self.num_iterations -= 1
            print('Handler ~ {} iterations left'.format(self.num_iterations))

        try:
            self.scrap.shutdown()
        except Exception:
            pass

        os.system('taskkill /f /im geckodriver.exe /T')

        return True


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

        self.page = current_page

        logger.debug('Initalized scraper')

        """
            list1, list2 = (list(t) for t in zip(*sorted(zip(list1, list2))))
        """

    def rotate_browser(self):
        global proxy_list, firefox_profile, options

        try:
            self.shutdown()
        except:
            traceback.print_exc()

        self.proxy_num += 1
        self.proxy_num %= 3

        sleep(10)

        if self.proxy_num == 0:
            self.browser = webdriver.Firefox(firefox_profile = firefox_profile, firefox_options = options)
        else:
            prox = Proxy()

            pxy = proxy_list[self.proxy_num]

            prox.proxy_type = ProxyType.MANUAL
            prox.http_proxy = pxy
            prox.socks_proxy = pxy
            prox.ssl_proxy = pxy

            capabilities = webdriver.DesiredCapabilities.FIREFOX
            prox.add_to_capabilities(capabilities)
            self.browser = webdriver.Firefox(firefox_profile=firefox_profile, firefox_options=options, desired_capabilities=capabilities)

    def iterate(self, n):
        global money_per_point_list

        logger.info('Iterating for {} times'.format(n))
        logger.info('Current Page - {}, Final Page - {}'.format(self.page, self.page + n - 1))

        for page in range(self.page, self.page + n):
            self.fillItems(page, (page - self.page) + 1)
            if not self.fillRealPrices():
                logger.critical('Failure in fillRealPrices()')
                return False
        self.page += n

        return True

    def shutdown(self):
        logger.debug('shutdown() called on Scraper instance')
        self.browser.quit()

    def fillItems(self, page, n):
        global item_list
        global point_price_list
        global num_iterations

        self.current_items.clear()
        self.current_point_prices.clear()

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
            self.current_items.append(link[0].text)
            self.current_point_prices.append(int(price[0].text[0:price[0].text.find(' ')]))
            #  print(link[0].text)
            #  print(price[0].text)

        #  item_list.extend(self.current_items)
        #  point_price_list.extend(self.current_point_prices)

        print('Fetched items from page #{} ({}/{})'.format(page, page - current_page, num_iterations))
        logger.info('Fetched items from page #{} ({}/{})'.format(page, page - current_page + 1, num_iterations))

    def fillRealPrices(self):
        global real_price_list
        global firefox_profile
        global query_count

        stop = False

        i = 0

        while i < len(self.current_items):
            try:
                self.browser.get('https://steamcommunity.com/market/priceoverview/?country=US&currency=1&appid=440&market_hash_name=' + str(self.current_items[i]))
                query_count += 1
            except WebDriverException:
                logger.debug('WebDriverException in fillRealPrices(); Refreshing page')
                sleep(0.5)
                self.browser.get('https://steamcommunity.com/market/priceoverview/?country=US&currency=1&appid=440&market_hash_name=' + str(self.current_items[i]))

            while True:
                try:
                    text = self.regularWait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/div[1]/div/div/div[2]/table/tbody/tr[2]/td[2]/span/span')))
                    #  browser.find_element_by_xpath('/html/body/div/div/div/div[1]/div/div/div[2]/table/tbody/tr[2]/td[2]/span/span')
                    stop = False
                    break
                except NoSuchElementException and TimeoutException:
                    print('Can''t find element for item {}'.format(self.current_items[i]))
                    logger.debug('Can''t find element for item {}'.format(self.current_items[i]))
                    source = self.browser.page_source
                    if 'null' in source:
                        print('NULL IN SOURCE')
                        logger.critical('Null found in page source')
                        logger.critical('iteration={}, page={}, pages completed={}'.format(i, self.page, self.page - current_page))
                        return False
                        self.rotate_browser()
                        sleep(4.0)
                        print('Rotated browser')
                    elif not stop:
                        logger.debug('Loop iteration #1 unsuccessful; stop=True')
                        stop = True
                    else:
                        logger.debug('Failed twice - Index #{} popped from list'.format(i))
                        self.current_items.pop(i)
                        self.current_point_prices.pop(i)
                        break
                    sleep(1)

            if stop:
                stop = False
                continue

            try:
                price = float(text.text[2:-1])
            except ValueError:
                print('ValueError in {}'.format(text.text))
                logger.debug('ValueError in {}'.format(text.text))
                text = self.browser.find_element_by_xpath('/html/body/div/div/div/div[1]/div/div/div[2]/table/tbody/tr[3]/td[2]/span/span')
                price = float(text.text[2:-1])
                print(price)
            #  print(price)
            self.current_real_prices.append(price)
            print('Completed iteration #{}/{}'.format(i + 1, len(self.current_items)))
            i += 1
            sleep(2.90)

        real_price_list.extend(self.current_real_prices)
        item_list.extend(self.current_items)
        point_price_list.extend(self.current_point_prices)

        self.current_real_prices.clear()
        self.current_items.clear()
        self.current_point_prices.clear()

        print()
        logger.info('fillRealPrices() exited correctly')
        return True


def get_money_per_point():
    ret = list()
    for i in range(0, len(real_price_list)):
        ret.append((real_price_list[i] / point_price_list[i]))
        #  print(ret[i])
    return ret


init_time = time()


def print_lists():
    global item_list
    global money_per_point_list
    global real_price_list
    global point_price_list

    dash = '-' * 93

    #  print(dash)
    #  print('{:<20s}{:>4s}{:^12s}{:>12s}'.format('Name', 'M/P', 'M', 'P'))
    print(dash)

    for i in range(len(money_per_point_list)):
        print('{:<60s}{:>4.3f}{:^12.2f}{:>12d}'.format(item_list[i], money_per_point_list[i], real_price_list[i], point_price_list[i]))


def sort_lists():
    global money_per_point_list, item_list, real_price_list, point_price_list

    index_list = list()
    for i in range(0, len(money_per_point_list)):
        index_list.append(i)

    for i in range(1, len(money_per_point_list)):
        ind = i
        while (ind > 0 and money_per_point_list[ind] < money_per_point_list[ind - 1]):
            temp = money_per_point_list[ind]
            money_per_point_list[ind] = money_per_point_list[ind - 1]
            money_per_point_list[ind - 1] = temp

            index_list[ind] ^= index_list[ind - 1]
            index_list[ind - 1] ^= index_list[ind]
            index_list[ind] ^= index_list[ind - 1]

            ind = ind - 1

    item_list = [item_list[i] for i in index_list]
    real_price_list = [real_price_list[i] for i in index_list]
    point_price_list = [point_price_list[i] for i in index_list]


# https://stackoverflow.com/questions/11236006/identify-duplicate-values-in-a-list-in-python
def remove_duplicates():
    global item_list
    global point_price_list
    global money_per_point_list
    global real_price_list

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

    logger.info('{} duplicates found in list'.format(len(indices)))

    while len(indices) > 0:
        item_list.pop(indices[0])
        point_price_list.pop(indices[0])
        money_per_point_list.pop(indices[0])
        real_price_list.pop(indices[0])
        indices.pop(0)


def save_lists():
    global item_list
    global point_price_list
    global money_per_point_list
    global real_price_list

    item_list_file = open("item_list_file.txt", "a+")
    money_per_point_list_file = open("money_per_point_list_file.txt", "a+")
    real_price_list_file = open("real_price_list_file.txt", "a+")
    point_price_list_file = open("point_price_list_file.txt", "a+")

    for i in range(0, len(item_list)):
        item_list_file.write(item_list[i] + '\n')
        money_per_point_list_file.write(str(money_per_point_list[i]) + '\n')
        real_price_list_file.write(str(real_price_list[i]) + '\n')
        point_price_list_file.write(str(point_price_list[i]) + '\n')

    item_list_file.close()
    money_per_point_list_file.close()
    real_price_list_file.close()
    point_price_list_file.close()

    item_list.clear()
    point_price_list.clear()
    money_per_point_list.clear()
    real_price_list.clear()

    logger.debug('Saved lists')


def main():
    global item_list
    global point_price_list
    global money_per_point_list
    global real_price_list
    global num_iterations
    global handler

    handler = Handler(num_iterations, 2)

    if handler.start():
        return True
    else:
        return False

    #  money_per_point_list.extend(get_money_per_point())

    # sort_lists()

    #  print_lists()


def __main__():
    global handler

    if not DISPLAY:
        try:
            if not main():
                print('FAIL')
        except Exception as e:
            print(e)

        print('{} seconds elapsed'.format(time() - init_time))
        logger.info('{} seconds elapsed'.format(time() - init_time))

        #  save_lists()

        final_page = handler.scrap.page

        print('Ended on page #{}'.format(final_page))
        logger.info('Start next run at page #{}'.format(final_page))

        """if len(item_list) < (36 * num_iterations):
            print('Finish this run before proceeding; {} entries in list, {} entries needed'.format(len(item_list), (36 * num_iterations)))
        else:
            print('Start next run at page #{}'.format(num_iterations + current_page))"""
    else:
        if SORT:
            sort_lists()

            remove_duplicates()

            item_list_file = open("item_list_file.txt", "w")
            money_per_point_list_file = open("money_per_point_list_file.txt", "w")
            real_price_list_file = open("real_price_list_file.txt", "w")
            point_price_list_file = open("point_price_list_file.txt", "w")

            for i in range(0, len(item_list)):
                item_list_file.write(item_list[i] + '\n')
                money_per_point_list_file.write(str(money_per_point_list[i]) + '\n')
                real_price_list_file.write(str(real_price_list[i]) + '\n')
                point_price_list_file.write(str(point_price_list[i]) + '\n')

            item_list_file.close()
            money_per_point_list_file.close()
            real_price_list_file.close()
            point_price_list_file.close()

        print_lists()

        if len(item_list) < (36 * (current_page + num_iterations)):
            print('Finish this run before proceeding; {} entries in list, {} entries needed'.format(len(item_list), (36 * (current_page + num_iterations))))
        else:
            print('Start next run at page #{}'.format(num_iterations + current_page))

    print(traceback.format_exc())


__main__()

log_handler.close()
print('Closed log handler')

with open('gametame_logger.log', mode='a') as file:
    file.write('\n' + ('-' * 70) + '\n\n')
