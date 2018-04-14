import bot_handlers
import config
import buttons
import telebot


ad_dict = {}
state_dict = {}


class Ad:
    def __init__(self, chat_id, name):
        self.author = chat_id
        self.name = name
        self.album = []
        self.text = ''

    def edit_text(self, text):
        self.text = text

    def edit_album(self, photo):
        self.album.append(photo)

    def post(self):
        text = self.text
        photo = {telebot.types.InputMediaPhoto(file) for file in self.album}
        if photo:
            bot_handlers.send_media_group(config.channel_id, photo)
        bot_handlers.send_message(config.channel_id, text)
        bot_handlers.send_message(config.admin_id, 'Объявление опубликовано!')

    def public(self, chat_id):
        if chat_id in state_dict:
            del state_dict[chat_id]
        if chat_id == config.admin_id:
            return self.post()
        text = self.text
        photo = {types.InputMediaPhoto(file) for file in self.album}
        if photo:
            bot_handlers.send_media_group(config.admin_id, photo)
        message = bot_handlers.send_message(config.admin_id, text, reply_markup=buttons.admin_keyboard())
        bot_handlers.send_message(chat_id, '{}, объявление отправлено на модерацию и скоро будет опубликовано!'.format(self.name))
        ad_dict[message.message_id] = self
