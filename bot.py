# -*- coding: utf-8 -*-
import config
import telebot
import Main_classes
import Fighting
import Item_list
import utils
import special_abilities
import Weapon_list
import time
import os
import bot_handlers
import datahandler

types = telebot.types
bot = telebot.TeleBot(config.token)

# Инлайн тимчата
@bot.inline_handler(func=lambda query: len(query.query)>0)
def query_text(query):
    try:
        Game = utils.get_game_from_player(query.from_user.id)
        r_sum = types.InlineQueryResultArticle(
            id='11', title="Отправить команде",
            # Описание отображается в подсказке,
            # message_text - то, что будет отправлено в виде сообщения
            description=query.query,
            input_message_content=types.InputTextMessageContent(
                message_text=utils.teamchat(query.query, Game.player_dict[query.from_user.id])))
        bot.answer_inline_query(query.id, [r_sum])
    except:
        r_sum = types.InlineQueryResultArticle(
            id='22', title="Ошибка!",
            description='Команда не найдена.',
            input_message_content=types.InputTextMessageContent(
                message_text='Ошибка!'))
        bot.answer_inline_query(query.id, [r_sum])


@bot.chosen_inline_handler(func=lambda chosen_inline_result: True )
def test_chosen(chosen_inline_result):
    if chosen_inline_result.result_id == '11':
        Game = utils.get_game_from_player(chosen_inline_result.from_user.id)
        player = Game.player_dict[chosen_inline_result.from_user.id]
        for p in player.team.players:
            bot.send_message(p.chat_id, player.message)



@bot.message_handler(commands=["start"])
def start(message):
    pass

@bot.message_handler(commands=["bugreport"])
def bugreport(message):
    Main_classes.reportid.append(message.from_user.id)
    bot.send_message(message.from_user.id, 'Опишите ошибку одним сообщением, как можно подробнее.')



# Обычный режим
@bot.message_handler(commands=["game"])
def start_game(message):
    if message.chat.id in Main_classes.existing_games:
        pass
    else:
        bot_handlers.start_game(0, message.chat.id)
        bot.send_message(message.chat.id, "Используйте команду /join, чтобы вступить в игру. 5 минут до отмены игры.")


# Сражение с носорогом
@bot.message_handler(commands=["rhinohunt"])
def start_game(message):
    if message.chat.id in Main_classes.existing_games:
        pass
    else:
        bot_handlers.start_game(1, message.chat.id)
        bot.send_document(message.chat.id, 'CgADAgADPgADc81oS3Dt10-ay0vUAg',
                          caption="Используйте команду /join, чтобы вступить в игру. 5 минут до отмены игры.")


# Сражение с волками
@bot.message_handler(commands=["doghunt"])
def start_game(message):
    if message.chat.id in Main_classes.existing_games:
        pass
    else:
        bot_handlers.start_game(2, message.chat.id)
        bot.send_document(message.chat.id, 'BQADAgADNwEAAsR9WEs0ItU70AeZUwI',
                          caption="Используйте команду /join, чтобы вступить в игру. 5 минут до отмены игры.")


@bot.message_handler(commands=["fight"])
def start_game(message):
    game = utils.get_game_from_chat(message.chat.id)
    if game is not None:
        if game.gamestate == game.gamestates[0]:
            if game.gametype == 'game':
                if len(game.players) < 2:
                    bot.send_message(message.chat.id, "Недостаточно игроков для начала игры.")
                elif len(game.players) > len(game.team1.players) + len(game.team2.players):
                    bot.send_message(message.chat.id, "Не все игроки выбрали команду.")
                elif len(game.players) == len(game.team1.players) + len(game.team2.players):
                    game.players = tuple(game.players)
                    bot_handlers.start_fight(message.chat.id)
            else:
                if len(game.players) < 1:
                    bot.send_message(message.chat.id, "Недостаточно игроков для начала игры.")
                else:
                    game.players = tuple(game.players)
                    bot_handlers.start_fight(message.chat.id)


@bot.message_handler(commands=["cancel"])
def cancel_game(message):
    try:
        game = Main_classes.existing_games[message.chat.id]
    except:
        game = None
    if game is not None:
        if game.gamestate == game.gamestates[0]:
            game.waitingtimer.cancel()
            bot.send_message(message.chat.id, "Игра отменена.")
            bot_handlers.cancel_game(game)


