#!/usr/bin/env python3
# coding=utf-8

from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters ,ConversationHandler
import requests,json

# main function , paste to beepaste.io
def paste(text,author):
    # json data
    data = {'api-key': 'AAAAAAAAAAAAAAAAAAAA', 'pasteRaw': text, 'pasteLanguage': 'text', 'pasteTitle': 'My Paste', 'pasteAuthor': author + ' , From @bpaste_bot '}
    # request
    rp = requests.post('https://beepaste.io/api', json=data)
    # get url as json
    rpj = rp.json()
    url = rpj["url"]
    return url

# access  bot via token
updater = Updater(token='NNNNNNNNN:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
dispatcher = updater.dispatcher
second = 2

# start_handler function
def start(bot, update):
    update.message.reply_text('Hi, Get me your long text')
    return second

# get text and call paste function
def second(bot, update):
    # get text
    txt = update.message.text
    # get user name for author
    author = update.message.from_user.first_name + " " + update.message.from_user.last_name
    # call paste function
    url = paste(txt , author)
    # replay the url to user
    bot.sendMessage(chat_id=update.message.chat_id,text=url)

# cancel function
def cancel(bot,update):
    bot.sendMessage(chat_id=update.message.chat_id,text="canceled")
# About function
def about(bot,update):
    abouttext = " @bpaste_bot is a Free Software that developed by Mostafa Asadi \n\n 🌐 https://github.com/mostafaasadi/bpastebot "
    bot.sendMessage(chat_id=update.message.chat_id,text=abouttext)

# manage conversation
conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            second: [MessageHandler(Filters.text,second)],
             },
        fallbacks=[CommandHandler('cancel', cancel)])

# it handle start command
start_handler = CommandHandler('start', start)
# handle all text
second_handler = MessageHandler(Filters.text , second)
# handle cancel
cancel_handler = CommandHandler('cancel', cancel)
# handle cancel
about_handler = CommandHandler('about', about)

# handle dispatcher
dispatcher.add_handler(start_handler)
dispatcher.add_handler(second_handler)
dispatcher.add_handler(conv_handler)
dispatcher.add_handler(cancel_handler)
dispatcher.add_handler(about_handler)

# run
updater.start_polling()
updater.idle()
updater.stop()
