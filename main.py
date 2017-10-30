from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import vk, datetime, time, requests, os, base64, hmac, hashlib, os, sys, traceback
import logging
#logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

tg_token = ''
vk_token = ''
arc_access_key = ''
arc_access_secret = ''
arc_requrl = ''
acr_http_method = ""
acr_http_uri = ""
acr_data_type = ""
acr_signature_version = ""

session = vk.AuthSession(access_token = vk_token)
vkapi = vk.API(session, v=5.64)

all_requests = 0
all_success = 0
all_with_audio = 0

def start(bot, update):
	now_clock = datetime.datetime.now()
	now_time = now_clock.strftime('%H:%M:%S')
	now_date = now_clock.strftime('%d.%m.%y')
	print('[ACRCloudTelegram][{}][{}]Start request from {}'.format(now_date, now_time, update.effective_user['username']))
	update.message.reply_text('Just send me audiomessage and I will recognize it!')

def voicemessage(bot, update):
	now_clock = datetime.datetime.now()
	now_time = now_clock.strftime('%H:%M:%S')
	now_date = now_clock.strftime('%d.%m.%y')
	print('[ACRCloudTelegram][{}][{}]Audiomessage from {}'.format(now_date, now_time, update.effective_user['username']))
	file_id = update.message.voice['file_id']
	print(' FileID get, downloading file...')
	response = requests.get('https://api.telegram.org/bot{}/getFile?file_id={}'.format(tg_token, file_id))
	filepath = response.json()['result']['file_path']
	filedata = requests.get('https://api.telegram.org/file/bot{}/{}'.format(tg_token, filepath))
	with open('sample.mp3', 'wb') as audiofile:
		audiofile.write(filedata.content)
		audiofile.close()
	print(' File get, recognizing...')
	timestamp = time.time()
	string_to_sign = acr_http_method+"\n"+acr_http_uri+"\n"+arc_access_key+"\n"+acr_data_type+"\n"+acr_signature_version+"\n"+str(timestamp)
	sign = base64.b64encode(hmac.new(bytearray(arc_access_secret, 'utf-8'), bytearray(string_to_sign, 'utf-8'), hashlib.sha1).digest())
	sample_file = open('sample.mp3', 'rb')
	sample_bytes = os.path.getsize('sample.mp3')
	arc_files = {'sample': sample_file}
	arc_data = {'access_key': arc_access_key, 'sample_bytes': sample_bytes, 'timestamp': str(timestamp), 'signature': sign, 'data_type': acr_data_type, "signature_version": acr_signature_version}
	response = requests.post(arc_requrl, files = arc_files, data = arc_data)
	sample_file.close()
	response.encoding = 'utf-8'
	recognition_result = response.json()
	if(recognition_result['status']['code'] == 0):
		print('  Response OK, processing...')
		try:
			artist = recognition_result['metadata']['music'][0]['artists'][0]['name']
		except Exception:
			print('   Unable to get Artist')
			artist = 'Unknown'
		try:
			title = recognition_result['metadata']['music'][0]['title']
		except Exception:
			print('   Unable to get Title')
			title = 'Unknown'
		try:
			genres = recognition_result['metadata']['music'][0]['genres'][0]['name']
		except Exception:
			print('   Unable to get Genres')
			genres = 'Unknown'
		try:
			date = recognition_result['metadata']['music'][0]['release_date']
		except Exception:
			print('   Unable to get Release Date')
			date = 'Unknown'
	else:
		print('  Cannot recognize audio. Aborting...')
		update.message.reply_text('Cannot recognize audio. Try to make music louder or get microphone closer to source.')
		return 0
	songname = artist + ' - ' + title
	print(' Sending text response...')
	response_text = '{}\nGenre: {}\nRelease Date: {}'.format(songname, genres, date)
	update.message.reply_text(response_text)
	print(' Searching song in VK Database...')
	try:
		song_database = vkapi.audio.search(q = songname, count = 10)
		if(len(song_database['items']) != 0):
			print('  Song found, trying to get URL...')
			url = song_database['items'][0]['url']
			print('   URL Get, downloading...')
			audio_data = requests.get(url)
			with open('{} - {}.mp3'.format(artist, title), 'wb') as resultaudio:
				resultaudio.write(audio_data.content)
			print('  Audio get. Uploading response...')
			music = open('{} - {}.mp3'.format(artist, title), 'rb')
			update.message.reply_audio(audio= music)
			music.close()
			print('  All done. Cleaning up...')
			os.remove('{} - {}.mp3'.format(artist, title))
			os.remove('sample.mp3')
		else:
			print('  Song not found. Skip...')
	except Exception:
		print('  Cannot get song, Non critical, done.')
		exc_type, exc_value, exc_traceback = sys.exc_info()
		lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
		traceback_str = ''.join(line for line in lines)
		print(traceback_str)

updater = Updater(tg_token)

audiomessagehandler = MessageHandler(Filters.voice, voicemessage)


updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(audiomessagehandler)

updater.start_polling()
updater.idle()