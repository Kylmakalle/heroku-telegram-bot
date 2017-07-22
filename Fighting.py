import Main_classes
import utils
import config
import telebot
import threading
import time
import Weapon_list
import datahandler
import random
import special_abilities

bot = telebot.TeleBot(config.token)
types = telebot.types

# Собираем пул активных игроков
def get_playerpool(Fight):
    Fight.round += 1
    Fight.fightstate = 'playerpool'
    print('Действующие игроки:')

    Fight.Game.string.add('Команда 1 - ' + ', '.join([p.name for p in Fight.Team1.actors]))
    Fight.Game.string.add('Команда 2 - ' + ', '.join([p.name for p in Fight.Team2.actors]))
    for p in Fight.activeplayers:
        if p.Alive and not p.Disabled:
            Fight.playerpool.append(p)
            print(p.name)
        elif 'Zombie' in p.passive and not p.Disabled:
            if p.zombiecounter > 0:
                Fight.playerpool.append(p)
                print(p.name)
        else:
            p.turn = 'disabled'


# Рассылаем варианты действий
def send_actions(Fight):
    for p in Fight.playerpool:
        account_targets(p, Fight)
        send_action(p,Fight)
        print('Послан список действий для ' + p.name)


# Описание вариантов действий
def send_action(p, Fight):
    keyboard = types.InlineKeyboardMarkup()
    if p.energy > 0:
        if not p.weapon.Melee:
            callback_button1 = types.InlineKeyboardButton(text="Выстрел", callback_data=str('attack'
                                                                                            + str(Fight.round)))
            callback_button2 = types.InlineKeyboardButton(text="Перезарядка", callback_data=str('reload'
                                                                                                + str(Fight.round)))
            keyboard.add(callback_button1, callback_button2)
        else:
            if p.Inmelee:
                callback_button1 = types.InlineKeyboardButton(text="Удар",
                                                              callback_data=str('attack' + str(Fight.round)))
                callback_button2 = types.InlineKeyboardButton(text="Отдышаться",
                                                              callback_data=str('reload' + str(Fight.round)))
                keyboard.add(callback_button1, callback_button2)
            else:
                if p.targets == []:
                    callback_button1 = types.InlineKeyboardButton(text="Подойти",
                                                              callback_data=str('move' + str(Fight.round)))
                    callback_button2 = types.InlineKeyboardButton(text="Отдышаться",
                                                              callback_data=str('reload' + str(Fight.round)))
                    keyboard.add(callback_button1, callback_button2)
                elif len(p.targets)<len(utils.GetOtherTeam(p).actors):
                    callback_button1 = types.InlineKeyboardButton(text="Удар",
                                                                  callback_data=str('attack' + str(Fight.round)))
                    callback_button2 = types.InlineKeyboardButton(text="Отдышаться",
                                                                  callback_data=str('reload' + str(Fight.round)))
                    keyboard.add(callback_button1, callback_button2)
                    callback_button1 = types.InlineKeyboardButton(text="Подойти",
                                                                  callback_data=str('move' + str(Fight.round)))
                    keyboard.add(callback_button1)
                else:
                    callback_button1 = types.InlineKeyboardButton(text="Удар",
                                                                  callback_data=str('attack' + str(Fight.round)))
                    callback_button2 = types.InlineKeyboardButton(text="Отдышаться",
                                                                  callback_data=str('reload' + str(Fight.round)))
                    keyboard.add(callback_button1, callback_button2)
    else:
        if not p.weapon.Melee:
            callback_button2 = types.InlineKeyboardButton(text="Перезарядка",
                                                          callback_data=str('reload' + str(Fight.round)))
            keyboard.add(callback_button2)
        else:
            callback_button2 = types.InlineKeyboardButton(text="Отдышаться",
                                                          callback_data=str('reload' + str(Fight.round)))

            keyboard.add(callback_button2)
    if p.firecounter > 0:
        keyboard.add(types.InlineKeyboardButton(text='Потушиться', callback_data=str('skip' + str(Fight.round))),
                 types.InlineKeyboardButton(text='Инфо', callback_data=str('info')))
    else:
        keyboard.add(types.InlineKeyboardButton(text='Пропустить', callback_data=str('skip' + str(Fight.round))),
                 types.InlineKeyboardButton(text='Инфо', callback_data=str('info')))

    if not p.Armed:
        if len(p.itemlist) > 2:
            callback_button1 = types.InlineKeyboardButton(text="Дополнительно",
                                                      callback_data=str('inventory' + str(Fight.round)))
            keyboard.add(callback_button1)
        else:
            for c in p.itemlist:
                if p.energy >= 2:
                    keyboard.add(types.InlineKeyboardButton(text=c.name, callback_data=str(c.id + str(Fight.round))))
                elif c.energy is False:
                    keyboard.add(types.InlineKeyboardButton(text=c.name, callback_data=str(c.id + str(Fight.round))))

    else:
        callback_button1 = types.InlineKeyboardButton(text="Отменить",
                                                      callback_data=str('release' + str(Fight.round)))
        keyboard.add(callback_button1)

    p.choicemessage = bot.send_message(p.chat_id, utils.PlayerTurnInfo(p).string,reply_markup=keyboard)
    p.info.clear()

