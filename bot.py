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
import threading
import datahandler
import os
import logging

types = telebot.types
bot = telebot.TeleBot(config.token)


def cancelgame(Game):
    if Game.gamestate == Game.gamestates[0]:
        bot.send_message(Game.cid, "Время вышло - игра отменена.")
        Fighting.refresh(Game)


@bot.inline_handler(func=lambda query: len(query.query)>0)
def query_text(query):
    try:
        Game = utils.GetGamefromPlayer(query.from_user.id)
        r_sum = types.InlineQueryResultArticle(
            id='11', title="Отправить команде",
            # Описание отображается в подсказке,
            # message_text - то, что будет отправлено в виде сообщения
            description=query.query,
            input_message_content=types.InputTextMessageContent(
                message_text=utils.Teamchat(query.query, Game.player_dict[query.from_user.id])))
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
        Game = utils.GetGamefromPlayer(chosen_inline_result.from_user.id)
        player = Game.player_dict[chosen_inline_result.from_user.id]
        for p in player.team.players:
            bot.send_message(p.chat_id, player.message)


# Обычный режим
@bot.message_handler(commands=["start"])
def start(message):
    datahandler.get_player(message.from_user.id, message.from_user.username)
    print(message.from_user.first_name)


@bot.message_handler(commands=["bugreport"])
def bugreport(message):
    Main_classes.reportid.append(message.from_user.id)
    bot.send_message(message.from_user.id, 'Опишите ошибку одним сообщением, как можно подробнее.')


@bot.message_handler(commands=["nocreate"])
def create(message):

    if message.chat.id == message.from_user.id:
        if not datahandler.checktournament(message.from_user.id):
            if not any(x.cid ==message.from_user.id for x in Main_classes.list_waitingplayers):
                player = Main_classes.WaitingPlayer(message.from_user.id, message.from_user.first_name)
                bot.send_message(message.chat.id,'Уникальный токен вашей команды - ' + str(player.token)
                     + '.\nИгрок, пославший ваш токен в личку боту, будет вашим партнером в турнире')
        else:bot.send_message(message.chat.id,'Вы уже учавствуете в турнире')


@bot.message_handler(commands=["nojointeam"])
def start(message):
    if message.chat.id == message.from_user.id:
        if not datahandler.checktournament(message.from_user.id):
            Main_classes.list_waitingtoken.append(message.from_user.id)
            bot.send_message(message.chat.id,'Введите токен.')
        else:
            bot.send_message(message.chat.id, 'Вы уже учавствуете в турнире')


@bot.message_handler(commands=["game"])
def start_game(message):
    if message.chat.id in Main_classes.dict_games:
        pass
    else:
        Game = Main_classes.Game(message.chat.id)
        Main_classes.dict_games[message.chat.id] = Game
        Main_classes.dict_games[message.chat.id].gamestate = Main_classes.dict_games[message.chat.id].gamestates[0]
        bot.send_message(message.chat.id, "Используйте команду /join, чтобы вступить в игру. 5 минут до отмены игры.")
        Game.waitingtimer = threading.Timer(300,cancelgame,[Game])
        Game.waitingtimer.start()


@bot.message_handler(commands=["rhinohunt"])
def start_game(message):
    if message.chat.id in Main_classes.dict_games:
        pass
    else:
        Game = Main_classes.Game(message.chat.id)
        Main_classes.dict_games[message.chat.id] = Game
        Main_classes.dict_games[message.chat.id].gamestate = Main_classes.dict_games[message.chat.id].gamestates[3]
        bot.send_document(message.chat.id, 'CgADAgADPgADc81oS3Dt10-ay0vUAg',caption="Используйте команду /join, чтобы вступить в игру. 5 минут до отмены игры.")
        Game.waitingtimer = threading.Timer(300, cancelgame, [Game])
        Game.waitingtimer.start()


@bot.message_handler(commands=["doghunt"])
def start_game(message):
    if message.chat.id in Main_classes.dict_games:
        pass
    else:
        Game = Main_classes.Game(message.chat.id)
        Main_classes.dict_games[message.chat.id] = Game
        Main_classes.dict_games[message.chat.id].gamestate = Main_classes.dict_games[message.chat.id].gamestates[2]
        bot.send_document(message.chat.id, 'BQADAgADNwEAAsR9WEs0ItU70AeZUwI',
                         caption="Используйте команду /join, чтобы вступить в игру. 5 минут до отмены игры.")
        Game.waitingtimer = threading.Timer(300, cancelgame, [Game])
        Game.waitingtimer.start()


