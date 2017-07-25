import utils
import config
import telebot
import threading
import time
import Weapon_list
import random
import special_abilities

bot = telebot.TeleBot(config.token)
types = telebot.types


# Собираем пул активных игроков
def get_playerpool(fight):
    fight.round += 1
    fight.fightstate = 'playerpool'
    for p in fight.activeplayers:
        if p.Disabled:
            p.turn = 'disabled'
        elif p.Alive:
            fight.playerpool.append(p)
        elif 'Zombie' in p.passive:
            if p.zombiecounter > 0:
                fight.playerpool.append(p)
        elif special_abilities.Zombie in p.abilities:
            fight.playerpool.append(p)


# Рассылаем варианты действий
def send_actions(fight):
    for p in fight.playerpool:
        account_targets(p)
        send_action(p, fight)
        print('Послан список действий для ' + p.name)


# Описание вариантов действий
def send_action(p, fight):
    keyboard = types.InlineKeyboardMarkup()
    if p.energy > 0:
        if not p.weapon.Melee:
            callback_button1 = types.InlineKeyboardButton(text="Выстрел", callback_data=str('attack'
                                                                                            + str(fight.round)))
            callback_button2 = types.InlineKeyboardButton(text="Перезарядка", callback_data=str('reload'
                                                                                                + str(fight.round)))
            keyboard.add(callback_button1, callback_button2)
        else:
            if p.Inmelee:
                callback_button1 = types.InlineKeyboardButton(text="Удар",
                                                              callback_data=str('attack' + str(fight.round)))
                callback_button2 = types.InlineKeyboardButton(text="Отдышаться",
                                                              callback_data=str('reload' + str(fight.round)))
                keyboard.add(callback_button1, callback_button2)
            else:
                if not p.targets:
                    callback_button1 = types.InlineKeyboardButton(text="Подойти",
                                                                  callback_data=str('move' + str(fight.round)))
                    callback_button2 = types.InlineKeyboardButton(text="Отдышаться",
                                                                  callback_data=str('reload' + str(fight.round)))
                    keyboard.add(callback_button1, callback_button2)
                elif len(p.targets) < len(utils.get_other_team(p).actors):
                    callback_button1 = types.InlineKeyboardButton(text="Удар",
                                                                  callback_data=str('attack' + str(fight.round)))
                    callback_button2 = types.InlineKeyboardButton(text="Отдышаться",
                                                                  callback_data=str('reload' + str(fight.round)))
                    keyboard.add(callback_button1, callback_button2)
                    callback_button1 = types.InlineKeyboardButton(text="Подойти",
                                                                  callback_data=str('move' + str(fight.round)))
                    keyboard.add(callback_button1)
                else:
                    callback_button1 = types.InlineKeyboardButton(text="Удар",
                                                                  callback_data=str('attack' + str(fight.round)))
                    callback_button2 = types.InlineKeyboardButton(text="Отдышаться",
                                                                  callback_data=str('reload' + str(fight.round)))
                    keyboard.add(callback_button1, callback_button2)
    elif special_abilities.Zombie in p.abilities:
        if not p.targets:
            callback_button1 = types.InlineKeyboardButton(text="Подойти",
                                                          callback_data=str('move' + str(fight.round)))
            keyboard.add(callback_button1)
        elif len(p.targets) < len(utils.get_other_team(p).actors):
            callback_button1 = types.InlineKeyboardButton(text="Удар",
                                                          callback_data=str('attack' + str(fight.round)))
            keyboard.add(callback_button1)
            callback_button1 = types.InlineKeyboardButton(text="Подойти",
                                                          callback_data=str('move' + str(fight.round)))
            keyboard.add(callback_button1)
        else:
            callback_button1 = types.InlineKeyboardButton(text="Удар",
                                                          callback_data=str('attack' + str(fight.round)))
            keyboard.add(callback_button1)
    else:
        if not p.weapon.Melee:
            callback_button2 = types.InlineKeyboardButton(text="Перезарядка",
                                                          callback_data=str('reload' + str(fight.round)))
            keyboard.add(callback_button2)
        else:
            callback_button2 = types.InlineKeyboardButton(text="Отдышаться",
                                                          callback_data=str('reload' + str(fight.round)))

            keyboard.add(callback_button2)
    if p.firecounter > 0:
        keyboard.add(types.InlineKeyboardButton(text='Потушиться', callback_data=str('skip' + str(fight.round))),
                     types.InlineKeyboardButton(text='Инфо', callback_data=str('info')))
    else:
        keyboard.add(types.InlineKeyboardButton(text='Пропустить', callback_data=str('skip' + str(fight.round))),
                     types.InlineKeyboardButton(text='Инфо', callback_data=str('info')))

    if not p.Armed:
        if len(p.itemlist) > 2:
            callback_button1 = types.InlineKeyboardButton(text="Дополнительно",
                                                          callback_data=str('inventory' + str(fight.round)))
            keyboard.add(callback_button1)
        else:
            for c in p.itemlist:
                if p.energy >= 2:
                    keyboard.add(types.InlineKeyboardButton(text=c.name, callback_data=str(c.id + str(fight.round))))
                elif c.energy is False:
                    keyboard.add(types.InlineKeyboardButton(text=c.name, callback_data=str(c.id + str(fight.round))))

    else:
        callback_button1 = types.InlineKeyboardButton(text="Отменить",
                                                      callback_data=str('release' + str(fight.round)))
        keyboard.add(callback_button1)
    if p.lostweapon is not None:
        keyboard.add(types.InlineKeyboardButton(text='Подобрать оружие', callback_data=str('take' + str(fight.round))))

    p.choicemessage = bot.send_message(p.chat_id, utils.player_turn_info(p).string, reply_markup=keyboard)
    p.info.clear()


