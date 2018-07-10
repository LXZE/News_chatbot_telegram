#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO: make updater.idle() can customize sigint listener

from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import logging
import signal
import sys
import time

def readUserList():
	file = open('account.txt', 'r')
	tmp = list(map(lambda x: x[:-1], file.readlines()))
	file.close()
	return tmp

def writeUser(idList):
	file = open('account.txt', 'w')
	for id_elem in idList:
		print(id_elem)
		file.write('{}\n'.format(id_elem))

def notify(idList, updater):
	for id_elem in idList:
		updater.bot.send_message(chat_id = id_elem, text="I'm online!")

def start(bot, update):
	chat_id = update.message.chat_id
	if chat_id not in userList:
		userList.append(chat_id)
	print(chat_id)
	bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")

def text(bot, update):
	time_in = time.strftime('%Y-%m-%d %H:%M:%S')
	chat_id = update.message.chat_id
	if chat_id not in userList:
		userList.append(chat_id)
	print(chat_id)
	bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
	bot.send_message(chat_id=chat_id, text='You type: ' + update.message.text)
	bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
	time.sleep(2)
	bot.send_message(chat_id=chat_id, text='At time: ' + time_in)

def signal_handler(signal, frame):
	global updater
	global userList
	print('Exit...')
	writeUser(userList)
	if updater:
		updater.stop()
	sys.exit(0)


def main():
	signal.signal(signal.SIGINT, signal_handler)
	signal.signal(signal.CTRL_C_EVENT, signal_handler)

	logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
	userList = readUserList()

	token = '425529719:AAFKwKj_BWVECRT5EVeKEuekUkYlJlOmwrk'
	updater = Updater(token=token)
	# job_queue = updater.job_queue
	dp = updater.dispatcher

	start_handler = CommandHandler('start', start)
	dp.add_handler(start_handler)
	text_handler = MessageHandler(Filters.text, text)
	dp.add_handler(text_handler)

	notify(userList, updater)

	updater.start_polling()
	updater.idle()

if __name__ == '__main__':
    main()