@bot.message_handler(commands=["suicide"])
def suicide(message):
    game = utils.get_game_from_chat(message.chat.id)
    if game != None:
        print("Игра найдена.")
        found = True
        actor = None
        try:
            actor = game.player_dict[message.from_user.id]
        except:
            print('ошибка')
            found = False

        if game.gamestate == 'fight' and found and actor in actor.team.players:
            actor.turn = 'suicide'
            try:
                game.fight.playerpool.remove(actor)
            except:
                pass
            try:
                bot.delete_message(chat_id=actor.chat_id, message_id=actor.choicemessage)
            except:
                pass


@bot.message_handler(commands=["join"])
def add_player(message):
    game = utils.get_game_from_chat(message.chat.id)
    if message.from_user.id in Main_classes.dict_players:
        pass
    elif game is not None:
        if game.gametype == game.gametypes[0] and message.from_user.id not in game.player_ids \
                and message.chat.id == game.cid and game.gamestate == game.gamestates[0]:
            bot.send_message(message.from_user.id, '*Вы успешно присоединились.*', parse_mode='markdown')
            try:
                game.players.append(
                    Main_classes.Player(message.from_user.id, message.from_user.first_name.split(' ')[0][:12], None,
                                        game))
            except AttributeError:
                bot.send_message(message.chat.id, 'Слишком поздно!')
                return
            utils.add_player(message.from_user.id, message.from_user.first_name.split(' ')[0][:12], game)
            bot.send_message(game.cid, message.from_user.first_name + ' успешно присоединился.')
            if len(game.players) == 1:
                game.team1.players.append(game.players[0])
                game.players[0].team = game.team1
            if len(game.players) == 2:
                game.team2.players.append(game.players[1])
                game.players[1].team = game.team2
            elif len(game.players) >= 3:
                print(message.from_user.first_name + ' выбирает сторону.')
                keyboard = types.InlineKeyboardMarkup()
                callback_button1 = types.InlineKeyboardButton(
                    text=str(len(game.team1.players))[:5] + ' - ' + game.players[0].name, callback_data='team1')
                callback_button2 = types.InlineKeyboardButton(
                    text=str(len(game.team2.players))[:5] + ' - ' + game.players[1].name, callback_data='team2')
                keyboard.add(callback_button1, callback_button2)
                bot.send_message(message.from_user.id,
                                 message.from_user.first_name + ' Выберите, кому вы поможете в этом '
                                                                'бою.', reply_markup=keyboard)

        elif message.from_user.id not in game.player_ids and message.chat.id == game.cid and \
                        game.gamestate == game.gamestates[0]:
            bot.send_message(message.from_user.id, '*Вы успешно присоединились.*', parse_mode='markdown')
            try:
                game.players.append(
                    Main_classes.Player(message.from_user.id, message.from_user.first_name.split(' ')[0][:12], None,
                                        game))
                game.team1.players.append(game.players[-1])
                game.players[-1].team = game.team1
            except AttributeError:
                return bot.send_message(message.chat.id, 'Слишком поздно!')
            utils.add_player(message.from_user.id, message.from_user.first_name.split(' ')[0][:12], game)
            bot.send_message(game.cid, message.from_user.first_name + ' успешно присоединился.')
            if len(game.players) >= 2 and game.gametype == game.gametypes[1]:
                game.players = tuple(game.players)
                bot_handlers.start_fight(game.cid)
        elif game.gamestate != game.gamestates[0]:
            bot.send_message(message.chat.id, 'Нет запущенной игры или игра уже началась.')
        elif message.chat.id != game.cid:
            bot.send_message(message.chat.id,
                             message.from_user.first_name + ', игра идет в другом чате.')

    time.sleep(3)


@bot.message_handler(commands=["sendall"])
def start(message):
    Main_classes.ruporready = True


@bot.message_handler(commands=['test'])
def find_file_ids(message):
    for file in os.listdir('gif/'):
        if file.split('.')[-1] == 'gif' or file.split('.')[-1] == 'png':
            f = open('gif/' + file, 'rb')
            msg = bot.send_document(message.chat.id, f, None)
            # А теперь отправим вслед за файлом его file_id
            bot.send_message(message.chat.id, msg.document.file_id, reply_to_message_id=msg.message_id)
        time.sleep(3)


@bot.message_handler(commands=['try'])
def find_file_ids(message):
    try:
        bot.send_message(message.chat.id, '@' + message.from_user.username)
    except:
        pass


