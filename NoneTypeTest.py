import requests
from time import time, sleep
from requests.exceptions import ProxyError
from random import random
from selenium import webdriver
import os

proxy_page = 1
proxies = list()


def get_proxies():
    global proxy_page

    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    
    driver = webdriver.Firefox(firefox_options=options)
    driver.get('https://free-proxy-list.net/anonymous-proxy.html')
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
    proxy_list = list()
    for proxy_element in proxies:
        ip = proxy_element.find_element_by_xpath('.//td[1]').text
        port = proxy_element.find_element_by_xpath('.//td[2]').text
        print('{}:{}'.format(ip, port))
        proxy_list.append('{}:{}'.format(ip, port))
    os.system('taskkill /f /im geckodriver.exe /T')
    return proxy_list
    
def get_new_proxy():
    global proxies
    print('{} proxies remaining'.format(len(proxies)))
    if len(proxies) == 0:
        logger.debug('Used up all proxies! Refreshing')
        proxies = get_proxies()
    return proxies.pop(int(random() * len(proxies)))
    

def get_proxy_dict(current_proxy):
    return { "https" : str(current_proxy) }


def random_string():
	j = ''
	for i in range(10):
		j += chr(int(random() * 100 + 34))
	return j


def main():
    global proxies
    proxies = get_proxies()
    proxy = get_proxy_dict(get_new_proxy())
    
    delay = 1.0
    
    s = requests.Session()
    
    for i in range(100):
            try:
                r = s.get('https://steamcommunity.com/market/priceoverview/?country=US&currency=1&appid=440&market_hash_name={}'.format(random_string()), proxies = proxy)
            except:
                proxy = get_proxy_dict(get_new_proxy())
                continue
            
            try:
                print(r.text)
                print(r.json())
            except Exception as e:
                print(e)
            sleep(delay)
        
main()
