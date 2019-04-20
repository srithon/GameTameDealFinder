import requests

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

s = None

def main(delay_time):
    global init_time, item_list, s
    s = requests.Session()
    init_time = time()
    counter = 0
    try:
        for item in item_list:
            try:
                r = s.get('https://steamcommunity.com/market/priceoverview/?country=US&currency=1&appid=440&market_hash_name=' + item)
                print(r.text)
            except:
                sleep(delay_time)
                init_time += delay_time
                continue
            sleep(delay_time)
            if 'null' in r.text:
                print('null in source')
                logger.error('NULL IN SOURCE')
                break
            counter += 1
            print('Completed iteration #{}'.format(counter))
    except Exception as e:
        print(e)
    return counter

last_count = 0

for i in range(3000, 4500, 200):
    delay = i / 100.0
    print('delay = {}'.format(delay))
    logger.info('Current delay = {}'.format(delay))
    
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
    logger.info('\n')
    sleep_time = 30.0 * (delay * delay)
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
        logger.info('Sleeping extra 30 minutes because delta count > 50')
        sleep(1800)
    elif count == 0:
        print('Count is 0; ending execution')
        logger.info('Count is 0; ending execution')
        break
    
    sleep(sleep_time)

    s = None
