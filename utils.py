import Main_classes
import config
import telebot
import random
import special_abilities
import Weapon_list



types = telebot.types
bot = telebot.TeleBot(config.token)


def GetOtherTeam(player):
    if player.team == player.Fight.Team1:
        return player.Game.Team2
    elif player.team == player.Game.Team2:
        return player.Game.Team1


def AddPlayer(playerchat_id, player_name, Game):
    Game.player_ids.append(playerchat_id)
    Game.players.append(Main_classes.Player(playerchat_id, player_name, None, Game))
    Main_classes.dict_players[playerchat_id] = Game


def RemovePlayer(playerchat_id, Game):
    removing = None
    for p in Game.players:
        if p.chat_id == playerchat_id:
            removing = p
    Game.player_ids.remove(playerchat_id)
    try:
        removing.team.remove(removing)
    except AttributeError:
        pass
    Game.players.remove(removing)
    del Main_classes.dict_players[playerchat_id]


def GetAbility(player):
    keyboard = types.InlineKeyboardMarkup()
    maxchoiceint = 5
    choice = []
    while len(choice) < maxchoiceint:
        x = special_abilities.abilities[random.randint(0,len(special_abilities.abilities)-1)]
        if player.weapon.Melee:
            if len(player.team.players) == 1:
                if x not in choice and x not in player.abilities and not x.RangeOnly and not x.TeamOnly:
                    choice.append(x)
            else:
                if x not in choice and x not in player.abilities and not x.RangeOnly:
                    choice.append(x)

        else:
            if len(player.team.players) == 1:
                if x not in choice and x not in player.abilities and not x.MeleeOnly and not x.TeamOnly:
                    choice.append(x)
            else:
                if x not in choice and x not in player.abilities and not x.MeleeOnly:
                    choice.append(x)

    for c in choice:
        callback_button1 = types.InlineKeyboardButton(text=c.name,
                                                      callback_data=str('a' + str(special_abilities.abilities.index(c))))
        callback_button2 = types.InlineKeyboardButton(text='Инфо',
                                                      callback_data=str('i' + str(special_abilities.abilities.index(c))))
        keyboard.add(callback_button1, callback_button2)
    bot.send_message(player.chat_id, 'Выберите способность. Ваш максимум способностей - ' + str(player.maxabilities), reply_markup=keyboard)


def GetWeapon(player):
    keyboard = types.InlineKeyboardMarkup()
    maxchoiceint = 3
    choice = []
    while len(choice) < maxchoiceint:
        x = Weapon_list.weaponlist[random.randint(0, len(Weapon_list.weaponlist) - 1)]
        if any(c == x for c in choice) == False:
            choice.append(x)
    for c in choice:
        callback_button1 = types.InlineKeyboardButton(text=c.name,
                                                      callback_data=str(
                                                          'a' + c.name))
        keyboard.add(callback_button1)
    bot.send_message(player.chat_id, 'Выберите оружие.',
                     reply_markup=keyboard)


def ActorFromId(id, Game):
    player = Game.player_dict[int(id)]
    return player


def PlayerInfo(player, cid=None):
    player.info.add(player.name)
    player.info.add(u'\U00002665'*player.hp + "|" +str(player.hp) + ' жизней. Максимум: ' + str(player.maxhp))
    player.info.add(u'\U000026A1'*player.energy + "|" + str(player.energy) + ' энергии. Максимум: '+ str(player.maxenergy))
    player.info.add("Способности: " + ", ".join([x.name for x in player.abilities]))
    templist = []
    for x in player.itemlist:
        if x.standart:
            templist.append(x)
    player.info.add("Предметы: " + ", ".join([x.name for x in templist]))
    player.info.add("Оружие: " + player.weapon.name + ' - ' + player.weapon.damagestring)
    if player.weapon == Weapon_list.bow:
        player.info.add(u'\U0001F3AF' + " | Вероятность попасть - " + str(int(GetHitChance(player, player.bonusaccuracy)))
                        + '%')
    else:
        player.info.add(u'\U0001F3AF' + " | Вероятность попасть - " + str(int(GetHitChance(player, 0)))
                    + '%')
    if cid== None:
        if player.weapon == Weapon_list.sniper and player.aimtarget != None:
            player.info.add(u'\U0001F3AF' + " |" 'Вероятность попасть в ' + ActorFromId(player.aimtarget, player.Game).name + ' - '
                            + str(int(GetHitChance(player,player.bonusaccuracy)))+ '%')

        player.info.post(bot, 'Информация')
    else:
        player.info.post(bot, 'Информация', cid=cid)


