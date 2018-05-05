import requests
import threading
from balebot.filters import *
from balebot.handlers import *
from balebot.config import Config
from balebot.updater import Updater
from balebot.models.messages import *
from balebot.models.base_models import Peer
from requests.packages.urllib3.exceptions import InsecureRequestWarning


Config.real_time_fetch_updates = True
updater = Updater(token="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
dispatcher = updater.dispatcher
bot = updater.bot
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# get token
def tokenize():
    global headers
    threading.Timer(850, tokenize).start()

    try:
        tokenRequest = requests.post(
            'https://beepaste.io/api/v1/auth',
            headers={'Content-Type': 'application/json'}, verify=False)
        token_json = tokenRequest.json()
        if token_json['status'] == 'success':
            token = token_json['X-TOKEN']
            headers = {'X-TOKEN': token}
            print(headers)
            return True
    except Exception as e:
        print('\nError: ' + e)


# main function , paste to beepaste.io
def paste(text, author):
    data = {
        'raw': text,
        'title': 'A new paste',
        'author': author + ' via 🤖@BPaste_bot on Bale '
    }
    try:
        r = requests.post(
            'https://beepaste.io/api/v1/paste',
            headers=headers, json=data, verify=False)
    except Exception as e:
        print('\n\nE: ' + e + '\n\n')
    rj = r.json()
    if rj['status'] == 'success':
        rjp = rj['paste']
        return rjp
    else:
        print('E')
        return False
        tokenize()


# expand paste
@dispatcher.message_handler(
    filters=[
        TextFilter(pattern="https://beepaste.io/paste/view\S+"),
        TemplateResponseFilter()
    ])
def expand(bot, update):
    m = update.get_effective_message()
    pid = m.text.split('/')[5].split(' ')[0]

    try:
        r = requests.get(
            'https://beepaste.io/api/v1/paste/' + pid,
            headers=headers
        )
    except Exception as e:
        print(e)
    rj = r.json()
    if rj['status'] == 'success':
        res = '🔗 https://beepaste.io/paste/view/' + rj['paste']['uri'] + \
            '\n👤 ' + rj['paste']['author'] + \
            '\n```\n\n' + rj['paste']['raw'] + '\n```'
        bot.reply(update, res)
        return True
    else:
        return False
        tokenize()


@dispatcher.message_handler(DocumentFilter())
def download_file(bot, update):
    def final_download_success(result, user_data):
        stream = user_data.get("byte_stream", None)
        u = update.users[0].get_json_object()
        author = u['name']
        # call paste function
        p = paste(stream.decode('utf-8'), str(author))
        # replay the url to user
        res = '🔗 https://beepaste.io/paste/view/' + p['uri'] + \
            '\n🔗 ' + p['shorturl']
        bot.reply(update, res)

    user_id = update.body.sender_user.peer_id
    file_id = update.body.message.file_id
    bot.download_file(
        file_id=file_id,
        user_id=user_id,
        file_type="file",
        success_callback=final_download_success
    )


@dispatcher.command_handler('/start')
def conversation_starter(bot, update):
    message = TextMessage("سلام, یک متن طولانی یا یک فایل متنی بلند را برای من بفرستید تا آن را پیست کنم همچنین اگر لینک پیستی را برای  من بفرستید همینجا آن را می‌گشایم")
    user_peer = update.get_effective_user()
    bot.send_message(message, user_peer)


# About function
@dispatcher.command_handler('/about')
def about(bot, update):
    abouttext = "@BPaste_bot , Can Paste Long Text and File Content or Expand your Paste \n🆓 This Bot , Totaly Free , Libre and OpenSource \n       🌐 https://github.com/mostafaasadi/bpastebot "
    bot.reply(update, abouttext)


@dispatcher.message_handler(filters=[TextFilter()])
def text(bot, update):
    m = update.get_effective_message()
    u = update.users[0].get_json_object()
    author = u['name']
    p = paste(m.text, str(author))

    res = '🔗 https://beepaste.io/paste/view/' + p['uri'] + \
        '\n🔗 ' + p['shorturl']
    bot.reply(update, res)


def main():
    tokenize()
    updater.run()


if __name__ == '__main__':
    main()