# Ожидание ответа
def wait_response(fight):
    fight.done = False
    fight.fightstate = 'waiting'
    print('Ждем хода: ')
    for n in fight.playerpool:
        print(n.name)
    timer = threading.Timer(120.0, timerd, [fight])
    timer.start()
    i = 1
    while fight.playerpool and fight.done is False:
        if len(fight.playerpool) == 1 and i == 1:
            i += 1
        time.sleep(5)
    if fight.done:
        for p in fight.playerpool:
            print('Удаляем ход ' + p.name)
            p.turn = 'skip' + str(fight.round)
            bot.edit_message_text(chat_id=p.chat_id, message_id=p.choicemessage.message_id,
                                  text="Ход " + str(fight.round) + ': ''Время вышло!')
        fight.playerpool = []
    timer.cancel()
    del timer


# Переключение счетчика
def timerd(fight):
    fight.done = True


# Осуществление действий
def manifest_actions(fight):
    fight.fightstate = 'action'
    for p in fight.aiplayers:
        p.get_turn(fight)
    manifest_used_q(fight)
    for p in fight.aiplayers:
        p.aiaction1q(fight)
    manifest_first_q(fight)
    for p in fight.aiplayers:
        p.aiaction2q(fight)
    manifest_second_q(fight)
    fight.string.post(bot, 'Ход ' + str(fight.round))
    apply_effects(fight)

    for p in fight.aiplayers:
        p.aiactionlastq(fight)
    manifest_last_q(fight)
    fight.string.post(bot, 'Эффекты ' + str(fight.round))


# Действия до хода
def manifest_used_q(fight):
    for p in fight.actors:
        for i in p.useditems:
                i.used(p)
        for a in p.abilities:
            a.special_used(a, p)


# Действия первой очереди
def manifest_first_q(fight):
    for p in fight.actors:
        if p.turn[0:4] == 'item':
            for i in p.itemlist:
                if p.turn[0:7] == i.id:
                    i.usebefore(p)
                    break
        if p.turn[0:4] == 'item':
            for i in p.itemlist:
                if p.turn[0:7] == i.id:
                    i.usefirst(p)
                    break
        for a in p.abilities:
            a.special_first(a, p)


