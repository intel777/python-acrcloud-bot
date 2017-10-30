import vk, time, datetime, requests, os, base64, hmac, hashlib, os, sys, traceback
token = ''
com_token = ''
arc_access_key = ''
arc_access_secret = ''
arc_requrl = ''
acr_http_method = ""
acr_http_uri = ""
acr_data_type = ""
acr_signature_version = ""
auido_maxlength = 45
message_err = '¯\_(ツ)_/¯'
message_err_long = 'Длина аудио превышает рекомендуемый размер в 45 секунд.'
message_err_notfound = 'К сожалению, аудиозапись не распознана. Попробуйте поднести микрофон ближе к источнику звука, или записать более длинный отрывок.'
message_err_notaudiomessage = 'Это не аудиосообщение. Обработка прервана.'
message_err_linknotfound = 'Невозможно получить ссылку на аудиозапись. Обработка прервана.'

com_session = vk.AuthSession(access_token = com_token)
api = vk.API(com_session, v=5.64)
audio_session = vk.AuthSession(access_token = token)
audio_api = vk.API(audio_session, v=5.64)

print('Started.')
while True:
	try:
		clock_now = datetime.datetime.now()
		current_time = clock_now.strftime('%H:%M:%S')
		current_date = clock_now.strftime('%d.%m.%y')
		msg_pool = api.messages.getDialogs(unread = 1, count = 10)
		for msg in msg_pool['items']:
			print('[ACRCloud][{}][{}]Request from {}'.format(current_date, current_time, msg['message']['user_id']))
			user_id = msg['message']['user_id']
			link = ''
			attachment = []
			print(' Searching forwarded messages...')
			fwd_counter = 0
			while True:
				if('fwd_messages' in msg['message']):
					fwd_counter += 1
					print('  Found {} message included'.format(fwd_counter))
					msg['message'] = msg['message']['fwd_messages'][0]
				else:
					print('  Search Done.')
					break
			print(' Searching link on document...')
			msg = msg['message']
			if('attachments' in msg):
				if(msg['attachments'][0]['type'] == 'doc'):
					print('  Type: Doc')
					if(msg['attachments'][0]['doc']['type'] == 5):
						print('  Found audiomessage')
						if(msg['attachments'][0]['doc']['preview']['audio_msg']['duration'] <= auido_maxlength):
							print('  Duration <= 45')
							link = msg['attachments'][0]['doc']['preview']['audio_msg']['link_mp3']
						else:
							print('  Duration is > 45. Aborting...')
							api.messages.send(user_id = user_id, message = message_err_long)
							continue
					else:
						print('  Not audiomessage. Aborting...')
						api.messages.send(user_id = user_id, message = message_err_notaudiomessage)
						continue
				elif(msg['attachments'][0]['type'] == 'audio'):
					print('  Type: Audio')
					if(msg['attachments'][0]['audio']['duration'] <= auido_maxlength):
						print('   Duration is <= 45')
						try:
							link = msg['attachments'][0]['audio']['url']
						except Exception:
							print('   Unable to get link, maybe regional limited.')
							api.messages.send(user_id = user_id, message = message_err_linknotfound)
							continue
					else:
						print('   Duration is > 45. Aborting...')
						api.messages.send(user_id = user_id, message = message_err_long)
						continue
				else:
					print('   No attachments with needed type detected. Aborting with message_err...')
					api.messages.send(user_id = user_id, message = message_err)
					continue
			else:
				print('   No attachments detected. Aborting...')
				api.messages.send(user_id = user_id, message = message_err)
				continue
			print(' Link found. Downloading audio...')
			audio_message = requests.get(link)
			with open('sample.mp3', 'wb') as audiofile:
				audiofile.write(audio_message.content)
				audiofile.close()
			print(' Sending on recognition...')
			timestamp = time.time()
			string_to_sign = acr_http_method+"\n"+acr_http_uri+"\n"+arc_access_key+"\n"+acr_data_type+"\n"+acr_signature_version+"\n"+str(timestamp)
			sign = base64.b64encode(hmac.new(bytearray(arc_access_secret, 'utf-8'), bytearray(string_to_sign, 'utf-8'), hashlib.sha1).digest())
			sample_file = open('sample.mp3', 'rb')
			sample_bytes = os.path.getsize('sample.mp3')
			arc_files = {'sample': sample_file}
			arc_data = {'access_key': arc_access_key, 'sample_bytes': sample_bytes, 'timestamp': str(timestamp), 'signature': sign, 'data_type': acr_data_type, "signature_version": acr_signature_version}
			response = requests.post(arc_requrl, files = arc_files, data = arc_data)
			response.encoding = 'utf-8'
			recognition_result = response.json()
			if(recognition_result['status']['code'] == 0):
				print('  Response OK, processing...')
				try:
					artist = recognition_result['metadata']['music'][0]['artists'][0]['name']
				except Exception:
					print('   Unable to get Artist')
					artist = 'Неизвестно'
				try:
					title = recognition_result['metadata']['music'][0]['title']
				except Exception:
					print('   Unable to get Title')
					title = 'Неизвестно'
				try:
					genres = recognition_result['metadata']['music'][0]['genres'][0]['name']
				except Exception:
					print('   Unable to get Genres')
					genres = 'Неизвестно'
				try:
					date = recognition_result['metadata']['music'][0]['release_date']
				except Exception:
					print('   Unable to get Release Date')
					date = 'Неизвестно'
			else:
				print('  Error on ACRCloud. Aborting...')
				api.messages.send(user_id = user_id, message = message_err_notfound)
				continue
			songname = artist + ' - ' + title
			print(' Searching song in VK Database...')
			try:
				song_database = audio_api.audio.search(q = songname, count = 1)
				if(len(song_database['items']) != 0):
					print('  Audio found, adding to attachment...')
					attachment.append('audio{}_{}'.format(song_database['items'][0]['owner_id'], song_database['items'][0]['id']))
				else:
					print('  Audio not found. Not critical, processing...')
			except Exception:
				print('   Error while getting audio. Not critical, processing...')
			print(' All done, sending response...')
			response_text = '{}<br>Жанр: {}<br>Дата выхода: {}'.format(songname, genres, date)
			api.messages.send(user_id = user_id, message = response_text, attachment = attachment)
			time.sleep(0.3)
	except Exception as send_error:
		if(str(send_error)[0:3] == '901'):
			print('API Error. User denied message send. Deleting task...')
			api.messages.deleteDialog(peer_id = user_id)
			continue
		elif(str(send_error)[0:2] == '10'):
			print('API Error. VK Internal server error. Retrying...')
			continue
		elif('Read timed out' in str(send_error)):
			print('API Error. Connection timed out. Retrying...')
			continue
		else:
			print('Unknown Error Occured. Retrying...')
			continue
	time.sleep(1)