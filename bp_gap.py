import re
import json
import gappy
import requests
import threading
from flask import Flask
from flask import request
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

TOKEN = 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAa'
ip = 'server public ip'

bot = gappy.Bot(TOKEN)
app = Flask(__name__)

regexp = re.compile(r"https://beepaste.io/paste/view\S+")


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
        'author': author + ' via 🤖@BPaste_bot on Gap '
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


@app.route('/', methods=['POST'])
def parse_request():
    msg = request.form
    chat_id = msg['chat_id']
    try:
        who = json.loads(msg['from'])
        user = who['name']
    except Exception:
        user = 'Anonymous user'
    if msg['type'] == 'text':
        if regexp.search(msg['data']):
            pid = msg['data'].split('/')[5].split(' ')[0]
            try:
                r = requests.get(
                    'https://beepaste.io/api/v1/paste/' + pid,
                    headers=headers
                )
            except Exception as e:
                print(e)
            rj = r.json()
            if rj['status'] == 'success':
                res = '🔗 https://beepaste.io/paste/view/' + \
                    rj['paste']['uri'] + '\n👤 ' + rj['paste']['author'] + \
                    '\n\n' + rj['paste']['raw']
                bot.send_text(chat_id, res)
                return True
            else:
                return False
                tokenize()
        else:
            p = paste(msg['data'], user)
            res = '🔗 https://beepaste.io/paste/view/' + p['uri'] + \
                '\n🔗 ' + p['shorturl']
            bot.send_text(chat_id, res)
    elif msg['type'] == 'file':
        data = json.loads(msg['data'])
        rg = requests.get(data['path'], allow_redirects=True)
        p = paste(str(rg.content.decode('utf-8')), user)
        res = '🔗 https://beepaste.io/paste/view/' + p['uri'] + \
            '\n🔗 ' + p['shorturl']
        bot.send_text(chat_id, res)
    return True


if __name__ == '__main__':
    tokenize()
    app.run(host=ip)
