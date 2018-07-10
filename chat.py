import random as r
import time
import rss_crawler

greet_Checklist = ['hello', 'hi', 'sup', 'greetings', 'hola', 'yo']
news_request_Checklist = ['update', 'new', 'news', 'anything', 'about', 'highlight', 'hot', 'today', 'happen']
accept_Checklist = ['one', 'this', 'show', 'display', 'pick']
def check_type(raw_sentence):
	for token in rss_crawler.clean(raw_sentence).split(' ')[::-1]:
		if token in greet_Checklist:
			return 'greet'
		elif token in news_request_Checklist:
			return 'request'
		elif token in accept_Checklist:
			return 'select'
	return 'unknown'

def findTopic(raw_sentence):
	doc = rss_crawler.clean(raw_sentence)
	token = doc.split(' ')
	if 'today' in token:
		token.remove('today')
	if 'about' in token:
		idx = token.index('about')
		topic = token[idx+1:]
	else:
		topic = [token[-1]]

	return ' '.join([t for t in topic if t not in greet_Checklist+news_request_Checklist+accept_Checklist])

def greet():
	return r.choice(greet_Checklist) + '!'

def getNews(input_text, topic):
	result = ''
	timeRead = ''
	with open('last.txt', 'r') as f:
		timeRead = f.readline()
		f.close()

	if time.time() - float(timeRead) > (60*1):
		print('update crawling')
		result = rss_crawler.crawl(topic,5)
	else:
		result = rss_crawler.query(topic, 5)

	res = ''
	if len(result) == 0:
		return 'There is no news related to "{}" in our database now'.format(topic)
	res += 'Here is news related to {}\n\n'.format(topic)
	for idx, entry in enumerate(result):
		res += '{}: {}\n'.format(idx+1, entry['title'])
		if idx != len(result)-1:
			res += ('-'*10) + '\n'
	return res

def selectNews(raw_sentence, topic):

	result = rss_crawler.query(topic, 5)
	idxLists = [
		['first', 'one', '1'],
		['second', 'two', '2'],
		['third', 'three', '3'],
		['fourth', 'four', '4'],
		['fifth', 'five', '5'],
		['last', 'lastest', '0']
	]
	try:
		tokens = rss_crawler.clean(raw_sentence).split(' ')
		idx = 0
		for token in tokens:
			for idxList in idxLists[::-1]:
				if token in idxList:
					idx = int(idxList[-1]) - 1
					if idx != 0:
						if 'one' in tokens:
							tokens.remove('one')
		print(idx)
		try:
			txt = 'Title: {}\n\n{}'.format(result[idx]['title'], result[idx]['content'])
			txt += '\n\nLinks: {}'.format(result[idx]['link'])
			return txt
		except IndexError:
			raise Exception('Index not found')
	except KeyError:
		raise Exception('key not found')

def chat(input_text, topic):

	type_input = check_type(input_text)
	print(type_input, topic)

	if type_input == 'greet':
		return ['greet', greet(), topic]

	elif type_input == 'request':
		# if topic == '':
		newTopic = findTopic(input_text)
		if newTopic != '':
			topic = newTopic

		if topic != '':
			return ['request', getNews(input_text, topic), topic]
		else:
			return ['error', 'Topic not found', topic]

	elif type_input == 'select':
		try:
			if topic == '':
				raise Exception('topic not found')
			return ['select' ,selectNews(input_text, topic), topic]
		except Exception as e:
			print(e)
			return ['error', 'Topic not found', topic]

	else:
		return ['unknown', 'I\'m don\'t understand', topic]