from random import random

# import threading
import os

import pickle

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.keys import Keys

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from time import sleep


cookie_path = 'cookies.cck'


def save_cookie(driver):
    global cookie_path
    path = cookie_path
    print('Saving cookies')
    while True:
        try:
            with open(path, 'wb') as filehandler:
                pickle.dump(driver.get_cookies(), filehandler)
            break
        except Exception as e:
            print(e)
            try:
                driver.get('https://gametame.com')
            except Exception as j:
                print(j)

def load_cookie(driver):
    global cookie_path
    path = cookie_path
    with open(path, 'rb') as cookiesfile:
        cookies = pickle.load(cookiesfile)
        for cookie in cookies:
            driver.add_cookie(cookie)
            print('Added {}'.format(cookie))
    print('Finished adding cookies')

def get_session_cookie():
    try:
        profile = webdriver.FirefoxProfile()
        profile.set_preference('general.useragent.override', 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:66.0) Gecko/20100101 Firefox/66.0')
        options = webdriver.FirefoxOptions()
        options.add_argument("--enable-file-cookies")
        driver1 = webdriver.Firefox(firefox_profile = profile, firefox_options = options)
        driver1.get('https://gametame.com')
        sleep(15.0)
        wait = WebDriverWait(driver1, 640.0)
        wait.until(EC.title_contains('Earn'))
        print('Done sleeping')
    except KeyboardInterrupt as e:
        print('Interrupted')
    finally:
        print('Saving cookies...')
        save_cookie(driver1)
        print('Saved cookies')
        driver1.quit()

def login_with_cookies():
    firefox_profile = webdriver.FirefoxProfile()
    # firefox_profile.set_preference('permissions.default.stylesheet', 2)
    # Disable images
    firefox_profile.set_preference('permissions.default.image', 2)
    # Disable Flash
    firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so',
                                   'false')
    firefox_profile.set_preference('javascript.enabled', False)
    
    options = webdriver.FirefoxOptions()
    options.add_argument("--enable-file-cookies")

    driver = webdriver.Firefox(firefox_profile = firefox_profile, firefox_options = options)

    driver.get('http://gametame.com')
    load_cookie(driver)
    print('Finished loading cookies')
    driver.refresh()
    print('Refreshed driver')
    
    sleep(5)
    
    close_button = driver.find_element_by_css_selector('button.btn:nth-child(3)')
    close_button.submit()
    
    return driver

def watch_videos():
    driver = login_with_cookies()
    smores_button = driver.find_element_by_css_selector('#videos > section:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > a:nth-child(2) > img:nth-child(1)')
    driver.execute_script('window.scrollTo(' + str(smores_button.location['x'])
                                + ',' + str(smores_button.location['y']) + ');')
    ActionChains(driver).move_to_element(smores_button).perform()
    sleep(0.25)
    ActionChains(driver).click(smores_button).perform()
    

def main():
    # get_session_cookie()
    # test_session_cookie()
    login_with_cookies()

main()