@bot.message_handler(commands=["fight"])
def start_game(message):
    Game = utils.GetGamefromChat(message.chat.id)
    if Game is not None:
        if Game.gamestate == Game.gamestates[0]:
            if len(Game.players) >= 2:
                if len(Game.players) <= len(Game.Team1.players) + len(Game.Team2.players):
                    try:
                        Main_classes.dict_games[message.chat.id].waitingtimer.cancel()
                        bot.send_message(message.chat.id, "Начинается выбор оружия.")
                        Game.gamestate = Game.gamestates[1]
                        Game.waitingtimer.cancel()
                        t = threading.Thread(target=Game.FormPlayerlist)
                        t.daemon = True
                        t.start()
                        Game.waitingtimer.cancel()
                    except:
                        bot.send_message(message.chat.id, "Ошибка")

                else:
                    bot.send_message(message.chat.id, "Не все игроки выбрали команду.")
            else:
                bot.send_message(message.chat.id, "Недостаточно игроков для начала игры.")

        elif Game.gamestate == Game.gamestates[2] and Game.players:
                try:
                    Main_classes.dict_games[message.chat.id].waitingtimer.cancel()
                    bot.send_message(message.chat.id, "Начинается выбор оружия.")

                    Game.gamestate = Game.gamestates[1]
                    Game.waitingtimer.cancel()
                    t = threading.Thread(target=Game.FormPlayerlistDoghunt)
                    t.daemon = True
                    t.start()
                except:
                    bot.send_message(message.chat.id, "Ошибка")

        elif Game.gamestate == Game.gamestates[3] and Game.players:
                try:
                    Main_classes.dict_games[message.chat.id].waitingtimer.cancel()
                    bot.send_message(message.chat.id, "Начинается выбор оружия.")

                    Game.gamestate = Game.gamestates[1]
                    Game.waitingtimer.cancel()
                    t = threading.Thread(target=Game.FormPlayerlistRhinohunt)
                    t.daemon = True
                    t.start()
                except:
                    bot.send_message(message.chat.id, "Ошибка")


@bot.message_handler(commands=["cancel"])
def cancel_game(message):
    try:
        Game= Main_classes.dict_games[message.chat.id]
    except:
        Game = None
    if Game!= None:
        Game.waitingtimer.cancel()
        if Game.gamestate == Game.gamestates[0] or Game.gamestate == Game.gamestates[2]:
            bot.send_message(message.chat.id, "Игра отменена.")
            Fighting.refresh(Game)



@bot.message_handler(commands=["stats"])
def del_player(message):
    games = datahandler.get_games(message.from_user.id)
    if games is None:
        bot.send_message(message.chat.id,'Извините, вас нет в списке.')
    else:
        if games[0]!= 0:
            bot.send_message(message.chat.id, message.from_user.first_name.split(' ')[0][:12] +
                         '\nИгр сыграно - %s\nИгр выиграно - %s\nВинрейт - %s%%'%(games[0],games[1],str(games[1]*100/games[0])[:4]))
        else:
            bot.send_message(message.chat.id, message.from_user.first_name.split(' ')[0][:12] +
                             '\nИгр сыграно - 0')



@bot.message_handler(commands=["suicide"])
def suicide(message):
    Game = utils.GetGamefromChat(message.chat.id)
    if Game != None:
        print("Игра найдена.")
        Found = True
        Actor = None
        try:
            Actor = Game.player_dict[message.from_user.id]
        except:
            print('ошибка')
            Found = False

        if Game.gamestate == 'game' and Found and Actor in Actor.team.players:
            Actor.turn = 'suicide'

            try:
                Game.Fight.playerpool.remove(Actor)
                bot.delete_message(chat_id=Actor.chat_id, message_id=Actor.choicemessage)
            except:
                pass



