# -*- coding: utf-8 -*-
import redis
import os
import telebot
import threading
import schedule
import telebot
import secrets
from pyowm.utils.config import get_default_config
from pyowm import OWM
import time
import logging
from time import sleep
import sys
import emoji
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters



# Example of your code beginning
#           Config vars
token = os.environ['TELEGRAM_TOKEN']
some_api_token = os.environ['SOME_API_TOKEN']
#             ...

# If you use redis, install this add-on https://elements.heroku.com/addons/heroku-redis
r = redis.from_url(os.environ.get("REDIS_URL"))

updater = Updater(token = '2003845994:AAEG-E_eVjh0J9bk25RgY4AYnrYHa1adZJI', use_context = True)
dispatcher = updater.dispatcher
logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO)

TOKEN = "2003845994:AAEG-E_eVjh0J9bk25RgY4AYnrYHa1adZJI" # — Rankobot token
bot = telebot.TeleBot(TOKEN) # chat id.
# bot.send_message(text = 'test', chat_id = 294645547)

# writting functionality of the command
# def start(update, context):
#     message = 'Čus, děkuji, že jsi vybrala mě'
#     context.bot.send_message(chat_id=update.effective_chat.id, text=message)
# # give a name to the command and add it to the dispaatcher
# start_handler = CommandHandler('start', start)
# dispatcher.add_handler(start_handler)
# updater.start_polling() # enable bot to get updates
#
# def echo(update, context):
#     context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)
# echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
# dispatcher.add_handler(echo_handler)

config_dict = get_default_config()
config_dict['language'] = 'en'
owm = OWM('f090f6b47d9a7259dfcb9a460f55a8a3', config_dict)

funny_message = ['Jsi kebab v tortille? Protože nedokážu žít bez tvé vůně...', 'Tvoje oči jsou jako bažina, potapím se v nich :face_screaming_in_fear:', 'Nejsou-li, náhodou tvoje rodiče cukráři? Nechápu teda, odkud mají tak hezký bonbónek :smirking_face:',
                 'Tvoje rodiče jsou květináři? Ne? Divný, protože ty jsi doopravdy květinka :smirking_face:',
                 'Tvoje rodiče jsou klenotnici? Tak odkud mají takové zlatíčko? :smirking_face:']
interesting_fakt = ['Žraloci čůrají kůží :relieved_face:', 'Když zemřeš, protože tě ve vesmíru vtáhla černá díra, zemřeš na špagetifikaci :winking_face:', 'Na Venuši by se zmražená pizza položená na zem dokonale propekla za pouhé 3 sekundy',
                    'Svijonožec má nejdelší penis ve zvířecí říši, když se porovnává velikost penisu na velikost tvora', 'Poníci nejsou mláďata od koní :relieved_face:',
                    'Sphenopalatine ganglion je lékařský název pro to, když vás začne bolet hlava při jezení příliš studené zmrzliny', 'Kdybys nepřetržitě křičela 8 let, 7 měsíců a 6 dní (třeba na mě za některé řádky tohoto programu), vytvořila bys dostatek zvukové energie, aby sis mohla udělat šálek čaje',
                    'Jestli jsi někdy přemítala, jak se říká jevu, kdy se tři kosmická tělesa v témže systému dostanou do jedné přímky, už nemusíš - jmenuje se to „syzygie :relieved_face:',
                    'Každý rok je v Americe nahlášeno 11.000 zranění vzniklých v důsledku sexuálních experimentů :smirking_face:',
                    'Je mnohem pravděpodobnější, že tě zabije padající kaktus, než zaútočí žralok :relieved_face:', 'Věděla jsi, že kdybys vzala všechny nervy z jednoho lidského těla a poskládala je do rovné čáry, šla bys na hodně, opravdu hodně dlouhou dobu do vězení?',
                    'V jakémkoli daném okamžiku je přibližně 0,7 % lidské populace opilých :relieved_face:', 'Fretka to vůbec nemá lehké. Když přijde čas páření a ona si nenajde fretčího samce, může z té frustrace až zemřít', 'Jediné varle plejtváka obrovského může vážit až 45 – 68 kg',
                    'K mračení potřebuješ zapojit 42 obličejových svalů, k úsměvu stačí jen 17 :smiling_face_with_smiling_eyes:']
# meme



