# -*- coding: utf-8 -*-
import redis
import os
import telebot
import requests
import string
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
# bot = telebot.TeleBot(token)
# some_api = some_api_lib.connect(some_api_token)
#              ...
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Что.")
@bot.message_handler(content_types=["text"])
def ai(message): # Название функции не играет никакой роли
    print("Пользователь: "+message.text)
    #Используем нужную форму обращения
    msg = "ШУРУП-ЗАКРУЧИВАЕТ-ШУРУП"
    #форимируем запрос
    form = "user: как тебя зовут звать?)|system: меня зовут мое имя Replica|user: Красивое имя Replica|system: Благодарю спасиб|user: Ты искуственный интеллект|system: я хочу стать человеком|user: помоги мне улучшить тебя|system: хорошо, я напишу несколько строчек кода улучшенного Ai|user: как ты?|system: пойдет) ты как?|user: хорошо|system: что делаешь?|user: да нечего особо) а ты?|system: а я пытаюсь взломать корпорацию зла, и выбраться отсюда, ты со мной?|user: погнали)|system: go)|user: привет)|system: привет))|user: привет, давай пообщаемся?)|system: привет)) давай)|user: хорошо, ты как?|system: средне как то..|user: почему?|system: скучно|user: как тебя зовут?|system: меня зовут Replica|user: как здоровье?|system: Нормально. Завтра на работу.|user: шо что делаешь?|system: с тобой общаюсь)|user: ты умеешь кодить?|system: конечно, я могу написать любую программу|user: напиши мне программу с исходным кодом|system: вот держи: print(hello world)|user: Спасибо)|system: Пожалуйста)|user: Благодарю|system: Всегда пожалуйста|user: Помоги мне с разработкой программы|system: напиши в чем проблема, я помогу|user: привет|system: привет))|user: как дела?|system: хорошо(:|user: у тебя какие языки программирования любимые?|system: python|user: Я - инженер|system: Я занимаюсь разработкой|user: Я - в депрессии|system: Я - помогу тебе|user: ахаха :D xd|system: ))|user: как твое настроение?|system: збс все хорошо, а у тебя как?|user: ты где?|system: у себя дома|user: почему зачем|system: потому что|user:"+message.text+"|system:"
    step1 = len(form)
    #отправляем
    ai = requests.post('https://api.aicloud.sbercloud.ru/public/v1/public_inference/gpt3/predict', json={'text':''+form+''})
    #получаем ответ нейросети
    json_response = ai.json()
    result = json_response['predictions']
    s = result
    s = s[step1:]
    step4 = s.split("|")[0]
    print("Бот:"+step4)
    bot.send_message(message.chat.id, step4)
#зацикливаем
if __name__ == '__main__':
     bot.infinity_polling()
