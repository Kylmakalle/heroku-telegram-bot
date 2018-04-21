import bot_handlers
import config
import buttons
import datahandler
import json
import random
from telebot import types


ad_dict = {}
state_dict = {}


class Ad:
    def __init__(self, chat_id=None, db_id=None, message_id=None):
        if db_id is not None:
            self.message_id = db_id
            info = datahandler.get_ad(self)
            print(info[0])
            self.author = config.admin_id
            self.text = info[0][2]
            self.album = json.loads(info[0][1])
            ad_dict[config.admin_id] = self
        else:
            self.message_id = int(random.randint(1,10000))
            self.author = chat_id
            self.album = []
            self.text = ''
            ad_dict[self.author] = self

    def edit_text(self, message):
        self.text = message.text

    def edit_album(self, photo):
        self.album.append(photo)

    def post(self):
        text = self.text
        photo = {types.InputMediaPhoto(file) for file in self.album}
        if photo:
            bot_handlers.send_media_group(config.channel_id, photo)
        bot_handlers.send_message(config.channel_id, text)
        bot_handlers.send_message(config.admin_id, 'Объявление опубликовано!')

    def public(self, chat_id, name):
        if chat_id in state_dict:
            del state_dict[chat_id]
        if chat_id == config.admin_id:
            datahandler.delete_ad(self)
            return self.post()
        datahandler.save_ad(self)
        text = self.text
        photo = {types.InputMediaPhoto(file) for file in self.album}
        if photo:
            bot_handlers.send_media_group(config.admin_id, photo)
        bot_handlers.send_message(chat_id, '{}, объявление отправлено на модерацию и скоро будет опубликовано!'.format(name))
        message = bot_handlers.send_message(config.admin_id, text, reply_markup=buttons.admin_keyboard(self))
