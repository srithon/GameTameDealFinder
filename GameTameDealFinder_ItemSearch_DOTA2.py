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



proxy_ip = '177.241.244.219:56792'

item_name = 'Robes of the Captive Princess'



log_formatter = logging.Formatter('%(asctime)s %(levelname)s:%(name)s\t%(message)s',
                                  datefmt='%H:%M:%S')

log_handler = logging.FileHandler(filename='gametame_item_search_dota2.log')
log_handler.setFormatter(log_formatter)

log_handler.setLevel(logging.DEBUG)

#  logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger('root_logger')

#  logging.getLogger('')
logger.addHandler(log_handler)

logger.setLevel(logging.DEBUG)

logger.info('Starting script...')

handler = None

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


def set_proxy(profile, proxy):
    ip = proxy[:proxy.find(':')]
    port = proxy[(proxy.find(':') + 1):]
    print(ip)
    print(port)
    profile.DEFAULT_PREFERENCES['frozen']["network.proxy.type"] = 1
    profile.DEFAULT_PREFERENCES['frozen']["network.proxy.http"] = ip
    profile.DEFAULT_PREFERENCES['frozen']["network.proxy.http_port"] = int(port)
    profile.DEFAULT_PREFERENCES['frozen']["network.proxy.ssl"] = ip
    profile.DEFAULT_PREFERENCES['frozen']["network.proxy.ssl_port"] = int(port)


# set_proxy(firefox_profile, proxy_ip)


class Scraper:
    def __init__(self):
        global firefox_profile
        global current_page
        global options
        global proxy_ip

        self.browser = webdriver.Firefox(firefox_profile=firefox_profile)#, firefox_options=options)

        self.proxy_num = 0

        self.initialWait = WebDriverWait(self.browser, 120.0)
        self.regularWait = WebDriverWait(self.browser, 1.0)  # was 15.0
        self.counter = 0
        
        # self.s = requests.Session()

        logger.debug('Initalized scraper')

    def shutdown(self):
        logger.debug('shutdown() called on Scraper instance')
        try:
            self.browser.quit()
        except Exception as e:
            print('Exception in Scraper shutdown')
            print(e)
            logger.error(e)

    def searchPage(self, page):
        logger.info('Looking in page #{}'.format(page))

        try:
            self.browser.get('https://gametame.com/dota2/page/' + str(page))
            self.initialWait.until(EC.title_contains('DOTA'))
            col_items_full = self.browser.find_element_by_css_selector('#content > div > div > div.col-xs-12.col-sm-12.col-md-10.col-lg-10 > div.row.products')
            col_items = col_items_full.find_elements_by_class_name('col-md-2')
            #  print(len(col_items))

            for col in col_items:
                text = col.find_elements_by_xpath('.//div[2]')
                link = text[0].find_elements_by_xpath('.//a')
                
                if link[0].text == item_name:
                    print('Found item on page {}'.format(page))
                    logger.info('Found {} on page {}'.format(item_name, page))
                    self.shutdown()
                    shutdown()

            sleep(0.1)
        except KeyboardInterrupt:
            print('Exiting...')
            self.shutdown()
            shutdown()

init_time = time()


def shutdown():
    log_handler.close()
    os.system('taskkill /f /im geckodriver.exe /T')


def main():
    s = Scraper()
    for i in range(76, 200):
        try:
            s.searchPage(i)
        except Exception as e:
            print(e)
            logger.error(e)
            break

    print('Could not find item')
    logger.error('Could not find item')

try:
    main()
except Exception as e:
    print(e)
finally:
    shutdown()
