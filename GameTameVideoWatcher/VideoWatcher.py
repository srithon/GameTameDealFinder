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

from selenium.webdriver.common.proxy import Proxy, ProxyType

from time import sleep, time

from requests import Session


cookie_path = 'cookies.cck'

proxy_page = 1

proxies_list = list()

def test_proxies():
    global proxies_list
    s = Session()
    
    min_ping = 10.0
    min_prox = None
    
    for prox in proxies_list:
        try:
            start = time()
            s.get('https://gametame.com', proxies = get_proxy_dict(prox))
            end = time()
            
            ping = end - start
            
            if ping < min_ping:
                min_ping = ping
                min_prox = prox
            
            print('{} took {} seconds to load gametame'.format(prox, end - start))
            
            if ping < 0.25:
                return prox
            # return prox
        except:
            print('{} is bad'.format(prox))
    print('All proxies were bad')
    return min_prox

def update_proxies():
    global proxy_page, proxies_list

    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    
    driver = webdriver.Firefox(firefox_options=options)
    
    while True:
        try:
            # driver.get('https://free-proxy-list.net/anonymous-proxy.html')
            driver.get('https://www.us-proxy.org')
            break
        except Exception as e:
            print(e)
        
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
          return None
    for proxy_element in proxies:
        ip = proxy_element.find_element_by_xpath('.//td[1]').text
        port = proxy_element.find_element_by_xpath('.//td[2]').text
        
        print('{}:{}'.format(ip, port))
        proxies_list.append('{}:{}'.format(ip, port))
    os.system('taskkill /f /im geckodriver.exe /T')
    
def get_new_proxy():
    global proxies_list
    print('{} proxies remaining'.format(len(proxies_list)))
    if len(proxies) == 0:
        print('Ran outta proxies')
        get_proxies()
    return proxies_list.pop(int(random() * len(proxies)))
    
def get_proxy_dict(current_proxy):
    return { "https" : str(current_proxy) }


def get_proxy():
    myProxy = test_proxies()
    
    return myProxy

    proxy = Proxy({
        'proxyType': ProxyType.MANUAL,
        'httpProxy': myProxy,
        'ftpProxy': myProxy,
        'sslProxy': myProxy,
        'noProxy': 'localhost'
        })
    
    return proxy

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

def get_hideouttv_cookie():
    try:
        profile = webdriver.FirefoxProfile()
        profile.set_preference('general.useragent.override', 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:66.0) Gecko/20100101 Firefox/66.0')
        options = webdriver.FirefoxOptions()
        options.add_argument("--enable-file-cookies")
        driver1 = webdriver.Firefox(firefox_profile = profile, firefox_options = options)
        driver1.get('https://hideout.tv/login.php')
        wait = WebDriverWait(driver1, 640.0)
        wait.until(EC.title_contains('Hideout.tv - '))
        print('Done sleeping')
    except KeyboardInterrupt as e:
        print('Interrupted')
    finally:
        print('Saving cookies...')
        save_cookie(driver1, 'hotv.cck')
        print('Saved cookies')

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

def get_browser(proxy = None):
    firefox_profile = webdriver.FirefoxProfile()
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
    
    if proxy != None:
        set_proxy(firefox_profile, proxy)
    
    return webdriver.Firefox(firefox_options = options, firefox_profile = firefox_profile)

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

def login_with_cookies(driver=None):
    """while True:
        if proxy == None:
            print('No proxy')
            driver = webdriver.Firefox(firefox_profile = firefox_profile, firefox_options = options)
        else:
            driver = webdriver.Firefox(firefox_profile = firefox_profile, firefox_options = options, proxy = proxy)
        
        try:
            driver.get('http://gametame.com')
            break
        except Exception as e:
            print('Error in get')
            print(e)
            if proxy != None:
                proxy = get_new_proxy()
            try:
                driver.quit()
            except Exception as e:
                print('Error in quit')
                print(e)"""
    
    if driver == None:
        driver = get_browser()
    
    driver.get('https://gametame.com/image/discord_bottom.png')
    sleep(2.0)
    load_cookie(driver, 'gt.cck')
    sleep(2.0)
    print('Finished loading cookies')
    driver.get('https://google.com')
    sleep(2.0)
    driver.get('https://gametame.com')
    print('Refreshed driver')

    sleep(3)
    
    return driver

def get_browser_with_new_proxy():
    proxy = get_proxy()
    return get_browser(proxy)
    

def watch_videos():
    # update_proxies()
    # init_driver = get_browser_with_new_proxy()
    # sleep(20)
    driver = login_with_cookies() # init_driver)
    
    while True:
        try:
            smores_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#videos > section:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > a:nth-child(2) > img:nth-child(1)')))
            break
        except Exception as e:
            print(e)
            driver.get('https://gametame.com')
        
    driver.execute_script('window.scrollTo(' + str(smores_button.location['x'])
                                + ',' + str(smores_button.location['y'] - 150) + ');')
    ActionChains(driver).move_to_element(smores_button).perform()
    sleep(0.25)
    ActionChains(driver).click(smores_button).perform()
    
    sleep(3)
    
    driver.switch_to_window(driver.window_handles[0])
    driver.close()
    driver.switch_to_window(driver.window_handles[0])
    
    offer_body = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#aw_offers")))
    sleep(2)
    offers = offer_body.find_elements_by_class_name('offer')
    
    for i in range(2):# range(len(offers)):
        offer = offers[i]
        offer_button = offer.find_element_by_xpath('./div/div/div[2]/div[2]/a')
        
        ActionChains(driver).move_to_element(offer_button).perform()
        sleep(0.25)
        ActionChains(driver).click(offer_button).perform()
        
        sleep(0.25)
        
        offer_confirm_button = driver.find_element_by_css_selector('.js-sending-offer-on-device > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(2) > a:nth-child(1)')#('.arrow_rotate')
        
        ActionChains(driver).move_to_element(offer_confirm_button).perform()
        sleep(0.25)
        ActionChains(driver).click(offer_confirm_button).perform()
        
        sleep(1.5)
        
        driver.switch_to_window(driver.window_handles[0])
        # print(offer_button.get_attribute('href'))
    

def main():
    # get_session_cookie(True)
    # test_session_cookie()
    login_with_cookies()
    # watch_videos()
    # get_gametame_cookie()
    # get_hideouttv_cookie()

main()