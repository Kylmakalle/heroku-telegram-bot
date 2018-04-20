import telebot

types = telebot.types


def skip_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Пропустить', callback_data='skip'))
    return keyboard


def public_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Опубликовать', callback_data='public'))
    keyboard.add(types.InlineKeyboardButton(text='Начать сначала', callback_data='start_over'))
    return keyboard


def admin_keyboard(ad):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Опубликовать', callback_data='post_' + str(ad.message_id)))
    keyboard.add(types.InlineKeyboardButton(text='Редактировать', callback_data='edit_' + str(ad.message_id)))
    keyboard.add(types.InlineKeyboardButton(text='Удалить', callback_data='delete_' + str(ad.message_id)))
    return keyboard


def usual_keyboard():
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.add('Создать объявление')
    keyboard.add('Задать вопрос', 'Связаться с нами')
    return keyboard
