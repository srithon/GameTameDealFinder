import requests

from time import sleep, time

import logging

import os

import json

import sys

from selenium import webdriver

from random import random


delay = 2.5


# TODO!!!! Bring back progress file
# so that you can sort the list and
# still come back!!



log_formatter = logging.Formatter('%(asctime)s %(levelname)s:%(name)s\t%(message)s',
                                  datefmt='%H:%M:%S')

log_handler = logging.FileHandler(filename='gametame_fill_market_data.log')
log_handler.setFormatter(log_formatter)

log_handler.setLevel(logging.DEBUG)

#  logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger('root_logger')

#  logging.getLogger('')
logger.addHandler(log_handler)

logger.setLevel(logging.DEBUG)

logger.info('Starting script...')

item_list = list()

point_price_list = list()

#  item_list_file.close()

real_price_list = list()

last_item = None

try:
    with open('item_list_file_active.txt', 'r') as file:
        for line in file:
            pass
        last_item = line
except KeyboardInterrupt as e:
    print('Exiting...')
    sys.exit()
except Exception as e:
    print(e)

print(last_item)

if last_item != None:
    try:
        with open("item_list_file_complete.txt", "r") as item_list_file:
            with open('point_price_list_file_complete.txt', 'r') as point_price_file:
                current = ''
                while current != last_item:
                    current = item_list_file.readline()
                    next(point_price_file)
                for line in item_list_file:
                    item_list.append(line)
                for line in point_price_file:
                    point_price_list.append(line)
    except Exception as e:
        print(e)
else:
    with open("item_list_file_complete.txt", "r") as item_list_file:
        for line in item_list_file:
            item_list.append(line.rstrip())

    with open('point_price_list_file_complete.txt', 'r') as point_price_file:
        for line in point_price_file:
            point_price_list.append(line.rstrip())

print('{}; {} points'.format(item_list[0], point_price_list[0]))

# sys.exit()

init_time = time()

s = None

proxies = list()

def save_lists():
    global real_price_list

    with open("real_price_list_file.txt", "a+") as real_price_list_file:
        for price in real_price_list:
            real_price_list_file.write(str(price))

    with open('item_list_file_active.txt', 'a+') as active_item_list_file:
        for item in item_list[:(len(real_price_list))]:
            active_item_list_file.write(item + '\n')

    with open('point_price_list_file_active.txt', 'a+') as active_point_price_file:
        for item in point_price_list[:(len(real_price_list))]:
            active_point_price_file.write(item + '\n')

    trim_lists()

def trim_lists():
    global item_list, real_price_list
    print('Last Item Saved - ' + item_list[len(real_price_list) - 1])
    del item_list[:len(real_price_list)]
    del point_price_list[:len(real_price_list)]
    real_price_list.clear()


def get_proxies():
    driver = webdriver.Firefox()
    driver.get('https://free-proxy-list.net/')
    search = driver.find_element_by_css_selector('#proxylisttable_filter > label:nth-child(1) > input:nth-child(1)')
    search.send_keys('elite proxy')
    sort_by_https = driver.find_element_by_css_selector('th.sorting:nth-child(7)') 
    sort_by_https.click()
    sleep(0.5)
    sort_by_https.click()
    sleep(1.0)
    proxies_body = driver.find_element_by_css_selector('#proxylisttable > tbody:nth-child(2)')
    proxies = proxies_body.find_elements_by_xpath('.//tr')
    print('{} proxies found in total'.format(len(proxies)))
    if len(proxies) == 0:
          print('No Proxies Found!')
          logger.e('No Proxies Found!')
          return None
    proxy_list = list()
    for proxy_element in proxies:
        ip = proxy_element.find_element_by_xpath('.//td[1]').text
        port = proxy_element.find_element_by_xpath('.//td[2]').text
        print('{}:{}'.format(ip, port))
        logger.info('{}:{}'.format(ip, port))
        proxy_list.append('{}:{}'.format(ip, port))
    os.system('taskkill /f /im geckodriver.exe /T')
    return proxy_list
    
def get_new_proxy():
    global proxies
    print('{} proxies remaining'.format(len(proxies)))
    if len(proxies) == 0:
        logger.debug('Used up all proxies! Refreshing')
        proxies = get_proxies()
        # TODO implement support for diff pages on proxy list site
        # because proxies will be used up
    return proxies.pop(int(random() * len(proxies)))
    

def get_proxy_dict(current_proxy):
    return { "https" : str(current_proxy) }


def main(delay):
    global init_time, item_list, real_price_list, s, proxies, active_item_list
    proxies = get_proxies()
    if proxies == None:
        logger.error('No proxies found!')
        sys.exit()
    proxy_dict = get_proxy_dict(get_new_proxy())
    s = requests.Session()
    init_time = time()
    counter = 0
    try:
        broken = True
        
        while broken:
            broken = False
            for i in range(len(item_list)):
                item = item_list[i]
                try:
                    r = s.get('https://steamcommunity.com/market/priceoverview/?country=US&currency=1&appid=440&market_hash_name=' + item, proxies = proxy_dict)
                    try:
                        price = float((r.json()['lowest_price'])[1:])
                        real_price_list.append(price)
                        print('( {} : {} )'.format(item, price))
                    except Exception as e:
                        print(e)
                        logger.error(e)
                        item_list.pop(i)
                        point_price_list.pop(i)
                        i -= 1
                        continue
                except KeyboardInterrupt as e:
                    print('Exiting...')
                    sys.exit()
                except:
                    logger.debug('Failed to get response. Retrying. item = {}'.format(item))
                    sleep(delay)
                    init_time += delay
                    continue
                sleep(delay)
                if 'null' in r.text:
                    print('null in source')
                    logger.error('NULL IN SOURCE')
                    logger.info('Counter = {}'.format(counter))
                    proxy_dict = get_proxy_dict(get_new_proxy())
                    i -= 1
                    continue
                counter += 1
                print('Completed iteration #{}'.format(counter))
                if (counter % 36 == 0):
                    print('Saving lists...')
                    logger.info('Saving lists...')
                    save_lists()
                    broken = True
                    break
            
    except Exception as e:
        print(e)
    return counter

last_count = 0

try:
    count = main(delay)
except Exception as e:
    print(e)

try:
    s.close()
except Exception as e:
    print(e)


final_time = time()
print('Time passed - {}'.format(final_time - init_time))
logger.info('Time passed - {}'.format(final_time - init_time))
logger.info('Counter = {}'.format(count))

s = None

log_handler.close()
