# -*- coding: utf-8 -*-
import redis
import os
import telebot
# import some_api_lib
# import ...

# Example of your code beginning
#           Config vars
token = os.environ['TELEGRAM_TOKEN']
some_api_token = os.environ['SOME_API_TOKEN']
#             ...

# If you use redis, install this add-on https://elements.heroku.com/addons/heroku-redis
r = redis.from_url(os.environ.get("REDIS_URL"))

#       Your bot code below

bot = telebot.TeleBot(token)


def gettingcats(message):
    try:
        bot.send_chat_action(message.chat.id, action='upload_document')
        r = requests.get('http://thecatapi.com/api/images/get?format=html&type=gif')
        match = re.search(r'src=[\'"]?([^\'" >]+)', r.text)
        mark = types.InlineKeyboardMarkup()
        moar = types.InlineKeyboardButton('More cats 😺', callback_data='MOAR')
        mark.add(moar)
        if match:
            bot.send_document(message.chat.id, match.group(0)[5:], reply_markup=mark)
    except:
        bot.send_message(message.chat.id, 'Something wrong with Cats 😿\nTry again')


@bot.callback_query_handler(func=lambda call: True)
def callback_buttons(call):
    if call.message:
        if call.data == "MOAR":
            gettingcats(call.message)
            bot.answer_callback_query(call.id)


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_chat_action(message.chat.id, action='typing')
    bot.send_message(message.chat.id, 'I am a CatBot and I send CatGifs. Write /cat and relax 😸')


@bot.message_handler(commands=['cat'])
def catbot(message):
    gettingcats(message)


bot.skip_pending = True
bot.polling(none_stop=True, interval=0)
#              ...