# Основные действия
def manifest_second_q(fight):
    for p in fight.actors:
        p.weapon.special_second(p)
        # Перезарядка
        if p.turn == 'reload' + str(fight.round):
            p.energy = p.maxenergy
            if p.weapon.Melee or isinstance(p.weapon, Weapon_list.BowBleeding):
                fight.string.add(u'\U0001F624' + "|" +
                                 p.name + ' переводит дух. Энергия восстановлена до максимальной! (' + str(
                                     p.energy) + ')')
            else:
                fight.string.add(
                                 u'\U0001F553' + "|" +
                                 str(p.name + ' перезаряжается. Энергия восстановлена до максимальной! (' +
                                     str(p.energy) + ')'))

        # Стрельба; определение player.target
        elif p.turn == 'attack' + str(fight.round):
            while p.target is None:
                pass
            p.action = str(p.attack())
            if p.target == p:
                p.action = p.action.replace('Противник', 'себя').replace('Игрок', p.name).replace('Цель', p.target.name)
            else:
                p.action = p.action.replace('Противник', p.target.name).replace('Игрок', p.name)\
                    .replace('Цель', p.target.name)
            fight.string.add(p.action)
        # Предмет
        elif p.turn[0:4] == 'item':
            for i in p.itemlist:
                if p.turn[0:7] == i.id:
                    p.action = i.use(p)
                    break
        # Пропуск хода\Тушение
        elif p.turn == 'skip' + str(fight.round):
            if p.firecounter == 0:
                fight.string.add(u'\U00002B07' + "|" + p.name + ' пропускает ход.')
            else:
                fight.string.add(u'\U0001F4A8' + "|" + p.name + ' тушит себя.')
            p.extinguish = True
        elif p.turn == 'draw':
            fight.string.add(u'\U0001F3F9' + "|" + p.name + ' натягивает тетиву Лука Асгард.')
        elif p.turn == 'take' + str(fight.round):
            fight.string.add(u'\U0000270B' + "|" + p.name + ' подбирает потерянное оружие.')
            p.weapon = p.lostweapon
            p.weapon.aquare(p)
            p.lostweapon = None
        # Целиться
        elif p.turn[0:4] == 'move':
            fight.string.add(u'\U0001F463' + "|" + p.name + ' подходит к противнику вплотную.')
            p.Inmelee = True
        # Ошибка
        elif p.turn == 'suicide':
            p.Suicide = True
            fight.string.add(u'\U00002620' + ' |' + p.name + ' решает покончить жизнь самоубийством.')
        elif p.turn is None:
            print('Ошибка в определении хода' + p.name)


# Эффекты
def apply_effects(fight):
    for p in fight.actors:
        if p.bleedcounter > 0 and special_abilities.Sturdy.Sturdy in p.abilities:
            if p.bleedcounter >= 6:
                fight.string.add(u'\U00002763' + "| Кровотечение отнимает у " + p.name + ' жизнь!')
                p.hp -= 1
                fight.string.add(u'\U00002665' * p.hp + ' |' + str(p.name) +
                                 " теряет " + str(1) + " жизнь(ей). Остается " + str(p.hp) + " хп.")
                p.bleedcounter = 0
                p.bloodloss = True
            else:
                fight.string.add(u'\U00002763' + "|" + p.name + ' истекает кровью!' + '(' + str(6-p.bleedcounter) + ')')
                p.bleedcounter += 1
        elif p.bleedcounter > 0:
            if p.bleedcounter >= 4:
                fight.string.add(u'\U00002763' + "| Кровотечение отнимает у " + p.name + ' жизнь!')
                p.hp -= 1
                fight.string.add(u'\U00002665' * p.hp + ' |' + str(p.name) +
                                 " теряет " + str(1) + " жизнь(ей). Остается " + str(p.hp) + " хп.")
                p.bleedcounter = 0
                p.bloodloss = True
            else:
                fight.string.add(u'\U00002763' + "|" + p.name + ' истекает кровью!' + '(' + str(4-p.bleedcounter) + ')')
                p.bleedcounter += 1
        if p.firecounter > 0:
            if p.extinguish is True:
                p.firecounter = 0
                p.extinguish = False
            elif p.offfire == fight.round:
                fight.string.add(u'\U0001F525' + "| Огонь на " + p.name + ' потух!')
                p.firecounter = 0
            else:
                p.damagetaken += p.firecounter
                p.energy -= p.firecounter - 1
                if p.firecounter - 1 == 0:
                    fight.string.add(u'\U0001F525' + "|" + p.name
                                     + ' горит! Получает ' + str(p.firecounter) + " урона.")
                else:
                    fight.string.add(u'\U0001F525' + "|" + p.name + ' горит! Теряет '
                                     + str(p.firecounter - 1) + " энергии и получает " + str(p.firecounter) + " урона.")
        if p.stuncounter > 0:
            p.stuncounter -= 1
            if p.stuncounter == 0:
                fight.string.add(u'\U0001F300' + '|' + p.name + ' приходит в себя.')