# Ожидание ответа
def wait_response(Fight):
    Fight.done = False
    Fight.fightstate = 'waiting'
    print('Ждем хода: ')
    for n in Fight.playerpool:
        print(n.name)
    timer = threading.Timer(120.0, timerd,[Fight])
    timer.start()
    i = 1
    while Fight.playerpool != [] and Fight.done is False:
        if len(Fight.playerpool) == 1 and i == 1:
            i+=1
        time.sleep(5)
    if Fight.done:
        for p in Fight.playerpool:
            print('Удаляем ход ' + p.name)
            p.turn = 'skip' + str(Fight.round)
            try:
                bot.edit_message_text(chat_id=p.chat_id, message_id=p.choicemessage.message_id, text="Ход " + str(Fight.round) + ': ''Время вышло!')
            except:
                pass
    Fight.playerpool = []
    timer.cancel()
    del timer


# Переключение счетчика
def timerd(Fight):
    Fight.done = True


# Осуществление действий
def manifest_actions(Fight):
    Fight.fightstate = 'action'
    for p in Fight.aiplayers:
        p.get_turn(Fight)
    manifest_used_q(Fight)

    for p in Fight.aiplayers:
        p.aiaction1q(Fight)
    manifest_first_q(Fight)
    for p in Fight.aiplayers:
        p.aiaction2q(Fight)
    manifest_second_q(Fight)
    Fight.string.post(bot, 'Ход ' + str(Fight.round))
    apply_effects(Fight)

    for p in Fight.aiplayers:
        p.aiactionlastq(Fight)
    manifest_last_q(Fight)
    Fight.string.post(bot, 'Эффекты ' + str(Fight.round))


# Действия до хода
def manifest_used_q(Fight):
    for p in Fight.actors:
        for i in p.useditems:
                i.used(p)
        for a in p.abilities:
            a.special_used(a,p)


# Действия первой очереди
def manifest_first_q(Fight):
    for p in Fight.actors:
        if p.turn[0:4] == 'item':
            for i in p.itemlist:
                if p.turn[0:7] == i.id:
                    i.usefirst(p)
                    break
        for a in p.abilities:
            a.special_first(a, p)


