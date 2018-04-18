import telebot
import config
import buttons
import utils
import ads
import bot_handlers


types = telebot.types
bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start'])
def start(message):
    bot_handlers.send_message(message.from_user.id, 'Добро пожаловать, {}! \n Выберите необходимый пункт меню.'.
                              format(message.from_user.first_name),
                              reply_markup=buttons.usual_keyboard())


@bot.message_handler(content_types=['text'])
def msg(message):
    chat_id = message.from_user.id
    if chat_id in ads.state_dict:
        if ads.state_dict[chat_id] == 'text':
            utils.add_text(message)
        elif ads.state_dict[chat_id] == 'question':
            text = message.text + '\n@' + message.from_user.username
            del ads.state_dict[chat_id]
            bot_handlers.send_message(config.admin_id, text)
            bot_handlers.send_message(message.from_user.id, 'Ваш вопрос принят. Ожидайте ответа.')
    elif message.text == 'Создать объявление':
        utils.new_ad(chat_id, message.from_user.first_name)
    elif message.text == 'Задать вопрос':
        utils.ask_question(chat_id, message.from_user.username)
    elif message.text == 'Связаться с нами':
        utils.contacts(chat_id)
    else:
        utils.start_over(message)


@bot.message_handler(content_types=['photo'])
def msg(message):
    chat_id = message.from_user.id
    if chat_id in ads.state_dict:
        if ads.state_dict[chat_id] == 'photo':
            utils.add_photo(message)
        elif ads.state_dict[chat_id] == 'photo_new':
            ads.ad_dict[chat_id].edit_album(message.photo[0].file_id)


@bot.callback_query_handler(func=lambda call: call)
def action(call):
    utils.call_handler(call)

bot.skip_pending = True

if __name__ == '__main__':
    bot.polling(none_stop=True)