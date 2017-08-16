import Main_classes
import threading
import utils
import telebot
import config
import datahandler
import Item_list
import special_abilities

types = telebot.types
bot = telebot.TeleBot(config.token)

# Инициировать игру в чате
def start_game(gametype, cid):

    game = Main_classes.Game(cid)
    Main_classes.existing_games[cid] = game
    game.gamestate = game.gamestates[0]
    game.gametype = game.gametypes[gametype]
    game.waitingtimer = threading.Timer(300, cancel_game, [game])
    game.waitingtimer.start()


# Удалить игру в чате
def cancel_game(game):
    utils.delete_game(game)
    bot.send_message(game.cid, "Игра отменена.")


# Закончить набор игроков и начать сражение
def start_fight(cid):
    game = Main_classes.existing_games[cid]
    game.waitingtimer.cancel()
    game.gamestate = game.gamestates[1]
    game.waitingtimer.cancel()
    t = threading.Thread(target=utils.prepare_fight, args=[game])
    t.daemon = True
    t.start()

def start_custom_fight(cid):
    game = Main_classes.existing_games[cid]
    game.waitingtimer.cancel()
    game.gamestate = game.gamestates[1]
    game.waitingtimer.cancel()
    t = threading.Thread(target=utils.prepare_custom_fight, args=[game])
    t.daemon = True
    t.start()


def player_menu(name, cid):
    data = list(datahandler.get_current(cid))
    itemnames = []
    skills = []
    private_string = None
    if datahandler.get_private_string(cid) != 0:
        print(strdatahandler.get_private_string(cid)())
        private_string = '|yes'
    if data[0] is None:
        data[0] = ' '
    if data[1] is None:
        data[1] = ' '
    elif data[1] == '':
        data[1] = ' '
    else:
        items = data[1].split(',')
        for item in items:
            if item == '':
                items.remove(item)
        for item in items:
            itemnames.append(Item_list.items[item].name)
    if data[2] is None:
        data[2] = ' '
    elif data[2] == '':
        data[2] = ' '
    else:
        skills = data[2].split(',')
    message = name + '\n Оружие: ' + data[0] + '\n Предметы: ' + ', '.join(itemnames) + '\n Навыки: ' + ', '.join(skills)
    keyboard = types.InlineKeyboardMarkup()
    callback_button1 = types.InlineKeyboardButton(
        text="Изменить оружие", callback_data='change_weapon')
    callback_button2 = types.InlineKeyboardButton(
        text="Изменить предметы", callback_data='change_items')
    callback_button3 = types.InlineKeyboardButton(
        text="Изменить навыки", callback_data='change_skills')
    if private_string is not None:
        callback_button4 = types.InlineKeyboardButton(
            text="Отчеты в личку" + private_string, callback_data='change_string')
    else:
        callback_button4 = types.InlineKeyboardButton(
            text="Отчеты в личку", callback_data='change_string')
    keyboard.add(callback_button1, callback_button2)
    keyboard.add(callback_button3)
    keyboard.add(callback_button4)
    return (message, keyboard)

def change_string(id):
    datahandler.change_private_string(id)

def weapon_menu(chat_id):
    weapons = utils.get_weaponlist()
    keyboard = types.InlineKeyboardMarkup()
    weapons = [x.name for x in weapons]
    unique = datahandler.get_unique(chat_id)[0]
    if unique is not None:
        unique = unique.split(',')
        for uniq in unique:
            weapons.append(uniq)
    for weapon in weapons:
        callback_button = types.InlineKeyboardButton(
            text=weapon, callback_data='new_weapon' + weapon)
        keyboard.add(callback_button)
    return ('Выберите оружие', keyboard)

def items_menu(chat_id):
    items = Item_list.itemlist
    data = datahandler.get_current(chat_id)[1]
    if data is not None:
        data = data.split(',')
        keyboard = types.InlineKeyboardMarkup()
        for item in items:
            matched_items = 0
            if item.id in data:
                matched_items += 1
                callback_button = types.InlineKeyboardButton(
                    text=(item.name + u'\U00002714'), callback_data='delete_item' + item.id)
                keyboard.add(callback_button)
            else:
                callback_button = types.InlineKeyboardButton(
                    text=item.name, callback_data='add_item' + item.id)
                keyboard.add(callback_button)
    else:
        keyboard = types.InlineKeyboardMarkup()
        for item in items:
            callback_button = types.InlineKeyboardButton(
                text=item.name, callback_data='add_item' + item.id)
            keyboard.add(callback_button)
    callback_button = types.InlineKeyboardButton(
        text='Принято', callback_data='accept_player')
    keyboard.add(callback_button)
    return ('Выберите предметы', keyboard)

def skills_menu(chat_id):
    skills = special_abilities.abilities
    data = datahandler.get_current(chat_id)[2]
    if data is not None:
        data = data.split(',')
        keyboard = types.InlineKeyboardMarkup()
        for skill in skills:
            matched_skills = 0
            if skill.name in data:
                matched_skills += 1
                callback_button = types.InlineKeyboardButton(
                    text=skill.name + u'\U00002714', callback_data='delete_skill' + skill.name)
                keyboard.add(callback_button)
            else:
                callback_button = types.InlineKeyboardButton(
                    text=skill.name, callback_data='add_skill' + skill.name)
                keyboard.add(callback_button)
    else:
        keyboard = types.InlineKeyboardMarkup()
        for skill in skills:
            callback_button = types.InlineKeyboardButton(
                text=skill.name, callback_data='add_skill' + skill.name)
            keyboard.add(callback_button)
    callback_button = types.InlineKeyboardButton(
        text='Принято', callback_data='accept_player')
    keyboard.add(callback_button)
    return ('Выберите предметы', keyboard)

def change_weapon(cid, weapon_name):
    datahandler.change_weapon(cid, weapon_name)

def add_item(cid, weapon_name):
    return datahandler.add_item(cid, weapon_name)