# Основные действия
def manifest_second_q(Fight):
    for p in Fight.actors:
        p.weapon.special_second(p)
        # Перезарядка
        if p.turn == 'reload' + str(Fight.round):
            p.energy = p.maxenergy
            if p.weapon.Melee or isinstance(p.weapon,Weapon_list.BowBleeding):
                Fight.string.add(u'\U0001F624' + "|" +
                                 p.name + ' переводит дух. Энергия восстановлена до максимальной! (' + str(
                                     p.energy) + ')')
            else:
                Fight.string.add(
                                 u'\U0001F553' + "|" +
                                 str(p.name + ' перезаряжается. Энергия восстановлена до максимальной! (' +
                                     str(p.energy) + ')'))

        # Стрельба; определение player.target
        elif p.turn == 'attack' + str(Fight.round):
            while p.target is None:
                pass
            p.action = str(p.attack(p.target))
            if p.target == p:
                p.action = p.action.replace('Противник','себя').replace('Игрок', p.name).replace('Цель', p.target.name)
            else:
                p.action = p.action.replace('Противник', p.target.name).replace('Игрок', p.name).replace('Цель', p.target.name)
            Fight.string.add(p.action)
        # Предмет
        elif p.turn[0:4] == 'item':
            for i in p.itemlist:
                if p.turn[0:7] == i.id:
                    p.action = i.use(p)
                    break
        # Пропуск хода\Тушение
        elif p.turn == 'skip' + str(Fight.round):
            if p.firecounter == 0:
                Fight.string.add(u'\U00002B07' + "|" + p.name + ' пропускает ход.')
            else:
                Fight.string.add(u'\U0001F4A8' + "|" + p.name + ' тушит себя.')
            p.extinguish = True
        # Целиться
        elif p.turn == 'aim':
            Fight.string.add(u'\U0001F3AF' + "|" + p.name + ' целится.')
        elif p.turn == 'draw':
            Fight.string.add(u'\U0001F3F9' + "|" + p.name + ' натягивает тетиву Лука Асгард.')

        # Целиться
        elif p.turn[0:4] == 'move':
            Fight.string.add(u'\U0001F463' + "|" + p.name + ' подходит к противнику вплотную.')
            p.Inmelee = True
        # Ошибка
        elif p.turn == 'suicide':
            p.Suicide = True
            Fight.string.add(u'\U00002620' + ' |' + p.name + ' решает покончить жизнь самоубийством.')
        elif p.turn is None:
            print('Ошибка в определении хода' + p.name)


# Эффекты
def apply_effects(Fight):
    for p in Fight.actors:
        if p.bleedcounter > 0:
            if p.bleedcounter >= 4:
                Fight.string.add(u'\U00002763' + "| Кровотечение отнимает у " + p.name + ' жизнь!')
                p.hp -= 1
                Fight.string.add(u'\U00002665' * p.hp + ' |' + str(p.name) +
                                 " теряет " + str(1) + " жизнь(ей). Остается " + str(p.hp) + " хп.")
                p.bleedcounter = 0
                p.bloodloss = True
            else:
                Fight.string.add(u'\U00002763' + "|" + p.name + ' истекает кровью!' + '(' + str(4-p.bleedcounter) + ')')
                p.bleedcounter += 1
        if p.firecounter > 0:
            if p.extinguish is True:
                p.firecounter = 0
                p.extinguish = False
            elif p.offfire == Fight.round:
                Fight.string.add(u'\U0001F525' + "| Огонь на " + p.name + ' потух!')
                p.firecounter = 0
            else:
                p.damagetaken += p.firecounter
                p.energy -= p.firecounter - 1
                if p.firecounter - 1 == 0:
                    Fight.string.add(u'\U0001F525' + "|" + p.name + ' горит! Получает ' + str(p.firecounter) + " урона.")
                else:
                    Fight.string.add(u'\U0001F525' + "|" + p.name + ' горит! Теряет '
                           + str(p.firecounter - 1) + " энергии и получает "  + str(p.firecounter) + " урона.")
        if p.stuncounter > 0:
            p.stuncounter -= 1
            if p.stuncounter == 0:
                Fight.string.add(u'\U0001F300' + '|' + p.name + ' приходит в себя.')


# Действия последней очереди
def manifest_last_q(Fight):
    for p in Fight.actors:
        if p.turn[0:4] == 'item':
            for i in p.itemlist:
                if p.turn[0:7] == i.id:
                    i.uselast(p)
                    break
        for a in p.abilities:
            a.special_last(a, p)

        for i in p.weaponeffect:
            i.effect(p)
        if p.damagetaken > 0 and p.armor > 0:
            if random.randint(1,100) <= p.armorchance:
                p.damagetaken -= p.armor
                Fight.string.add(u'\U0001F6E1' + '| Броня ' + p.name + ' снимает ' + str(p.armor) + ' урона!')
        if p.damagetaken < 0: p.damagetaken = 0


# Сброс переменных
def refresh_turn(Fight):
    for p in Fight.actors:
        p.turn = None
        p.target = None
        p.tempaccuracy = 0
        p.targets = []
        p.Blocked = False
        if p.accuracyfix > 0:
            p.accuracy -= p.accuracyfix
            p.accuracyfix = 0
        if p.damagefix > 0:
            p.bonusdamage -= p.damagefix
            p.damagefix = 0
        p.Hit = False
        p.Hitability = False
        if p.energy < 0: p.energy = 0
        if p.stuncounter > 0:
            p.Disabled = True
        else:
            p.Disabled = False
        if p.energy > p.maxenergy:
            p.energy = p.maxenergy
            Fight.string.add(p.name + ' теряет излишек энергии.')


