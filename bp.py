#!/usr/bin/env python3
# coding=utf-8

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
    ConversationHandler, InlineQueryHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent
from uuid import uuid4
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import tempfile

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# get token
def tokenize(bot, job):
    global headers

    try:
        tokenRequest = requests.post(
            'https://beepaste.io/api/v1/auth',
            headers={'Content-Type': 'application/json'}, verify=False)
        token_json = tokenRequest.json()
        if token_json['status'] == 'success':
            token = token_json['X-TOKEN']
            headers = {'X-TOKEN': token}
    except Exception as e:
        print('\nError: ' + e)


# main function , paste to beepaste.io
def paste(text, author):
    data = {
        'raw': text,
        'title': 'A new paste',
        'author': author + ' via @BPaste_bot 🤖'
    }
    try:
        r = requests.post(
            'https://beepaste.io/api/v1/paste',
            headers=headers, json=data, verify=False)
    except Exception as e:
        print(e)
    rj = r.json()
    if rj['status'] == 'success':
        rjp = rj['paste']
        return rjp
    else:
        return False
        tokenize()


# access  bot via token
updater = Updater(token='AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
dispatcher = updater.dispatcher
second = 2

# start_handler function
def start(bot, update):
    update.message.reply_text('Hi, Give me your long text or send me your file')
    return second


# get file and paste
def filef(bot, update):
    # get file id
    file = bot.getFile(update.message.document.file_id)
    # create a randon temp file name
    tf = tempfile.mkstemp()
    # download file
    file.download(tf[1])
    # read file content
    try:
        tfco = open(tf[1], "r")
        tfc = tfco.read()
        tfco.close()
    except Exception as e:
        # if it is not text file
        bot.sendMessage(
            chat_id=update.message.chat_id,
            reply_to_message_id=update.message.message_id,
            text=" ⚠️ Please send me a text file")

    # get user name for author
    try:
        author = update.message.from_user.first_name + " " \
            + update.message.from_user.last_name
    except Exception:
        author = "Anonymous user"
    # call paste function
    p = paste(tfc, author)
    # replay the url to user
    bot.sendMessage(
        chat_id=update.message.chat_id,
        reply_to_message_id=update.message.message_id,
        text='🔗 https://beta.beepaste.io/paste/view/' + p['uri'] + \
            '\n🔗 ' + p['shorturl']
    )


def second(bot, update):
    # get text
    txt = update.message.text
    # get user name for author
    try:
        author = update.message.from_user.first_name + " " + \
            update.message.from_user.last_name
    except Exception:
        author = "Anonymous user"

    # call paste function
    p = paste(txt, author)
    # replay the url to user
    bot.sendMessage(
        chat_id=update.message.chat_id,
        reply_to_message_id=update.message.message_id,
        text='🔗 https://beta.beepaste.io/paste/view/' + p['uri'] + \
            '\n🔗 ' + p['shorturl']
    )


# cancel function
def cancel(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="canceled")


# About function
def about(bot, update):
    abouttext = "@BPaste_bot , Can Paste Long Text and File Content In Groups and Private Chats , Via inline Mode Or Directly  \n🆓 This Bot , Totaly Free , Libre and OpenSource \n       🌐 https://github.com/mostafaasadi/bpastebot "
    bot.sendMessage(chat_id=update.message.chat_id, text=abouttext)


# inline respond function
def inlinequery(bot, update):
    query = update.inline_query.query
    results = list()

    try:
        author = update.inline_query.from_user.first_name + " " + \
            update.inline_query.from_user.last_name
    # set name for Anonymous user
    except Exception:
        author = "Anonymous user"

    # add inline query to bot
    # inline mode for zero character
    if len(query) == 0:
        results.clear()
        results.append(InlineQueryResultArticle(
            id=uuid4(),
            title=" ▶️ Beepaste",
            description="type some text less than 256 character inline mode",
            url="t.me/bpaste_bot",
            thumb_url="http://mostafaasadi.ir/bots/beepastelogo.png",
            input_message_content=InputTextMessageContent(
                "BPaste, paste your world! \n@bpaste_bot")))
    # inline mode for long text
    elif len(query) > 255:
        results.clear()
        results.append(InlineQueryResultArticle(
            id=uuid4(),
            title=" Sorry! 😞",
            description=" ⚠️ We can't get long long text in inline mode, send it directly",
            url="t.me/bpaste_bot",
            thumb_url="http://mostafaasadi.ir/bots/beepastelogo.png",
            input_message_content=InputTextMessageContent(
                "We can't get so long text in inline mode, send it directly, @bpaste_bot")))
    # inline mode for normal text
    else:
        results.clear()
        p = paste(query, author)
        results.append(InlineQueryResultArticle(
            id=uuid4(),
            title=" ✅ Pasted!",
            description=" pasted with this link",
            url=p['shorturl'],
            thumb_url="http://mostafaasadi.ir/bots/beepastelogo.png",
            input_message_content=InputTextMessageContent(
                '🔗 https://beta.beepaste.io/paste/view/' + p['uri'] + \
                '\n🔗 ' + p['shorturl'])))
    # update inline respond
    update.inline_query.answer(results)


def main():
    # manage conversation
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            second: [MessageHandler(Filters.text, second)]},
        fallbacks=[CommandHandler('cancel', cancel)])

    # it handle start command
    start_handler = CommandHandler('start', start)
    # handle all text
    second_handler = MessageHandler(Filters.text, second)

    filef_handler = MessageHandler(Filters.document, filef)
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
    dispatcher.add_handler(filef_handler)
    j = updater.job_queue
    j.run_repeating(tokenize, interval=840, first=0)
    # run
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
