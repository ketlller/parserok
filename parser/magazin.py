import requests
import json
import random
from threading import Thread
from bs4 import BeautifulSoup
from pymongo import MongoClient
import datetime
import pymongo
import time
import smtplib
from email.mime.text import MIMEText
from email.header import Header


headers = {
	'Accept-Encoding': 'gzip, deflate, br',
	'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
	'Connection': 'keep-alive',
	'Cookie': '_ga=GA1.2.1135460412.1541230776; csrftoken=tMwBgCIgewSN9sHakkbnignqS39f0w4RZal1VIzpXl3KS5NBfWDKjptzfNgrNhI7; sessionid=6idwkbhrnv3s4io0uiaoaoj7w78k9dwx; caccpt=true; _gid=GA1.2.395715459.1541456265; _gat=1',
	'Host': 'lootdog.io',
	'Referer': 'https://lootdog.io/product/10072',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}

def send_notification(mesg):
	# настройки
	mail_sender = "yuepyvp89@mail.ru"
	mail_receiver = "yuepyvp89@mail.ru"
	username = "yuepyvp89@mail.ru"
	password = "12vfbkhehekbn"
	server = smtplib.SMTP('smtp.mail.ru:587')

	# тело письма
	subject = "Тестовое письмо от " + mail_sender
	body = mesg
	msg = MIMEText(body, 'plain', 'utf-8')
	msg['Subject'] = Header(subject, 'utf-8')

	# отправка письма 

	server.starttls()
	server.ehlo()
	server.login(username, password)
	server.sendmail(mail_sender, mail_sender, msg.as_string())
	server.quit()

def get_proxy():
	r = BeautifulSoup(requests.get('http://online-proxy.ru/').text, 'html5lib')
	result = []
	for row in r.find_all('tr'):
		try:
			if(row.find_all('td')[3].get_text() == 'HTTP' and row.find_all('td')[4].get_text() == 'ýëèòíûé' and int(row.find_all('td')[9].get_text()) < 20 ):
				result.append(row.find_all('td')[1].get_text()+':'+row.find_all('td')[2].get_text())
		except:
			pass

	return result		

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

def compare_names(all_old_names, all_new_names):
	for name in all_old_names:
		if(not (name in all_new_names)):
			send_notification('Из магазина пропал товар: '+name)

	for name in all_new_names:
		if(not (name in all_old_names)):
			send_notification('В магазине появился новый товар: '+name)

def get_overage_price(item_name):

	tod = datetime.datetime.now()
	d = datetime.timedelta(days = int(setings_parser['days_to_notification']))
	a = tod - d

	items = list(collection.find({
		'item_name': item_name, 	    
	    'date': {
	        '$gte': a,
	        '$lt': tod
	    }
	}))

	count = len(items)

	summary = 0
	e = 0
	for item in items:
		summary += int(list(item['prices'])[0])
		e = int(list(item['prices'])[0])

	if(count != 0):
		return int(summary/count)
	else:
		return 0


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
			
			try:
				current_price_item = prices[0]
			except:
				current_price_item = 0

			while True:
				try:
					sold_today = get_sold_today(item_id)
					if(sold_today != None):
						break
				except:
					pass

			# проверка цены за месяц

			post = {
				"item_id" : item_id,
				"game_name" : game_name,
				"item_name" : item_name,
				"count_on_sale_now" : count_on_sale_now,
				"prices" : prices,
				"sold_today" : sold_today,
				"date": datetime.datetime.utcnow()
			}

			# уведомление о цене
			overage_price_item = get_overage_price(item_name)
			percents_high = int(setings_parser['high_percents_to_notification'])
			percents_low = int(setings_parser['low_percents_to_notification'])	
			
			if(overage_price_item != 0):
				if((overage_price_item/current_price_item - 1) > percents_low/100):
					send_notification('товар '+item_name+' подорожал на '+str(overage_price_item/current_price_item - 1)+'%')
				elif((current_price_item/overage_price_item - 1) > percents_high/100):
					send_notification('товар '+item_name+' подешевел на '+str(current_price_item/overage_price_item - 1)+'%')
			else:
				pass


			collection.insert_one(post)


while True:
	
	print('собираю..')
	# получение прокси
	proxies = get_proxy()

	# mongooo
	client = MongoClient('localhost', 27017)
	db = client.lootdog
	collection = db.price_statistics
	settings_collection = db.settings_parser


	# получение всех товаров
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

	# main loop

	while True:

		# появление/пропажа товара из продажи
		all_old_names = settings_collection.find_one({'key': 'secret'})['last_names']
		all_new_names = [item["name"] for item in items]
		compare_names(all_old_names, all_new_names)

		# обновление имен товаров
		settings_collection.update_one({'key':"secret"},
			{
			'$set': {
		    	'last_names': all_new_names
			}
		}, upsert=False)

		# настройки парсера
		setings_parser = settings_collection.find_one({'key': 'secret'})
		
		# добавление товаров по кусочкам
		chunks = chunkIt(items, 20)
		for chunk in chunks:
			thread = ParserThread(chunk)
			thread.start()

		# задержка
		time.sleep(int(setings_parser['period_parsing'])*60)