# Результаты
def get_results(Fight):
    print('Урон команды 1 - ' + str(Fight.Team1.getteamdamage()))
    print('Урон команды 2 - ' + str(Fight.Team2.getteamdamage()))
    Fight.Team1.losthp = 0
    Fight.Team2.losthp = 0
    if Fight.Team1.damagetaken<Fight.Team2.damagetaken:
        Fight.string.add(u'\U00002757'+ "|" + 'Команда ' + Fight.Team1.actors[0].name + ' нанесла больше урона!')
        utils.ApplyDamage(Fight.Team2.actors)

    elif Fight.Team1.damagetaken == Fight.Team2.damagetaken == 0:
        Fight.string.add(u'\U00002757'+ "|" + 'Урона в раунде не нанесено!')

    elif Fight.Team1.damagetaken == Fight.Team2.damagetaken:
        Fight.string.add(u'\U00002757'+ "|" +  'Все команды понесли потери.')
        utils.ApplyDamage(Fight.activeplayers)
        utils.ApplyDamage(Fight.aiplayers)
    else:
        Fight.string.add(u'\U00002757'+ "|" + 'Команда ' + Fight.Team2.actors[0].name + ' нанесла больше урона!')
        utils.ApplyDamage(Fight.Team1.actors)
    for p in Fight.actors:
        for a in p.abilities:
            a.special_end(a, p)
        for a in p.enditems:
            a.used(p)
    for p in Fight.aiplayers:
        p.aiactionend(Fight)


def kill_players(Fight):
    Fight.Team1.damagetaken = 0
    Fight.Team2.damagetaken = 0
    for p in Fight.Game.players:
        p.damagetaken = 0
        p.hploss = 1
    for p in Fight.Game.players:
            if p.Suicide:
                p.Suicide = False
                p.Alive = False
                Fight.string.add(u'\U00002620' + ' |' + p.name + ' теряет сознание.')
                p.team.actors.remove(p)
                p.team.players.remove(p)
                p.team.deadplayers.append(p)
                Fight.activeplayers.remove(p)
                Fight.actors.remove(p)
            elif p.Alive == False and 'Zombie' in p.passive:

                if p.zombiecounter > 0:
                    p.zombiecounter -= 1
                    if p.zombiecounter == 0:
                        Fight.string.add(u'\U00002620' + ' |' + p.name + ' теряет сознание.')
                        p.team.actors.remove(p)
                        p.team.players.remove(p)
                        p.team.deadplayers.append(p)
                        Fight.activeplayers.remove(p)
                        Fight.actors.remove(p)

            elif p.hp <= 0 and p.Alive == True:
                p.Alive = False
                if 'Zombie' in p.passive:
                    p.bonusdamage += 2
                    p.zombiecounter = 2
                    Fight.string.add(u'\U0001F9DF' + ' |' + p.name + ' продолжает сражаться, истекая кровью!')
                else:
                    Fight.string.add(u'\U00002620' + ' |' +  p.name + ' теряет сознание.')
                    p.team.actors.remove(p)
                    p.team.players.remove(p)
                    p.team.deadplayers.append(p)
                    Fight.activeplayers.remove(p)
                    Fight.actors.remove(p)
    for p in Fight.Game.aiplayers:
            p.damagetaken = 0
            p.hploss = 1
    for p in Fight.Game.aiplayers:
        if p.hp <= 0 and p.Alive == True:
            p.Alive = False
            Fight.string.add(u'\U00002620' + ' |' + p.name + ' погибает.')
            p.team.deadplayers.append(p)
            p.team.actors.remove(p)
            Fight.aiplayers.remove(p)
            Fight.actors.remove(p)