@bot.message_handler(commands=["join"])
def add_player(message):
    Game = utils.GetGamefromChat(message.chat.id)
    if message.from_user.id in Main_classes.dict_players:
        pass
    elif Game != None:
        try:
            if Game.gamestate == Game.gamestates[0] and message.from_user.id not in Game.player_ids\
                and message.chat.id == Game.cid:
                bot.send_message(message.from_user.id, '*Вы успешно присоединились.*', parse_mode='markdown')
                datahandler.get_player(message.from_user.id, message.from_user.username)
                utils.AddPlayer(message.from_user.id, message.from_user.first_name.split(' ')[0][:12], Game)
                bot.send_message(Game.cid, message.from_user.first_name + ' успешно присоединился.')
                if len(Game.players) == 1:
                    Game.Team1.players.append(Game.players[0])
                    Game.players[0].team = Game.Team1
                if len(Game.players) == 2:
                    Game.Team2.players.append(Game.players[1])
                    Game.players[1].team = Game.Team2
                elif len(Game.players) >= 3:
                    print (message.from_user.first_name + ' выбирает сторону.')
                    keyboard = types.InlineKeyboardMarkup()
                    callback_button1 = types.InlineKeyboardButton(text=str(len(Game.Team1.players))[:5] + ' - ' + Game.players[0].name, callback_data='team1')
                    callback_button2 = types.InlineKeyboardButton(text=str(len(Game.Team2.players))[:5] + ' - ' + Game.players[1].name, callback_data='team2')
                    keyboard.add(callback_button1, callback_button2)
                    bot.send_message(message.from_user.id, message.from_user.first_name + ' Выберите, кому вы поможете в этом '
                                                                              'бою.', reply_markup=keyboard)

            elif Game.gamestate == Game.gamestates[2] and message.from_user.id not in Game.player_ids \
                    and message.chat.id == Game.cid:
                bot.send_message(message.from_user.id, '*Вы успешно присоединились.*', parse_mode='markdown')
                datahandler.get_player(message.from_user.id, message.from_user.username)
                utils.AddPlayer(message.from_user.id, message.from_user.first_name.split(' ')[0][:12], Game)
                bot.send_message(Game.cid, message.from_user.first_name + ' успешно присоединился.')

            elif Game.gamestate == Game.gamestates[3] and message.from_user.id not in Game.player_ids \
                    and message.chat.id == Game.cid:
                bot.send_message(message.from_user.id, '*Вы успешно присоединились.*', parse_mode='markdown')
                datahandler.get_player(message.from_user.id, message.from_user.username)
                utils.AddPlayer(message.from_user.id, message.from_user.first_name.split(' ')[0][:12], Game)
                bot.send_message(Game.cid, message.from_user.first_name + ' успешно присоединился.')
                if len(Game.players) >=2:
                    try:
                        Main_classes.dict_games[message.chat.id].waitingtimer.cancel()
                        bot.send_message(message.chat.id, "Начинается выбор оружия.")
                        Game.gamestate = Game.gamestates[1]
                        Game.waitingtimer.cancel()
                        t = threading.Thread(target=Game.FormPlayerlistRhinohunt)
                        t.daemon = True
                        t.start()
                    except:
                        bot.send_message(message.chat.id, "Ошибка")
            elif Game.gamestate != Game.gamestates[0]:
                bot.send_message(message.chat.id, 'Нет запущенной игры или игра уже началась.')
            elif message.chat.id != Game.cid:
                bot.send_message(message.chat.id,
                             message.from_user.first_name + ', игра идет в другом чате.')

        except:
            bot.send_message(message.chat.id, message.from_user.first_name, ' надо в личку боту написать.')
    time.sleep(3)


@bot.message_handler(commands=["sendall"])
def start(message):
    Main_classes.ruporready = True


@bot.message_handler(commands=['test'])
def find_file_ids(message):
    for file in os.listdir('gif/'):
        if file.split('.')[-1] == 'gif' or file.split('.')[-1] == 'png':
            f = open('gif/'+file,'rb')
            msg = bot.send_document(message.chat.id, f, None)
            # А теперь отправим вслед за файлом его file_id
            bot.send_message(message.chat.id, msg.document.file_id, reply_to_message_id=msg.message_id)
        time.sleep(3)

@bot.message_handler(commands=['try'])
def find_file_ids(message):
    bot.send_message(message.chat.id, '@' + message.from_user.username)

