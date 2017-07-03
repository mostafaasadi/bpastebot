#!/usr/bin/env python3
# coding=utf-8

from telegram.ext import Updater,CommandHandler,MessageHandler, Filters ,ConversationHandler,InlineQueryHandler
from telegram import InlineQueryResultArticle, ParseMode,InputTextMessageContent
from uuid import uuid4
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
    update.message.reply_text('Hi, Give me your long text')
    return second

# get text and call paste function
def second(bot, update):
    # get text
    txt = update.message.text
    # get user name for author
    try:
        author = update.message.from_user.first_name + " " + update.message.from_user.last_name
    except Exception: 
        author = "Anonymous user"
    # call paste function
    url = paste(txt , author)
    # replay the url to user
    bot.sendMessage(chat_id=update.message.chat_id,reply_to_message_id=update.message.message_id,text=url)

# cancel function
def cancel(bot,update):
    bot.sendMessage(chat_id=update.message.chat_id,text="canceled")
# About function
def about(bot,update):
    abouttext = " @bpaste_bot is a Free Software that developed by Mostafa Asadi \n\n 🌐 https://github.com/mostafaasadi/bpastebot "
    bot.sendMessage(chat_id=update.message.chat_id,text=abouttext)

# inline respond function
def inlinequery(bot, update):
    query = update.inline_query.query
    results = list()
    # get ans send inline info to paste function
    def inlinepaste():
        try:
            author = update.inline_query.from_user.first_name + " " + update.inline_query.from_user.last_name
        except Exception: 
            author = "Anonymous user"
        url = paste(query,author)
        return url
    # add inline query to bot
    results.append(InlineQueryResultArticle(id=uuid4(),title="Paste it!" , description="put your text and click", thumb_url="http://url/beepastelogo.png", input_message_content=InputTextMessageContent(inlinepaste())))
    # update inline respond
    update.inline_query.answer(results)

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
dispatcher.add_handler(InlineQueryHandler(inlinequery))
dispatcher.add_handler(start_handler)
dispatcher.add_handler(second_handler)
dispatcher.add_handler(conv_handler)
dispatcher.add_handler(cancel_handler)
dispatcher.add_handler(about_handler)

# run
updater.start_polling()
updater.idle()
updater.stop()