# Действия последней очереди
def manifest_last_q(fight):
    for p in fight.actors:
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
            if random.randint(1, 100) <= p.armorchance:
                p.damagetaken -= p.armor
                fight.string.add(u'\U0001F6E1' + '| Броня ' + p.name + ' снимает ' + str(p.armor) + ' урона!')
        if p.damagetaken < 0:
            p.damagetaken = 0


# Сброс переменных
def refresh_turn(fight):
    for p in fight.actors:
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
        if p.energy < 0:
            p.energy = 0
        if p.stuncounter > 0:
            p.Disabled = True
        else:
            p.Disabled = False
        if p.lostweapon == p.weapon:
            p.weapon = Weapon_list.fists
            p.lostweapon.lose(p)
        if p.energy > p.maxenergy:
            p.energy = p.maxenergy
            fight.string.add(p.name + ' теряет излишек энергии.')


# Результаты
def get_results(fight):
    print('Урон команды 1 - ' + str(fight.team1.getteamdamage()))
    print('Урон команды 2 - ' + str(fight.team2.getteamdamage()))
    fight.team1.losthp = 0
    fight.team2.losthp = 0
    if fight.team1.damagetaken < fight.team2.damagetaken:
        fight.string.add(u'\U00002757' + "|" + 'Команда ' + fight.team1.actors[0].name + ' нанесла больше урона!')
        utils.apply_damage(fight.team2.actors)

    elif fight.team1.damagetaken == fight.team2.damagetaken == 0:
        fight.string.add(u'\U00002757' + "|" + 'Урона в раунде не нанесено!')

    elif fight.team1.damagetaken == fight.team2.damagetaken:
        fight.string.add(u'\U00002757' + "|" + 'Все команды понесли потери.')
        utils.apply_damage(fight.activeplayers)
        utils.apply_damage(fight.aiplayers)
    else:
        fight.string.add(u'\U00002757' + "|" + 'Команда ' + fight.team2.actors[0].name + ' нанесла больше урона!')
        utils.apply_damage(fight.team1.actors)
    for p in fight.actors:
        p.weapon.special_end(p)
        for a in p.enditems:
            a.used(p)
        for a in p.abilities:
            a.special_end(a, p)
    for p in fight.aiplayers:
        p.aiactionend(fight)


def kill_players(fight):
    fight.team1.damagetaken = 0
    fight.team2.damagetaken = 0
    for p in fight.game.players:
        p.damagetaken = 0
        p.hploss = 1
        if p.hp < 0:
            p.hp = 0
        p.Losthp = False
    for p in fight.game.players:
            if special_abilities.Zombie in p.abilities:
                pass
            elif p.Suicide:
                p.Suicide = False
                p.Alive = False
                fight.string.add(u'\U00002620' + ' |' + p.name + ' кончает жизнь самоубийством.')
                p.team.actors.remove(p)
                p.team.players.remove(p)
                p.team.deadplayers.append(p)
                fight.activeplayers.remove(p)
                fight.actors.remove(p)
            elif not p.Alive and 'Zombie' in p.passive:
                if p.zombiecounter > 0:
                    p.zombiecounter -= 1
                    if p.zombiecounter == 0:
                        fight.string.add(u'\U00002620' + ' |' + p.name + ' теряет сознание.')
                        p.team.actors.remove(p)
                        p.team.players.remove(p)
                        p.team.deadplayers.append(p)
                        fight.activeplayers.remove(p)
                        fight.actors.remove(p)
            elif p.hp <= 0 and p.Alive:
                p.Alive = False
                if 'Zombie' in p.passive:
                    p.bonusdamage += 2
                    p.zombiecounter = 2
                    fight.string.add(u'\U0001F62C' + ' |' + p.name + ' продолжает сражаться, истекая кровью!')
                else:
                    fight.string.add(u'\U00002620' + ' |' + p.name + ' теряет сознание.')
                    p.team.actors.remove(p)
                    p.team.players.remove(p)
                    p.team.deadplayers.append(p)
                    fight.activeplayers.remove(p)
                    fight.actors.remove(p)
    for p in fight.game.aiplayers:
        p.damagetaken = 0
        p.hploss = 1
        if p.hp < 0:
            p.hp = 0
        p.Losthp = False
    for p in fight.game.aiplayers:
        if p.hp <= 0 and p.Alive:
            p.Alive = False
            fight.string.add(u'\U00002620' + ' |' + p.name + ' погибает.')
            p.team.deadplayers.append(p)
            p.team.actors.remove(p)
            fight.aiplayers.remove(p)
            fight.actors.remove(p)
        elif p.Suicide:
            p.Suicide = False
            p.Alive = False
            fight.string.add(u'\U00002620' + ' |' + p.name + ' кончает жизнь самоубийством.')
            p.team.deadplayers.append(p)
            p.team.actors.remove(p)
            fight.aiplayers.remove(p)
            fight.actors.remove(p)