def end(Fight, Game):
    if not Fight.Withbots:
        for p in Game.players:
            datahandler.add_played_games(p.chat_id)
        if not Fight.Team1.actors and not Fight.Team2.actors:
            bot.send_message(Game.cid, "Обе команды проиграли!")
        elif not Fight.Team1.actors:
            for p in Fight.Team2.participators:
                datahandler.add_won_games(p.chat_id)

            bot.send_message(Game.cid, "Команда " + Fight.Team1.leader.name + " потерпела поражение!")
            try:
                pic = bot.get_user_profile_photos(Fight.Team2.leader.chat_id).photos[0][0].file_id
                bot.send_photo(Game.cid, pic, "Команда " + Fight.Team2.leader.name + " победила!")
            except:
                bot.send_message(Game.cid, "Команда " + Fight.Team2.leader.name + " победила!")
        elif not Fight.Team2.actors:
            for p in Fight.Team1.participators:
                datahandler.add_won_games(p.chat_id)
            bot.send_message(Game.cid, "Команда " + Fight.Team2.leader.name + " потерпела поражение!")
            try:
                pic = bot.get_user_profile_photos(Fight.Team1.leader.chat_id).photos[0][0].file_id
                bot.send_photo(Game.cid, pic, "Команда " + Fight.Team1.leader.name + " победила!")
            except:
                bot.send_message(Game.cid, "Команда " + Fight.Team1.leader.name + " победила!")
    else:
        if not Fight.Team1.actors and not Fight.Team2.actors:
            bot.send_message(Game.cid, "Обе команды проиграли!")
        elif not Fight.Team1.actors:
            bot.send_message(Game.cid, "Команда " + Fight.Team1.leader.name + " потерпела поражение!")
            try:
                pic = Fight.Team2.leader.wonpic
                bot.send_document(Game.cid, pic, caption="Команда " + Fight.Team2.leader.name + " победила!")
            except AttributeError:
                bot.send_message(Game.cid, "Команда " + Fight.Team2.leader.name + " победила!")
        elif not Fight.Team2.actors:
            bot.send_message(Game.cid, "Команда " + Fight.Team2.leader.name + " потерпела поражение!")
            try:
                pic = bot.get_user_profile_photos(Fight.Team1.leader.chat_id).photos[0][0].file_id
                bot.send_photo(Game.cid, pic, "Команда " + Fight.Team1.leader.name + " победила!")
            except:
                bot.send_message(Game.cid, "Команда " + Fight.Team1.leader.name + " победила!")


def refresh(Game):
    for p in Game.players:
        try:
            del Main_classes.dict_players[p.chat_id]
        except KeyError:
            pass
    del Main_classes.dict_games[Game.cid]
    del Game


def fight(Game, Fight):

    print('Команда 1 - ' + ', '.join([p.name for p in Game.Team1.players]))
    print('Команда 2 - ' + ', '.join([p.name for p in Game.Team2.players]))

    Fight.Team1 = Game.Team1
    Fight.Team2 = Game.Team2
    Fight.Team1.leader = Game.Team1.actors[0]
    Fight.Team2.leader = Game.Team2.actors[0]
    Fight.actors = Fight.aiplayers + Fight.activeplayers
    for p in Game.players:
        if p.chat_id == 197216910:
            p.weapon = Weapon_list.spear
            p.weapon.aquare(p)
        p.hp = p.maxhp
        p.energy = p.maxenergy
        p.Alive = True
        p.team.participators.append(p)
    while Fight.Team1.actors != [] and Fight.Team2.actors != [] and Fight.round != 50:
        get_playerpool(Fight)
        send_actions(Fight)
        wait_response(Fight)
        manifest_actions(Fight)
        get_results(Fight)
        refresh_turn(Fight)
        kill_players(Fight)
        Fight.string.post(bot, 'Результат хода ' + str(Fight.round))
    end(Fight, Game)
    refresh(Game)


def account_targets(player, Fight):
    if not player.weapon.Melee:
        player.targets = utils.GetOtherTeam(player).actors
    else:
        if player.Inmelee:
            player.targets = utils.GetOtherTeam(player).actors
        else:
            for p in utils.GetOtherTeam(player).actors:
                if p.weapon.Melee and p.Inmelee:
                    player.targets.append(p)
        blockers = []
        for p in player.targets:
            if special_abilities.Blocker in p.abilities:
                blockers.append(p)
        if blockers != []:
            player.targets = blockers
            player.Blocked = True