def PlayerTurnInfo(player):
    player.info.add('Ход ' + str(player.Fight.round))
    player.info.add(u'\U00002665'*player.hp + "|" +str(player.hp) + ' жизней. Максимум: ' + str(player.maxhp))
    player.info.add(u'\U000026A1'*player.energy + "|" + str(player.energy) + ' энергии. Максимум: '+ str(player.maxenergy))
    if player.weapon == Weapon_list.bow:
        player.info.add(u'\U0001F3AF' + " | Вероятность попасть - " + str(int(GetHitChance(player, player.bonusaccuracy)))
                        + '%')
    else:
        player.info.add(u'\U0001F3AF' + " | Вероятность попасть - " + str(int(GetHitChance(player, 0)))
                    + '%')
    if player.weapon == Weapon_list.sniper:
        if player.aimtarget != None:
            player.info.add(u'\U0001F3AF' + " |" 'Вероятность попасть в ' + ActorFromId(player.aimtarget, player.Game).name + ' - '
                            + str(int(GetHitChance(player,player.bonusaccuracy)))+ '%')
    return player.info


def GetHitChance(player, bonus):
    hitdice = 10 - player.energy - player.weapon.bonus - player.accuracy - bonus
    print (hitdice)
    onechance = 100 - (10*hitdice)

    if hitdice >= 10 or player.energy == 0:
        onechance = 0
    elif hitdice <= 0:
        onechance = 100
        return onechance
    dmax = player.weapon.dice
    print(onechance)
    d = 1
    tempchance = onechance
    while d != dmax:
        tempchance += (100 - tempchance) * (onechance/100)
        d += 1
    return tempchance


def ApplyDamage(targets):
    for p in targets:
        if p.damagetaken != 0:
            if p.damagetaken >= 6: p.hploss += 1
            if p.damagetaken >= 12: p.hploss += 1
            if p.damagetaken >= 18: p.hploss += 1
            if special_abilities.Armorer in p.abilities:
                p.hp -= 1
                p.team.losthp += 1
                if p.hploss > 1: p.Fight.string.add(u'\U0001F480'+ '|Крепкий череп ' + p.name + ' предотвращает потерю жизней.')
                p.Fight.string.add(u'\U00002665' * p.hp + ' |' + str(p.name) +
                           " теряет " + str(1) + " жизнь(ей). Остается " + str(p.hp) + " хп.")
            else:
                p.hp -= p.hploss
                p.team.losthp += p.hploss
                p.Fight.string.add(u'\U00002665' * p.hp + ' |' + str(p.name) +
                           " теряет " + str(p.hploss) + " жизнь(ей). Остается " + str(p.hp) + " хп.")


def Teamchat(text, player):
    player.message = u'\U00002757'+ "| " + player.name + ": " + text
    return str(player.name + ' что-то говорит.')


def GetGamefromChat(id):
    try:
        return Main_classes.dict_games[id]
    except:
        print('Игра не найдена!')
        return None


def GetGamefromPlayer(id):
    try:
        return Main_classes.dict_players[id]
    except:
        print('Игрок не найден!')
        return None


def sendinventory(player):
    keyboard = types.InlineKeyboardMarkup()
    for p in player.itemlist:
        keyboard.add(types.InlineKeyboardButton(text=p.name, callback_data=str(p.id + str(player.Fight.round))))
    keyboard.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('cancel')))
    bot.send_message(player.chat_id, 'Выберите предмет.', reply_markup=keyboard)


def sendskills(player):
    keyboard = types.InlineKeyboardMarkup()
    for p in player.itemlist:
        if p.standart == False:
            keyboard.add(types.InlineKeyboardButton(text=p.name, callback_data=str(p.id + str(player.Fight.round))))
    keyboard.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('cancel')))
    bot.send_message(player.chat_id, 'Выберите навык.', reply_markup=keyboard)
