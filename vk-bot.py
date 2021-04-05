import requests, aiohttp, asyncio, json, sys, logging, random

# Банальный Template для бота в вк 
#
# Использует Long Poll API 
#
# Async обработка событый
#
# P.S. Расписал вроде всё что можно было, даже примеры привёл, ссылаясь на документацию
# P.S.S. Не использую vk api для питона, потому что потому, что вы мне сделаете? а? м?
#
# Автор SAwckA, https://vk.com/sawcka


######ОПРЕДЕЛЕНИЕ ТОКЕНОВ и URL########
VK_API_URL = 'https://api.vk.com/method/'

GROUP_ID = #Ну тут понятно, id вашей группы(строка)

GROUP_TOKEN = # Ключ доступа сообщества, иструкци к получению: https://vk.com/dev/access_token?f=2.%20%D0%9A%D0%BB%D1%8E%D1%87%20%D0%B4%D0%BE%D1%81%D1%82%D1%83%D0%BF%D0%B0%20%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D1%81%D1%82%D0%B2%D0%B0
########### В ТОЙ ЖЕ ВКЛАДКЕ ЕСТЬ РАЗДЕЛ Long Poll API, в типах событий желательно указать то, что вам необходимо 

#######################################

#################LOGGING
HTTPlogging = True
LPlogging = True
########################


if HTTPlogging: 
	#Логи всех запросов HTTP
	logging.basicConfig(level=logging.DEBUG)



from concurrent.futures import ThreadPoolExecutor
_executor = ThreadPoolExecutor(10) #ПУЛ ДЛЯ ПОТОКОВ (ЧЕМ БОЛЬШЕ, ТЕМ БОЛЬШЕ ПОЛЬЗОВАТЕЛЕЙ МОЖНО ОБРАБОТАТЬ ОДНОВРЕМЕННО)



def get_longpoll_data(): 
	#Функция получения сервера longpoll
	#Подробнее: https://vk.com/dev/groups.getLongPollServer
	return json.loads(requests.get(f'{VK_API_URL}groups.getLongPollServer/?group_id={GROUP_ID}&access_token={GROUP_TOKEN}&v=5.69').content.decode('utf-8'))['response']





# Простой объект, в котором можно описать только нужные методы VK API 

# Полный список методов: https://vk.com/dev/methods
# Список методов messages: https://vk.com/dev/messages
# Список методов для фото: https://vk.com/dev/photos 
# 	|_Подробнее об upload server'e https://vk.com/dev/photos.getMessagesUploadServer
# 	|_P.S. Чтобы отправить фото, необходимо залить её на upload server и получить ссылку на картинку, которую потом прикрепить в attachment в message.send
# 	|
# 	|_	Пример как это можно сделать:
# 	|__		Получаем upload server 
# 	|			#def get_upload_server():
# 	|			#	r = requests.get('%sphotos.getMessagesUploadServer/'%(VK_API_URL), params = {
# 	|			#			'peer_id':0,
# 	|			#			'access_token':GROUP_TOKEN,
# 	|			#			'v':'5.126',
# 	|			#		})
# 	|			#	return json.loads(r.content.decode('utf-8'))
# 	|__		Отправляем на него фотку
# 	|			#def upload_photo(photo):
# 	|			#	serv_data = get_upload_server()['response']
# 	|			#	upload_url = serv_data['upload_url']
# 	|			#	request = requests.post(upload_url, files={'photo': open(photo, "rb")})
# 	|			#	params = {'server': request.json()['server'],
# 	|			#          'photo': request.json()['photo'],
# 	|			#          'access_token':GROUP_TOKEN,
# 	|			#          'hash': request.json()['hash'],
# 	|			#          'v':'5.126'}
# 	|			#	r = requests.get('%sphotos.saveMessagesPhoto/'%VK_API_URL, params=params)
# 	|			#	return json.loads(r.content.decode('utf-8'))['response']
# 	|__  Подробнее: https://vk.com/dev/photos.saveMessagesPhoto как это делать 

# Пример с методом /messages.send : 
# P.S. это лучше выносить в другой модуль, а здесь писать только минимальные вызовы 

# # class VKchat(): 
# # 	def __init__(self, user_id):
# # 		#Инициализация с user_id (участника беседы, к которому мы будем обращаться)
# # 		self.user_id = user_id

# # 	def send_text_message(self, message, keyboard = None):
# # 		#Отправка текстового сообщения
# # 		params = {

# # 			'user_id':self.user_id,
# # 			'peer_id':self.user_id,
# # 			'message':str(message),
# # 			'access_token': GROUP_TOKEN,
# # 			'v':'5.103',
# # 			'keyboard': keyboard,
# # 			'random_id': random.randint(1, 2**31 - 1)

# # 		}

# # 		r = requests.get(f'{VK_API_URL}messages.send/', params = params)
# # 		return r.content.decode('utf-8')











def your_sync_main_func(args):
	#Функция основного кода (ниже пример для класса сверху для отправки сообщения с объектом, полученным от сервера)
	# chat = VKchat(args['object']['user_id'])
	# chat.send_text_message(args)
	print(args)




















async def entry_func(args):
	#Точка входа для синхронной функции, которая кидается в поток 
	return_ = await loop.run_in_executor(_executor, your_sync_main_func, args)
	return return_


async def longpoll_loop(): 
	#Асинхронный цикл longpoll сервера
	session = aiohttp.ClientSession() #Сессия для запросов


	"""определение параметров для запросов на longpoll сервер"""
	LPkey, LPserver, LPts = get_longpoll_data().values()
	LPtimeout = 30 #Таймаут ответа сервера, 30 более-менее оптимальное значение
	"""======================================================"""

	while True:
		#Цикл запросов
		try:
			# Запрос на longpoll server
			# Подробнее: https://vk.com/dev/bots_longpoll
			r = await session.get(f'{LPserver}?act=a_check&key={LPkey}&ts={LPts}&wait=25&mode=2&version=3', timeout = LPtimeout) 
			
			json_r = json.loads(await r.text())


			if LPlogging: 
				#Логи для ответов longpoll сервера
				print(json_r)

			if json_r['updates'] != []: #Получаем список событий, пришедших от сервера 

				for item in json_r['updates']: #item - элемент (одно конкретное) событие, для обработки каждного из которых будем вызывать функцию обработки в потоке


					if item['type'] == 'message_new':
						# В данном случае обрабатываем событие message_new (входящее сообщение)

						loop.create_task(entry_func(item)) #Точка входа 


					"""
						Дополняется в зависимости от типа события
						Тип событий: https://vk.com/dev/groups_events

					"""


			LPts = json_r['ts'] #перезаписываем тс, потому что получили обновление (он нужен для определения последнего события сервером)

			session.close() #Закрваем сессию, чтобы они не наслаивались друг на друга 
		except: #Если произошла ошибка на longpoll сервере, то необходимо получить данные для нового сервера
			LPkey, LPserver, LPts = get_longpoll_data().values()

#Запускаем асинхронный цикл 
loop = asyncio.get_event_loop()
loop.run_until_complete(longpoll_loop())