@bot.message_handler(content_types = ['text'])
def send_echo(message):
    text = message.text

    # if "Sranda" or "Sranda plz" in text:
    #     bot.send_message(text=secrets.choice(funny_message), chat_id=message.chat.id)
    # elif "Fakt" or "Fakt plz" in text:
    #     bot.send_message(text=secrets.choice(interesting_fakt), chat_id=message.chat.id)
    # else:
    #     bot.send_message(text="", chat_id=message.chat.id)


    # elif "meme plz" in text:
    #         bot.send_message(text = secrets.choice(interesting_fakt), chat_id = message.chat.id)

    mgr = owm.weather_manager()
    observation = mgr.weather_at_place(text)
    w = observation.weather
    temp = w.temperature('celsius')["temp"]
    weather = observation.weather
    # print(weather.detailed_status)
    # print(str(temp))

    actual_weather = ""
    if 'clear' in (weather.detailed_status):
        actual_weather = "Jo, a nebe je čisté, tak v poho."
    elif 'cloud' in (weather.detailed_status):
        actual_weather = "Jsou tam mraky, ale pršet by nemělo."
    elif 'rain' in (weather.detailed_status):
        actual_weather = "A nezapomeň na deštník, prší tam!"

    if temp < 0:
        bot.send_message(text = "Já se zabiju, je tam " + str(temp) + " stupňu, dobře si to rozmysli! " + actual_weather + " \n", chat_id = message.chat.id)
    elif temp < 10:
        bot.send_message(text = "Ty joo, je tam " + str(temp) + " stupňu, tak to je hodně zíma! Obleč se pořadně! " + actual_weather + " \n", chat_id = message.chat.id)
    elif temp < 15:
        bot.send_message(text ="Neeeee, je tam zima! " + str(temp) + " stupňu! Obleč si něco teplého! " + actual_weather + " \n", chat_id = message.chat.id)
    elif temp < 20:
        bot.send_message(text = "Je tam trochu zíma! " + str(temp) + " stupňu! Obleč si mikinu! " + actual_weather + " \n", chat_id = message.chat.id)
    elif temp < 30:
        bot.send_message(text = "Ted' je teplo, pouhých " + str(temp) + " stupňu! Stačí ti i hezké tričko! " + actual_weather + " \n", chat_id = message.chat.id)




def good_morning():
    good_morning_Deni = ['Dobré ránko, Deni :smiling_face_with_smiling_eyes:! ', 'Dobré ráááááááno :smiling_face_with_smiling_eyes: ', 'Ty jo, tak to byl krasný sen! ']
    random_hi = ['Výpadáš dneska skvěle!', 'Máš hezký zadek :winking_face:', 'Dneska jsi naprosto úžasná! :smiling_face_with_heart-eyes:', 'Hezky ses vyspala?', 'Doufám, že se ti zdalo něco hezkýho :relieved_face:', 'Vyspala ses dneska?', 'Užij si dnešek!']

    bot.send_message(text = emoji.emojize((secrets.choice(good_morning_Deni) + secrets.choice(random_hi))), chat_id = 294645547)
    sys.stdout.flush()
    sleep(3)
    bot.send_message(text = "Podíváme se, jak to dneska výpadá s počasím...\n", chat_id = 294645547)
    sys.stdout.flush()
    sleep(3)
    bot.send_message(text = "Napovíš mi, kde jsi? Stačí napsat město, můžeš i česky: \n", chat_id = 294645547)

def funny():
    bot.send_message(text = emoji.emojize("Pozor:red_exclamation_mark::red_exclamation_mark::red_exclamation_mark:\nNevhodný vtip bude za..."), chat_id=294645547)
    sys.stdout.flush()
    sleep(1.5)
    bot.send_message(text = "3...", chat_id=294645547)
    sys.stdout.flush()
    sleep(1)
    bot.send_message(text = "2...", chat_id=294645547)
    sys.stdout.flush()
    sleep(1)
    bot.send_message(text = "1...", chat_id=294645547)
    sys.stdout.flush()
    sleep(1)
    bot.send_message(text = emoji.emojize(secrets.choice(funny_message)), chat_id = 294645547)

def fact():
    bot.send_message(text = emoji.emojize("Čauky-mňauky, čas pro zajímavé fakty :winking_face:"), chat_id=294645547)
    sys.stdout.flush()
    sleep(3)
    bot.send_message(text = emoji.emojize(secrets.choice(interesting_fakt)), chat_id = 294645547)


@bot.message_handler(commands=['start', 'go'])
def start_handler(message):
    bot.send_message(text = emoji.emojize(secrets.choice(funny_message)), chat_id = 294645547)

def telegram_polling():
    try:
        bot.infinity_polling() #constantly get messages from Telegram
    except:
        traceback_error_string=traceback.format_exc()
        with open("Error.Log", "a") as myfile:
            myfile.write("\r\n\r\n" + time.strftime("%c")+"\r\n<<ERROR polling>>\r\n"+ traceback_error_string + "\r\n<<ERROR polling>>")
        bot.stop_polling()
        time.sleep(10)
        telegram_polling()



# def clear():
#     os.system('cls' if os.name=='nt' else 'clear')



schedule.every(10).seconds.do(good_morning)
schedule.every().day.at("09:00:00").do(good_morning)
schedule.every().day.at("18:00:00").do(fact)
schedule.every().day.at("12:00:00").do(funny)



def schedule_loop():
  while 1:
      schedule.run_pending()
      time.sleep(1)

if __name__== '__main__':
    th = threading.Thread(target = schedule_loop)
    th.start()
    telegram_polling()