def end(fight, game):
    if not fight.Withbots:
        if not fight.team1.actors and not fight.team2.actors:
            bot.send_message(game.cid, "Обе команды проиграли!")
        elif not fight.team1.actors:
            bot.send_message(game.cid, "Команда " + fight.team1.leader.name + " потерпела поражение!")
            try:
                pic = bot.get_user_profile_photos(fight.team2.leader.chat_id).photos[0][0].file_id
                bot.send_photo(game.cid, pic, "Команда " + fight.team2.leader.name + " победила!")
            except:
                bot.send_message(game.cid, "Команда " + fight.team2.leader.name + " победила!")
        elif not fight.team2.actors:
            bot.send_message(game.cid, "Команда " + fight.team2.leader.name + " потерпела поражение!")
            try:
                pic = bot.get_user_profile_photos(fight.team1.leader.chat_id).photos[0][0].file_id
                bot.send_photo(game.cid, pic, "Команда " + fight.team1.leader.name + " победила!")
            except:
                bot.send_message(game.cid, "Команда " + fight.team1.leader.name + " победила!")
    else:
        if not fight.team1.actors and not fight.team2.actors:
            bot.send_message(game.cid, "Обе команды проиграли!")
        elif not fight.team1.actors:
            bot.send_message(game.cid, "Команда " + fight.team1.leader.name + " потерпела поражение!")
            try:
                pic = fight.team2.leader.wonpic
                bot.send_document(game.cid, pic, caption="Команда " + fight.team2.leader.name + " победила!")
            except:
                bot.send_message(game.cid, "Команда " + fight.team2.leader.name + " победила!")
        elif not fight.team2.actors:
            bot.send_message(game.cid, "Команда " + fight.team2.leader.name + " потерпела поражение!")
            try:
                pic = bot.get_user_profile_photos(fight.team1.leader.chat_id).photos[0][0].file_id
                bot.send_photo(game.cid, pic, "Команда " + fight.team1.leader.name + " победила!")
            except:
                bot.send_message(game.cid, "Команда " + fight.Team1.leader.name + " победила!")


def fight_loop(game, fight):

    fight.team1 = game.team1
    fight.team2 = game.team2
    fight.team1.leader = game.team1.actors[0]
    fight.team2.leader = game.team2.actors[0]
    fight.actors = fight.aiplayers + fight.activeplayers
    for p in game.players:

        if p.chat_id == 86190439:
            p.abilities.append(special_abilities.Isaev)
            special_abilities.Isaev.aquare(p.abilities, p)
        p.hp = p.maxhp
        if p.chat_id == 253478906:
            fight.string.add(u'\U00002620' + ' |' + 'В Вегана бьёт молния! Он теряет 4 хп.')
            p.hp -= 4
        p.energy = p.maxenergy
        p.Alive = True
        p.team.participators.append(p)
    while fight.team1.actors != [] and fight.team2.actors != [] and fight.round != 50:
        fight.string.add('Команда 1 - ' + ', '.join([p.name for p in game.team1.actors]))
        fight.string.add('Команда 2 - ' + ', '.join([p.name for p in game.team2.actors]))
        get_playerpool(fight)
        send_actions(fight)
        wait_response(fight)
        manifest_actions(fight)
        get_results(fight)
        refresh_turn(fight)
        kill_players(fight)
        fight.string.post(bot, 'Результат хода ' + str(fight.round))
    end(fight, game)
    utils.delete_game(game)


def account_targets(player):
    if not player.weapon.Melee:
        player.targets = utils.get_other_team(player).actors
    else:
        if player.Inmelee:
            player.targets = utils.get_other_team(player).actors
        else:
            for p in utils.get_other_team(player).actors:
                if p.weapon.Melee and p.Inmelee:
                    player.targets.append(p)
        blockers = []
        for p in player.targets:
            if special_abilities.Blocker in p.abilities:
                blockers.append(p)
        if blockers:
            player.targets = blockers
            player.Blocked = True