@bot.callback_query_handler(func=lambda call: True)
def action(call):
    if call.message:
        print("Получено.")
        if call.data == '1':
            bot.send_message(call.from_user.id, call.message.text)
    game = utils.get_game_from_player(call.from_user.id)

    if game is not None:
        print("Игра найдена.")
        found = True
        actor = None
        try:
            actor = game.player_dict[call.from_user.id]
        except:
            print('ошибка')
            found = False
        if game.gamestate == game.gamestates[0]:
            print('Подбор команды.')
            for p in game.players:
                if call.from_user.id == p.chat_id:
                    print('Игрок найден')
                    if call.data == 'team1':
                        print('Команда 1')
                        game.team1.players.append(p)
                        p.team = game.team1
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text="Вы присоединились к команде " + game.players[0].name)
                        bot.send_message(game.cid, p.name + ' вступает в бой на стороне ' + game.players[0].name)

                    if call.data == 'team2':
                        print('Команда 2')
                        p.team = game.team2
                        game.team2.players.append(p)
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text="Вы присоединились к команде " + game.players[1].name)
                        bot.send_message(game.cid,
                                         p.name + ' вступает в бой на стороне ' + game.players[1].name)
        elif game.gamestate == 'weapon' and found:
            if call.data[0] == 'a' and call.data[0:1] != 'at':
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text="Оружие выбрано: " + (call.data[1:]))
                for w in Weapon_list.fullweaponlist:
                    if w.name == call.data[1:]:
                        actor.weapon = w
                        break
                game.weaponcounter -= 1
                print(actor.name + ' выбрал оружие.')
        elif game.gamestate == 'ability' and found:
            if call.data[0] == 'i' and len(call.data) < 4:
                bot.send_message(call.from_user.id, special_abilities.abilities[int(call.data[1:])].info)
            elif call.data[0] == 'a' and len(call.data) < 4:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text="Способность выбрана: " + special_abilities.abilities[
                                          int(call.data[1:])].name)
                actor.abilities.append(special_abilities.abilities[int(call.data[1:])])
                if actor.maxabilities > \
                        len(actor.abilities):
                    utils.get_ability(actor)
                else:
                    try:
                        game.abilitycounter -= 1
                        print(actor.name + ' выбрал способности.')
                    except:
                        pass
        elif game.gamestate == game.gamestates[3] and found:
            if actor in game.fight.playerpool:
                if call.data[0:4] == 'item':
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text="Ход " + str(actor.fight.round) + ': ' + Item_list.items[
                                              call.data[0:7]].name)
                if call.data[0:4] == 'vint':
                    if call.data[0:8] == 'vintinfo':
                        bot.send_message(call.from_user.id, special_abilities.abilities[int(call.data[8:])].info)
                    else:
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text="Временная способность выбрана: " + special_abilities.abilities[
                                                  int(call.data[4:])].name)
                        x = len(actor.abilities)
                        actor.abilities.append(special_abilities.abilities[int(call.data[4:])])
                        while x == len(actor.abilities):
                            pass
                        actor.abilities[-1].aquare(actor.abilities[-1], actor)
                        Fighting.send_action(actor, actor.fight)
                elif call.data[0:4] == 'move':
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text="Ход " + str(actor.fight.round) + ": Подойти.")
                    actor.turn = 'move'
                    actor.fight.playerpool.remove(actor)
                elif call.data[0:9] == 'inventory':
                    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                    utils.send_inventory(actor)
                elif call.data[0:6] == 'skills':
                    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                    utils.send_skills(actor)
                elif call.data[0:6] == 'cancel':
                    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                    Fighting.send_action(actor, actor.fight)
                elif call.data[0:3] == 'aim':
                    print(actor.name + ' целится.')
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text="Цель принята: " + utils.actor_from_id(call.data[3:], game).name)
                    actor.weapon.special(actor, call)
                    actor.turn = 'aim'
                    actor.fight.playerpool.remove(actor)
                elif call.data == 'take' + str(actor.fight.round):
                    print(actor.name + ' подбирает оружие.')
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text="Ход " + str(actor.fight.round) + ": Подобрать оружие.")
                    actor.turn = 'take' + str(actor.fight.round)
                    actor.fight.playerpool.remove(actor)
                elif call.data[0:13] == 'weaponspecial':
                    print(actor.name + ' целится.')
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text="Особая атака.")
                    actor.weapon.special(actor, call)
                    actor.turn = 'weaponspecial'
                    actor.fight.playerpool.remove(actor)
                elif call.data[0:4] == 'draw':
                    print(actor.name + ' целится.')

                    if actor.bonusaccuracy == 1:
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text='Вы натягиваете тетиву Лука. Характеристики лука увеличены!'
                                                   ' Появился шанс оглушить противника!')
                    else:
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text="Вы натягиваете тетиву Лука. Характеристики лука увеличены!")
                    actor.weapon.special(actor, call)
                    actor.turn = 'draw'
                    actor.fight.playerpool.remove(actor)
                elif call.data[0:4] == 'info':
                    if call.data == 'info':
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text="Информация выслана.")
                        utils.player_info(actor)

                    else:
                        if call.data[4:] == 'cancel':
                            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                  text="Отменено")
                        else:
                            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                  text="Информация выслана.")
                            utils.player_info(utils.actor_from_id(call.data[4:], actor.game), cid=actor.chat_id)
                            actor.itemlist.remove(Item_list.mental)
                            actor.mentalrefresh = actor.fight.round + 2

                    Fighting.send_action(actor, actor.fight)
                elif call.data[0:2] == 'op':
                    if call.data[2:] == 'cancel':

                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text="Отменено")
                        Fighting.send_action(actor, actor.fight)
                    else:
                        print(actor.name + ' выбор противника.')
                        actor.target = utils.actor_from_id(call.data[2:], game)
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text="Противник принят: " + actor.target.name)
                        try:
                            actor.fight.playerpool.remove(actor)
                        except:
                            print('Не удалось удалить игрока из пула(прицел).')
                            pass
                elif call.data[0:5] == 'itemh':
                    Item_list.items[call.data[0:7]].useact(actor)
                    Fighting.send_action(actor, actor.fight)
                elif call.data[0:7] == 'release':
                    actor.bonusaccuracy = 0
                    actor.Armed = False
                    bot.delete_message(actor.chat_id, actor.choicemessage)
                    bot.send_message(actor.chat_id, 'Вы перестали натягивать тетиву.')
                    Fighting.send_action(actor, actor.fight)
                elif call.data[0:5] == 'items':
                    Item_list.items[call.data[0:7]].useact(actor)
                elif call.data[0:5] == 'itemt' or call.data[0:6] == 'itemat':
                    actor.turn = call.data
                    print(str(actor.turn) + ' ' + str(actor.fight.round) + ' ' + str(actor.name))
                    Item_list.items[call.data[0:7]].useact(actor)
                elif call.data[0:6] == 'spitem':
                    if call.data[6:] == 'cancel':
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text="Отменено")
                        Fighting.send_action(actor, actor.fight)
                    else:
                        actor.itemtarget = utils.actor_from_id(call.data[6:], actor.game)
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text="Цель - " + actor.itemtarget.name)
                        actor.fight.playerpool.remove(actor)
                elif call.data[0:5] == 'mitem':
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text="Принято.")
                    Item_list.items[call.data[0:7]].useact(actor)
                elif call.data[0:6] == 'attack':
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text="Ход " + str(actor.fight.round) + ": Атака.")
                    actor.weapon.get_action(actor, call)
                else:

                    actor.turn = call.data
                    try:
                        actor.fight.playerpool.remove(actor)
                    except:
                        print('Не удалось удалить игрока из пула(обычный ход).')
                        pass
                    print(str(actor.turn) + ' ' + str(actor.fight.round) + ' ' + str(actor.name))

                    if call.data[:4] == 'skip':
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text="Ход " + str(actor.fight.round) + ": Пропуск хода.")
                    if call.data == 'reload' + str(actor.fight.round):
                        if actor.weapon.Melee:
                            bot.edit_message_text(chat_id=actor.chat_id, message_id=actor.choicemessage.message_id,
                                                  text="Ход " + str(actor.fight.round) + ': ' + 'Отдых')
                        else:
                            bot.edit_message_text(chat_id=actor.chat_id, message_id=actor.choicemessage.message_id,
                                                  text="Ход " + str(actor.fight.round) + ': ' + 'Перезарядка')


@bot.message_handler(content_types=["text"])
def start(message):
    if message.chat.id == 197216910 and Main_classes.ruporready:
        Main_classes.ruporready = False
        list = datahandler.getallplayers()
        for x in list:
            bot.send_message(x, message.text)


bot.skip_pending = True
if __name__ == '__main__':
    time.sleep(1)
    bot.polling(none_stop=True)