@bot.callback_query_handler(func=lambda call: True)
def action(call):
    if call.message:
        print("Получено.")
        if call.data == '1':
                bot.send_message(call.from_user.id, call.message.text)
    Game = utils.GetGamefromPlayer(call.from_user.id)

    if Game is not None:
        print("Игра найдена.")
        Found = True
        Actor = None
        try:
            Actor = Game.player_dict[call.from_user.id]
        except:
            print('ошибка')
            Found = False
        if Game.gamestate == Game.gamestates[0] :
            print('Подбор команды.')
            for p in Game.players:
                if call.from_user.id == p.chat_id:
                    print('Игрок найден')
                    if call.data == 'team1':
                        print('Команда 1')
                        Game.Team1.players.append(p)
                        p.team = Game.Team1
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text="Вы присоединились к команде " + Game.players[0].name)
                        bot.send_message(Game.cid, p.name + ' вступает в бой на стороне ' + Game.players[0].name)

                    if call.data == 'team2':
                        print('Команда 2')
                        p.team = Game.Team2
                        Game.Team2.players.append(p)
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text="Вы присоединились к команде " + Game.players[1].name)
                        bot.send_message(Game.cid,
                                         p.name + ' вступает в бой на стороне ' + Game.players[1].name)
        elif Game.gamestate == 'weapon' and Found:
            if call.data[0] == 'a' and call.data[0:1] != 'at':
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text="Оружие выбрано: " + (call.data[1:]))
                for w in Weapon_list.fullweaponlist:
                    if w.name == call.data[1:]:
                        Actor.weapon = w
                        break
                Game.weaponcounter -= 1
                print (Actor.name + ' выбрал оружие.')
        elif Game.gamestate == 'ability' and Found:
            if call.data[0] == 'i'and len(call.data) < 4:
                    bot.send_message(call.from_user.id,special_abilities.abilities[int(call.data[1:])].info)
            elif call.data[0] == 'a' and len(call.data) < 4:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text="Способность выбрана: " + special_abilities.abilities[int(call.data[1:])].name)
                Actor.abilities.append(special_abilities.abilities[int(call.data[1:])])
                if Actor.maxabilities > \
                    len(Actor.abilities):
                    utils.GetAbility(Actor)
                else:
                    try:
                        Game.abilitycounter -= 1
                        print (Actor.name + ' выбрал способности.')
                    except:
                        pass
        elif Game.gamestate == Game.gamestates[1] and Found:
                if Actor in Game.Fight.playerpool:
                    if call.data[0:4] == 'item':
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text="Ход " + str(Actor.Fight.round) + ': ' + Item_list.items[
                                                  call.data[0:7]].name)
                    if call.data[0:4] == 'vint':
                        if call.data[0:8] == 'vintinfo':
                            bot.send_message(call.from_user.id, special_abilities.abilities[int(call.data[8:])].info)
                        else:
                            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                  text="Временная способность выбрана: " + special_abilities.abilities[
                                                      int(call.data[4:])].name)
                            x = len(Actor.abilities)
                            Actor.abilities.append(special_abilities.abilities[int(call.data[4:])])
                            while x == len(Actor.abilities):
                                pass
                            Actor.abilities[-1].aquare(Actor.abilities[-1], Actor)
                            Fighting.send_action(Actor, Actor.Fight)
                    elif call.data[0:4] == 'move':
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text="Ход " + str(Actor.Fight.round) + ": Подойти.")
                        Actor.turn = 'move'
                        Actor.Fight.playerpool.remove(Actor)
                    elif call.data[0:9] == 'inventory':
                        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                        utils.sendinventory(Actor)
                    elif call.data[0:6] == 'skills':
                        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                        utils.sendskills(Actor)
                    elif call.data[0:13] == 'weaponspecial':
                        print(Actor.name + ' целится.')
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text="Контратака.")
                        Actor.weapon.special(Actor, call)
                        Actor.turn = 'weaponspecial'
                        Actor.Fight.playerpool.remove(Actor)
                    elif call.data[0:6] == 'cancel':
                        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                        Fighting.send_action(Actor, Actor.Fight)
                    elif call.data[0:3] == 'aim':
                        print(Actor.name + ' целится.')
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text="Цель принята: " + utils.ActorFromId(call.data[3:], Game).name)
                        Actor.weapon.special(Actor, call)
                        Actor.turn = 'aim'
                        Actor.Fight.playerpool.remove(Actor)
                    elif call.data[0:4] == 'draw':
                        print(Actor.name + ' целится.')

                        if Actor.bonusaccuracy == 1:
                            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                  text='Вы натягиваете тетиву Лука. Характеристики лука увеличены!'
                                                           ' Появился шанс оглушить противника!')
                        else:
                            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text="Вы натягиваете тетиву Лука. Характеристики лука увеличены!")
                        Actor.weapon.special(Actor, call)
                        Actor.turn = 'draw'
                        Actor.Fight.playerpool.remove(Actor)
                    elif call.data[0:4] == 'info':
                        if call.data == 'info':
                            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text="Информация выслана.")
                            utils.PlayerInfo(Actor)

                        else:
                            if call.data[4:] == 'cancel':
                                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                      text="Отменено")
                            else:
                                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                      text="Информация выслана.")
                                utils.PlayerInfo(utils.ActorFromId(call.data[4:], Actor.Game),cid=Actor.chat_id)
                                Actor.itemlist.remove(Item_list.mental)
                                Actor.mentalrefresh = Actor.Fight.round + 2

                        Fighting.send_action(Actor, Actor.Fight)
                    elif call.data[0:2] == 'op':
                        if call.data[2:] == 'cancel':

                            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                  text="Отменено")
                            Fighting.send_action(Actor, Actor.Fight)
                        else:


                            print(Actor.name + ' выбор противника.')
                            Actor.target = utils.ActorFromId(call.data[2:], Game)
                            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                  text="Противник принят: " + Actor.target.name)
                            try:
                                Actor.Fight.playerpool.remove(Actor)
                            except:
                                print('Не удалось удалить игрока из пула(прицел).')
                                pass
                    elif call.data[0:5] == 'itemh':
                        Item_list.items[call.data[0:7]].useact(Actor)
                        Fighting.send_action(Actor, Actor.Fight)
                    elif call.data[0:7] == 'release':
                        Actor.bonusaccuracy = 0
                        Actor.Armed = False
                        bot.delete_message(Actor.chat_id, Actor.choicemessage)
                        bot.send_message(Actor.chat_id, 'Вы перестали натягивать тетиву.')
                        Fighting.send_action(Actor, Actor.Fight)
                    elif call.data[0:5] == 'items':Item_list.items[call.data[0:7]].useact(Actor)
                    elif call.data[0:5] == 'itemt' or call.data[0:6] == 'itemat':
                        Actor.turn = call.data
                        print(str(Actor.turn) + ' ' + str(Actor.Fight.round) + ' ' + str(Actor.name))
                        Item_list.items[call.data[0:7]].useact(Actor)
                    elif call.data[0:6] == 'spitem':
                        if call.data[6:] == 'cancel':
                            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                  text="Отменено")
                            Fighting.send_action(Actor, Actor.Fight)
                        else:

                            Actor.itemtarget = utils.ActorFromId(call.data[6:], Actor.Game)
                            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                  text="Цель - " + Actor.itemtarget.name)

                            Actor.Fight.playerpool.remove(Actor)
                    elif call.data[0:5] == 'mitem':
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text="Принято.")
                        Item_list.items[call.data[0:7]].useact(Actor)
                    elif call.data[0:6] == 'attack':
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text="Ход " + str(Actor.Fight.round) + ": Атака.")
                        Actor.weapon.get_action(Actor,call)
                    else:

                        Actor.turn = call.data
                        try:
                            Actor.Fight.playerpool.remove(Actor)
                        except:
                            print('Не удалось удалить игрока из пула(обычный ход).')
                            pass
                        print(str(Actor.turn) + ' ' + str(Actor.Fight.round) + ' ' + str(Actor.name))

                        if call.data[:4] == 'skip':
                            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                  text="Ход " + str(Actor.Fight.round) + ": Пропуск хода.")
                        if call.data == 'reload' + str(Actor.Fight.round):
                            if Actor.weapon.Melee:
                                bot.edit_message_text(chat_id=Actor.chat_id, message_id=Actor.choicemessage.message_id,
                                                      text="Ход " + str(Actor.Fight.round) + ': ' + 'Отдых')
                            else:
                                bot.edit_message_text(chat_id=Actor.chat_id, message_id=Actor.choicemessage.message_id,
                                                      text="Ход " + str(Actor.Fight.round) + ': ' + 'Перезарядка')


@bot.message_handler(content_types=["text"])
def start(message):
    if message.from_user.id in Main_classes.list_waitingtoken:
        for p in Main_classes.list_waitingplayers:
            if str(p.token) == message.text and p.cid != message.from_user.id:
                datahandler.createteam(p.cid,message.from_user.id, p.name, message.from_user.first_name)
                bot.send_message(p.cid,'Команда создана!')
                bot.send_message(message.from_user.id, 'Команда создана!')
        Main_classes.list_waitingtoken.remove(message.from_user.id)
    elif message.chat.id == 197216910 and Main_classes.ruporready:
        Main_classes.ruporready = False
        list = datahandler.getallplayers()
        for x in list:
            bot.send_message(x,message.text)
    elif message.chat.id in Main_classes.reportid:
        try:
            Main_classes.reportid.remove(message.chat.id)
            logging.basicConfig(filename='example.log', level=logging.WARNING)
            bot.send_message(message.chat.id,'Сообщение принято.')
            logging.warning(message.from_user.username + ': !' + str(message.text))
        except:
            pass

bot.skip_pending = True
if __name__ == '__main__':
     time.sleep(1)
     bot.polling(none_stop=True)
