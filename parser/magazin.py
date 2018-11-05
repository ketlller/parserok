import requests
import json
import random
from threading import Thread
from bs4 import BeautifulSoup
from pymongo import MongoClient
import datetime
import pymongo


headers = {
	'Accept-Encoding': 'gzip, deflate, br',
	'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
	'Connection': 'keep-alive',
	'Cookie': '_ga=GA1.2.1135460412.1541230776; csrftoken=tMwBgCIgewSN9sHakkbnignqS39f0w4RZal1VIzpXl3KS5NBfWDKjptzfNgrNhI7; sessionid=6idwkbhrnv3s4io0uiaoaoj7w78k9dwx; caccpt=true; _gid=GA1.2.395715459.1541456265; _gat=1',
	'Host': 'lootdog.io',
	'Referer': 'https://lootdog.io/product/10072',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}

proxies = ['94.250.249.190:80',
'109.195.36.195:3128',
'91.239.89.60:3128',
'77.94.111.238:8080',
'195.208.172.70:8080',
'89.109.233.227:8080',
'79.172.32.2:3128',
'91.144.167.217:8080',
'91.221.200.106:53281',
'91.144.147.46:8080',
'88.147.142.25:8080',
'91.213.23.110:8080',
'78.41.101.200:3128',
'94.242.58.108:1448',
'185.22.172.94:10010',
'185.22.174.65:1448',
'185.22.172.94:1448',
'94.242.58.142:10010',
'94.242.57.136:10010',
'185.22.174.65:10010',
'185.22.174.69:10010',
'94.242.58.108:10010',
'94.242.58.14:10010',
'94.242.57.136:1448',
'94.242.58.14:1448',
'94.242.59.135:1448',
'94.242.59.135:10010',
'94.242.58.142:1448',
'94.242.55.108:10010',
'94.242.55.108:1448',
'195.211.197.125:8000',
'94.242.59.245:1448',
'94.79.52.207:8080',
'188.128.72.26:8080',
'46.235.71.241:8080',
'46.63.162.171:8080',
'185.22.174.69:1448',
'212.46.210.248:8080',
'188.0.171.182:8080',
'85.236.182.44:8080',
'88.87.72.72:8080',
'37.228.89.215:80',
'91.206.19.193:8081',
'185.148.220.11:8081']	
		

def chunkIt(seq, num):
	avg = len(seq) / float(num)
	out = []
	last = 0.0

	while last < len(seq):
		out.append(seq[int(last):int(last + avg)])
		last += avg

	return out


def get_prices(item_id):
	proxy = {
		'http': random.choice(proxies)
	}
	r = requests.get('https://lootdog.io/api/orders/?format=json&product='+str(item_id)+'&page=1&limit=5&is_buy=false&user=all&sorting=price', headers=headers, proxies=proxy).text
	items = json.loads(r)['results']
	prices = [item['buy_price']['amount'] for item in items]
	return prices

def get_sold_today(item_id):
	proxy = {
		'http': random.choice(proxies)
	}
	r = requests.get('https://lootdog.io/api/products/'+str(item_id)+'/market_info/?format=json&id='+str(item_id), headers=headers, proxies=proxy).text
	return json.loads(r)['sold_today']


class ParserThread(Thread):
	
	def __init__(self, myGoods):
		Thread.__init__(self)
		self.myGoods = myGoods
	
	def run(self): 
		for good in self.myGoods:
			item_id = good['id']
			
			try:
				game_name = good['game']['name']
			except:
				game_name = ''
			item_name = good['name']
			count_on_sale_now = good['on_sale_count']
			
			while True:
				try:
					prices = get_prices(item_id)
					if(prices != None):
						break
				except:
					pass
			
			
			while True:
				try:
					sold_today = get_sold_today(item_id)
					if(sold_today != None):
						break
				except:
					pass

			post = {
				"item_id" : item_id,
				"game_name" : game_name,
				"item_name" : item_name,
				"count_on_sale_now" : count_on_sale_now,
				"prices" : prices,
				"sold_today" : sold_today,
				"date": datetime.datetime.utcnow()
			}

			collection.insert_one(post)

for i in range(100):

	while True:
		try:
			proxy = {
				'http': random.choice(proxies)
			}
			items = json.loads(requests.get('https://lootdog.io/api/products/?format=json&search=&on_sale=1&game=&price_min=&price_max=&kind=&sorting=popular&page=1&limit=1000000', headers=headers, proxies=proxy).text)['results']
			if(items != None):
				break
		except:
			pass

	chunks = chunkIt(items, 20)
	# mongooo

	client = MongoClient('localhost', 27017)
	db = client.lootdog
	collection = db.price_statistics


	for chunk in chunks:
		thread = ParserThread(chunk)
		thread.start()




