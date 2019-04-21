import requests

from requests.exceptions import ProxyError

from time import sleep



delay = 2.5



s = requests.Session()

params = { "text" : 'decal tool', "conversion" : "440" }

proxy = {'https' : ''}

s.get('https://backpack.tf/market_search', params = params, proxies = proxy)

try:
	print(s.json())
except ProxyError:
	print('ProxyError')

print(s.text)