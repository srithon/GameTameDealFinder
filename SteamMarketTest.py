from selenium import webdriver

from time import sleep, time

import logging

import os

log_formatter = logging.Formatter('%(asctime)s %(levelname)s:%(name)s\t%(message)s',
                                  datefmt='%H:%M:%S')

log_handler = logging.FileHandler(filename='steam_market_test.log')
log_handler.setFormatter(log_formatter)

log_handler.setLevel(logging.DEBUG)

#  logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger('root_logger')

#  logging.getLogger('')
logger.addHandler(log_handler)

logger.setLevel(logging.DEBUG)

logger.info('Starting script...')

item_list = list()

item_list_file = open("item_list_file.txt", "r")
    
for line in item_list_file:
    item_list.append(line.rstrip())

item_list_file.close()

init_time = 0

def main(delay_time):
    global init_time, item_list
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference("browser.privatebrowsing.autostart", True)
    firefox_profile.set_preference('permissions.default.stylesheet', 2)
    # Disable images
    firefox_profile.set_preference('permissions.default.image', 2)
    # Disable Flash
    firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so',
                                   'false')
    firefox_profile.set_preference('javascript.enabled', False)
    
    driver = webdriver.Firefox(firefox_profile=firefox_profile)
    init_time = time()
    counter = 0
    for item in item_list:
        try:
            driver.get('https://steamcommunity.com/market/priceoverview/?country=US&currency=1&appid=440&market_hash_name=' + item)
        except:
            sleep(1.0)
            init_time += 1.0
            continue
        sleep(delay_time)
        source = driver.page_source
        if 'null' in source:
            print('null in source')
            logger.error('NULL IN SOURCE')
            break
        counter += 1
        print('Completed iteration #{}'.format(counter))
    return counter

last_count = 0

for i in range(24, 80, 2):
    delay = i / 10.0
    print('delay = {}'.format(delay))
    logger.info('Current delay = {}'.format(delay))
    
    try:
        count = main(delay)
    except Exception as e:
        print(e)


    final_time = time()
    print('Time passed - {}'.format(final_time - init_time))
    logger.info('Time passed - {}'.format(final_time - init_time))
    logger.info('Counter = {}'.format(count))
    logger.info('\n')
    os.system('taskkill /f /im geckodriver.exe /T')
    sleep_time = 60.0 * delay
    print('Pausing for {}'.format(sleep_time))
    logger.info('Pausing for {}'.format(sleep_time))

    del item_list[:count]

    if len(item_list) < 800:
        item_list_file = open("item_list_file.txt", "r")
    
        for line in item_list_file:
            item_list.append(line.rstrip())

        item_list_file.close()

    if count - last_count > 50:
        print('Sleeping extra 5 minutes because delta count > 50')
        logger.info('Sleeping extra 5 minutes because delta count > 50')
        sleep(300)
    
    sleep(sleep_time)
