import utils
import config
import telebot
import copy
import random
import Weapon_list
import special_abilities

bot = telebot.TeleBot(config.token)
types = telebot.types
itemlist = []

# itema - предмет от способности
# itemt - предмет с целью
# itemat - предмет от способности с целью
# itemh - предмет, не траятящий хода
# iteme - предмет, тратящий энергию


class Item(object):
    acting = False

    def __init__(self, name, item_id, standart=True):
        self.name = name
        self.id = item_id
        self.energy = False
        self.standart = standart
        if self.standart:
            itemlist.append(self)
        if self.id[0:5] == 'iteme':
            self.energy = True

    def usenow(self, user):
        pass

    def aquare(self, user):
        pass

    def usefirst(self, user):
        pass

    def use(self, user):
        pass

    def uselast(self, user):
        pass

    def usebefore(self, user):
        pass


class Grenade(Item):
    def use(self, user):
        damage = random.randint(2, 3)
        enemycount = len(utils.get_other_team(user).actors)
        if enemycount > 2:
            target1 = utils.get_other_team(user).actors[random.randint(0, enemycount-1)]
            newtargets = list(utils.get_other_team(user).actors)
            newtargets.remove(target1)
            target2 = newtargets[random.randint(0, enemycount-2)]
            utils.damage(user, target1, damage, 'explosion')
            utils.damage(user, target2, damage, 'explosion')
            user.fight.string.add(u'\U0001F4A3' + " |" + user.name + ' кидает Гранату! Нанесено ' + str(damage)
                                  + ' урона по ' + target2.name + ' и ' + target1.name + '.')
        else:
            for c in utils.get_other_team(user).actors:
                utils.damage(user, c, damage, 'melee')
            user.fight.string.add(u'\U0001F4A3' + " |" + user.name + ' кидает Гранату! Нанесено ' + str(
                                  damage) + ' урона.')
        user.energy -= 2
        user.itemlist.remove(self)


class Firegrenade(Item):
    def use(self, user):
        enemycount = len(utils.get_other_team(user).actors)
        targets = []
        if enemycount > 2:
            target1 = utils.get_other_team(user).actors[random.randint(0, enemycount-1)]
            newtargets = list(utils.get_other_team(user).actors)
            newtargets.remove(target1)
            target2 = newtargets[random.randint(0, enemycount-2)]
            newtargets = list(utils.get_other_team(user).actors)
            newtargets.remove(target2)
            target1.firecounter += 1
            target1.offfire = user.fight.round + 2
            targets.append(target1)
            if random.randint(1, 3) > 1:
                target2.firecounter += 1
                target2.offfire = user.fight.round + 2
                targets.append(target2)

        else:
            utils.get_other_team(user).actors[0].firecounter += 1
            utils.get_other_team(user).actors[0].offfire = user.fight.round + 2
            targets.append(utils.get_other_team(user).actors[0])
            for c in utils.get_other_team(user).actors[1:]:
                if random.randint(1, 3) > 1:
                    c.firecounter += 1
                    c.offfire = user.fight.round + 2
                    targets.append(c)
        if targets:
            user.fight.string.add(u'\U0001F378' + " |" + user.name + ' кидает Коктейль Молотова! '
                                  + ', '.join([x.name for x in targets]) + ' в огне!')
        else:
            user.fight.string.add(u'\U0001F378' + " |" + user.name
                                  + ' кидает Коктейль Молотова, но ни по кому не попадает!')
        user.energy -= 2
        user.itemlist.remove(self)


class GasGrenade(Item):
    def useact(self, user):
        keyboard = types.InlineKeyboardMarkup()
        for p in utils.get_other_team(user).actors:
            callback_button = types.InlineKeyboardButton(text=p.name, callback_data='spitem' + str(p.chat_id))
            keyboard.add(callback_button)
        keyboard.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('spitemcancel')))
        bot.send_message(user.chat_id, 'Выберите цель для гранаты.',
                         reply_markup=keyboard)

    def use(self, user):
        user.fight.string.add(u'\U0001F635' + " |" + user.name + ' кидает Световую гранату в '
                              + user.itemtarget.name + '. (- 8 Энергии)')
        del user.itemtarget
        user.itemlist.remove(self)

    def usefirst(self, user):
        if special_abilities.Impaler in user.itemtarget.abilities:
            user.fight.string.add(u'\U0000274C' + "|" + user.itemtarget.name + ' игнорирует вспышку.')
        elif special_abilities.Gasmask in user.itemtarget.abilities:
            user.fight.string.add(u'\U0000274C' + "|" + user.itemtarget.name + ' защищен от вспышки. (-1 Энергии)')
            user.itemtarget.energy -= 1
        else:
            user.itemtarget.energy -= 8


class Shield(Item):
    def useact(self, user):
        keyboard = types.InlineKeyboardMarkup()
        for p in user.team.actors:
            callback_button = types.InlineKeyboardButton(text=p.name,callback_data='spitem' + str(p.chat_id))
            keyboard.add(callback_button)
        keyboard.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('spitemcancel')))
        bot.send_message(user.chat_id, 'Выберите цель для щита.',reply_markup=keyboard)

    def use(self, user):
        if user.itemtarget == user:
            user.fight.string.add(u'\U0001F535' + " |" + user.name + ' использует щит. Урон отражен!')
        else:
            user.fight.string.add(u'\U0001F535' + " |" + user.name + ' использует щит на ' + user.itemtarget.name + '. Урон отражен!')

    def uselast(self, user):
        user.itemtarget.damagetaken = 0
        user.itemlist.remove(self)
        del user.itemtarget


class ThrowingKnife(Item):

    def useact(self, user):
        keyboard = types.InlineKeyboardMarkup()
        for p in utils.get_other_team(user).actors:
            callback_button = types.InlineKeyboardButton(text=p.name,callback_data='spitem' + str(p.chat_id))
            keyboard.add(callback_button)
        keyboard.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('spitemcancel')))
        chance = (user.energy + 4)*10
        if chance > 100:
            chance = 100
        bot.send_message(user.chat_id, 'Выберите цель для ножа. Шанс попасть - ' + str(chance) + '%',reply_markup=keyboard)

    def use(self, user):
        if random.randint(1, 10)<=user.energy + 5:
            user.fight.string.add(u'\U0001F52A' + " |" + user.name + ' кидает Метательный Нож в '
                                  + user.itemtarget.name + '. Нанесено 1 урона ' +
                                  u'\U00002763' + "|" + user.itemtarget.name + ' истекает кровью!')
            utils.damage(user, user.itemtarget, 1, 'melee')
            user.itemtarget.bleedcounter += 1
            user.itemtarget.bloodloss = False

        else:
            user.fight.string.add(u'\U0001F4A8' + " |" + user.name + ' кидает Метательный Нож, но не попадает.')
        user.itemlist.remove(self)
        user.energy -= 1
        del user.itemtarget


class Jet(Item):
    def useact(self, user):
        bot.send_message(user.chat_id, 'Через 3 хода ваша энергия полностью восстановится!')
        user.useditems.append(self)
        user.itemlist.remove(self)

    def used(self, user):
        user.fight.string.add(u'\U0001F489' + " |" + user.name + ' использует Джет.')
        user.jetturn = user.fight.round + 2
        user.Drugged = True
        user.abilities.append(special_abilities.Jet)


class Chitin(Item):
    def useact(self, user):
        bot.send_message(user.chat_id, 'Вы получаете 2 брони на 3 хода! В конце третьего вы будете оглушены.')
        user.useditems.append(self)
        user.itemlist.remove(self)

    def used(self, user):
        user.fight.string.add(u'\U0001F489' + " |" + user.name + ' использует Хитин.')
        user.chitinoff = user.fight.round + 2
        user.armor += 2
        user.armorchance += 100
        user.Drugged = True
        user.abilities.append(special_abilities.Chitin)


class Drug(Item):
    def useact(self, user):
        bot.send_message(user.chat_id, 'В начале раунда ваша энергия увеличится на 3!')
        user.useditems.append(self)
        user.itemlist.remove(self)

    def used(self, user):
        user.energy += 3
        user.Drugged = True
        user.fight.string.add(u'\U0001F489' + " |" + user.name + ' использует Адреналин, увеличивая энергию на 3.')


class Heal(Item):
    def useact(self, user):
        keyboard = types.InlineKeyboardMarkup()
        for p in user.team.actors:
            if p.Alive:
                callback_button = types.InlineKeyboardButton(text=p.name,callback_data='spitem' + str(p.chat_id))
                keyboard.add(callback_button)
        keyboard.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('spitemcancel')))
        bot.send_message(user.chat_id, 'Выберите цель для лечения.',reply_markup=keyboard)


    def use(self, user):
        if user.itemtarget == user:
            user.fight.string.add(u'\U0001F489' + " |" + user.name + ' использует стимулятор.')
        else:
            user.fight.string.add(u'\U0001F489' + " |" + user.name + ' использует стимулятор на ' + user.itemtarget.name + '.')
        user.enditems.append(self)
        user.itemlist.remove(self)

    def used(self, user):
        user.itemtarget.hp += 2
        user.Drugged = True
        if user.itemtarget.hp > user.itemtarget.maxhp: user.itemtarget.hp = user.itemtarget.maxhp
        user.fight.string.add(u'\U00002665'*user.itemtarget.hp + u'\U0001F489' + " |" + user.itemtarget.name + ' получает 2 хп. Остается ' + str(user.itemtarget.hp)
                                     + ' хп.')
        user.enditems.remove(self)
        del user.itemtarget



drug = Drug('Адреналин','itemh01')
shield = Shield('Щит', 'itemt02')
gasgrenade = GasGrenade('Световая Граната', 'itemt04')
grenade = Grenade('Граната', 'iteme01')
firegrenade = Firegrenade('Коктейль', 'iteme02')
throwingknife = ThrowingKnife('Метательный Нож', 'itemt03')
jet = Jet('Джет', 'itemh02')
chitin = Chitin('Хитин', 'itemh03')
heal = Heal('Стимулятор', 'itemt01', standart=False)
id_items = list(itemlist)


class Shieldg(Item):
    def useact(self, user):
        keyboard = types.InlineKeyboardMarkup()
        for p in user.team.actors:
            callback_button = types.InlineKeyboardButton(text=p.name, callback_data='spitem' + str(p.chat_id))
            keyboard.add(callback_button)
        keyboard.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('spitemcancel')))
        bot.send_message(user.chat_id, 'Выберите цель для щита.', reply_markup=keyboard)
    def use(self, user):
        if user.itemtarget == user:
            user.fight.string.add(u'\U0001F535' + " |" + user.name + ' использует щит. Урон отражен!')
        else:
            user.fight.string.add(u'\U0001F535' + " |" + user.name + ' использует щит на ' + user.itemtarget.name + '. Урон отражен!')
    def uselast(self, user):
        user.shieldrefresh = user.fight.round + 4
        user.itemtarget.damagetaken = 0
        user.itemlist.remove(self)
        del user.itemtarget


class Hypnosys(Item):
    def useact(self, user):
        keyboard = types.InlineKeyboardMarkup()
        for p in utils.get_other_team(user).actors:
            callback_button = types.InlineKeyboardButton(text=p.name, callback_data='spitem' + str(p.chat_id))
            keyboard.add(callback_button)
        keyboard.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('spitemcancel')))
        bot.send_message(user.chat_id, 'Выберите цель для гипноза.', reply_markup=keyboard)

    def usefirst(self, user):
        user.energy -= 3
        if user.itemtarget.target is None:
            user.fight.string.add(
                    u'\U0001F31D' + "|" + 'Гипнотизеру ' + user.name + " не удается сбить прицел " + user.itemtarget.name
                    + '.')
        elif random.randint(1,100) > user.itemtarget.hypnosysresist:
            user.itemtarget.target = user.itemtarget.team.actors[
                    random.randint(0, len(user.itemtarget.team.actors) - 1)]
            user.fight.string.add(
                    u'\U0001F31A' + "|" + 'Гипнотизер ' + user.name + " сбивает прицел " + user.itemtarget.name
                    + '. Новая цель - ' + user.itemtarget.target.name + '!')

            user.itemtarget.tempaccuracy -= 2
        else:
            user.fight.string.add(
                    u'\U0001F31D' + "|" + 'Гипнотизер ' + user.name + " сбивает прицел, но " + user.itemtarget.name
                    + ' сопротивляется Гипнозу!')
            user.itemtarget.tempaccuracy -= 10
        user.hypnosysrefresh = user.fight.round + 5
        user.itemlist.remove(self)
        del user.itemtarget


class Isaev(Item):

    def useact(self, user):
        keyboard = types.InlineKeyboardMarkup()
        for p in utils.get_other_team(user).actors:
            callback_button = types.InlineKeyboardButton(text=p.name, callback_data='spitem' + str(p.chat_id))
            keyboard.add(callback_button)
        keyboard.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('spitemcancel')))
        bot.send_message(user.chat_id, 'Выберите цель для оскорбления.', reply_markup=keyboard)

    def usefirst(self, user):
        if random.randint(1, 100) <= 8:
            user.fight.string.add(
                u'\U0001F595' + u'\U0001F494' + "|" + 'Исаев ' + user.name + " посылает " + user.itemtarget.name
                + ' нахуй. ' + user.itemtarget.name + ' теряет веру в себя!')
            user.itemtarget.Suicide = True
        else:
            user.fight.string.add(
                u'\U0001F595' + "|" + 'Исаев ' + user.name + " посылает " + user.itemtarget.name
                + ' нахуй.')
        user.isaevrefresh = user.fight.round + 2
        user.itemlist.remove(self)
        del user.itemtarget


class Mental(Item):
    def useact(self, user):
        keyboard = types.InlineKeyboardMarkup()
        for p in utils.get_other_team(user).actors:
            callback_button = types.InlineKeyboardButton(text=p.name, callback_data='info' + str(p.chat_id))
            keyboard.add(callback_button)
        keyboard.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('infocancel')))
        bot.send_message(user.chat_id, 'Выберите цель для получения информации.', reply_markup=keyboard)


class Engineer(Item):
    def useact(self, user):
        keyboard = types.InlineKeyboardMarkup()
        for p in user.team.players:
            if not p.weapon.Melee and p != user:
                callback_button = types.InlineKeyboardButton(text=p.name, callback_data='spitem' + str(p.chat_id))
                keyboard.add(callback_button)
        keyboard.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('spitemcancel')))
        bot.send_message(user.chat_id, 'Выберите цель для получения информации.', reply_markup=keyboard)

    def use(self, user):
        user.fight.string.add(u'\U0001F527' + " |" + user.name + ' перезаряжает оружие ' + user.itemtarget.name + '. Энергия восстановлена до максимальной! (' + str(
            user.itemtarget.maxenergy) + ')')
        user.itemtarget.energy = user.itemtarget.maxenergy
        user.engineerrefresh = user.fight.round + 3


    def uselast(self, user):
        user.itemtarget.accuracy += 2
        user.itemtarget.accuracyfix += 2
        user.itemtarget.bonusdamage += 2
        user.itemtarget.damagefix += 2
        user.itemlist.remove(self)
        del user.itemtarget


class Ritual(Item):
    def useact(self, user):
        keyboard = types.InlineKeyboardMarkup()
        cureses = list(user.fight.actors)
        for p in cureses:
            callback_button = types.InlineKeyboardButton(text=p.name, callback_data='spitem' + str(p.chat_id))
            keyboard.add(callback_button)
        keyboard.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('spitemcancel')))
        bot.send_message(user.chat_id, 'Выберите жертву.', reply_markup=keyboard)

    def use(self, user):
        user.fight.string.add(u'\U0001F47F' + " |" + user.name + ' чертит странные символы на земле.')
        user.cursecounter = 5
        user.cursetarget = user.itemtarget
        user.itemlist.remove(self)


class Curse(Item):
    def useact(self, user):
        keyboard = types.InlineKeyboardMarkup()
        for p in user.fight.actors:
            callback_button = types.InlineKeyboardButton(text=p.name, callback_data='spitem' + str(p.chat_id))
            keyboard.add(callback_button)
        keyboard.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('spitemcancel')))
        bot.send_message(user.chat_id, 'Выберите цель для проклятия.', reply_markup=keyboard)

    def use(self, user):
        user.fight.string.add(u'\U0001F47F' + " |" + user.name + ' поднимает руки к небу. Разряд молнии'
                                                                 ' бьет в ' + user.itemtarget.name + '.')
        user.itemtarget.hp -= 2
        user.fight.string.add(u'\U00002665' * user.itemtarget.hp + ' |' + str(user.itemtarget.name) +
                         " теряет " + str(2) + " жизнь(ей). Остается " + str(user.itemtarget.hp) + " хп.")
        user.itemlist.remove(self)


class Explode_corpse(Item):
    def use(self, user):
        damage = random.randint(2, 3)
        enemycount = len(utils.get_other_team(user).actors)
        if enemycount > 2:
            target1 = utils.get_other_team(user).actors[random.randint(0, enemycount - 1)]
            newtargets = list(utils.get_other_team(user).actors)
            newtargets.remove(target1)
            target2 = newtargets[random.randint(0, enemycount - 2)]
            utils.damage(user, target1, damage, 'melee')
            utils.damage(user, target2, damage, 'melee')
            user.fight.string.add(u'\U0001F47F' + " |" + user.name + ' взрывает труп! Нанесено ' + str(damage)
                                  + ' урона по ' + target2.name + ' и ' + target1.name + '.')
        else:
            for c in utils.get_other_team(user).actors:
                utils.damage(user, c, damage, 'melee')
            user.fight.string.add(u'\U0001F47F' + " |" + user.name + ' взрывает труп! Нанесено ' + str(
                damage) + ' урона.')
        user.corpsecounter -= 1
        user.itemlist.remove(self)


class Zombie(Item):

    def useact(self, user):
        keyboard = types.InlineKeyboardMarkup()
        zombies = list(user.team.deadplayers)
        for p in zombies:
            if not p.bot:
                callback_button = types.InlineKeyboardButton(text=p.name, callback_data='spitem' + str(p.chat_id))
                keyboard.add(callback_button)
        keyboard.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('spitemcancel')))
        bot.send_message(user.chat_id, 'Выберите зомби.', reply_markup=keyboard)

    def use(self, user):
        user.fight.string.add(u'\U0001F47F' + " |" + user.name + ' поднимает зомби.')
        if Zombie not in user.itemtarget.abilities:
            user.itemtarget.abilities = []
            user.itemtarget.itemlist = []
            user.itemtarget.passive = []
            user.itemtarget.truedamage = 0
            user.itemtarget.accuracy = 0
            user.itemtarget.mult = 1
            user.itemtarget.armor = 0
            user.itemtarget.armorchance = 0
            user.itemtarget.tempaccuracy = 0
            user.itemtarget.firecounter = 0
            user.itemtarget.bleedcounter = 0
            user.itemtarget.stuncounter = 0
            user.itemtarget.maxenergy = 0
            user.itemtarget.maxhp = 0
            user.itemtarget.weapon = Weapon_list.fangs
            user.itemtarget.abilities.append(special_abilities.Zombie)
            user.itemtarget.team.actors.append(user.itemtarget)
            user.itemtarget.team.players.append(user.itemtarget)
            try:
                user.itemtarget.team.deadplayers.remove(user.itemtarget)
            except ValueError:
                pass
            user.itemtarget.fight.activeplayers.append(user.itemtarget)
            user.itemtarget.fight.actors.append(user.itemtarget)
            user.itemtarget.hungercounter = 3
            user.itemtarget.accuracy = 7 - user.itemtarget.hungercounter*2
            user.itemtarget.turn = 'raise'
            user.itemlist.remove(self)


class Steal(Item):

    def useact(self, user):
        keyboard = types.InlineKeyboardMarkup()
        for p in utils.get_other_team(user).actors:
            callback_button = types.InlineKeyboardButton(text=p.name, callback_data='spitem' + str(p.chat_id))
            keyboard.add(callback_button)
        keyboard.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('spitemcancel')))
        bot.send_message(user.chat_id, 'Выберите цель для кражи.', reply_markup=keyboard)

    def usebefore(self, user):
        if user.itemtarget.turn[:4] == 'item' and user.itemtarget.turn[:5] != 'itema':
            user.itemtarget.turn = 'loss' + user.itemtarget.turn
            for i in user.itemtarget.itemlist:
                if i.id == user.itemtarget.turn[4:11]:
                    user.itemtarget.itemlist.remove(i)
                    user.itemlist.append(i)
                    user.stolenitem = i.name
                    break
        elif user.itemtarget.useditems:
            x = user.itemtarget.useditems[-1]
            user.itemtarget.useditems.remove(x)
            user.itemlist.append(x)
            user.stolenitem = x.name


    def use(self, user):
        if not user.itemtarget.itemlist:
            bot.send_message(user.chat_id, 'У цели нет предметов!')
        if user.itemtarget.turn[0:4] == 'loss':
            user.fight.string.add(
                u'\U0001F60F' + "|" + user.itemtarget.name + " пытается использовать " + user.stolenitem
                + ', но предмет оказывается в руках у ' + user.name + '!')
            user.itemtarget.turn = 'losе'
            del user.stolenitem
        elif hasattr(user, 'stolenitem'):
            user.fight.string.add(
                u'\U0001F60F' + "|" + user.itemtarget.name + " пытается использовать " + user.stolenitem
                + ', но предмет оказывается в руках у ' + user.name + '!')
            del user.stolenitem
        else:
            user.fight.string.add(
                u'\U0001F612' + "|" + 'Вору ' + user.name + ' не удается ничего украсть!')
        user.stealrefresh = user.fight.round + 2
        user.itemlist.remove(self)
        del user.itemtarget


class WeaponMaster(Item):

    def useact(self, user):
        new = copy.copy(user.weapon)
        user.weapon = user.sec_weapon
        user.sec_weapon = new
        bot.send_message(user.chat_id, 'Вы меняете оружие.')
        user.useditems.append(self)
        user.itemlist.remove(self)
        user.change_refresh = user.fight.round

    def used(self, user):
        user.fight.string.add(u'\U0001F60F' + "|" +  user.name + " достает " + user.weapon.name + '!')


class ThrowingSpear(Item):
    def useact(self, user):
        keyboard = types.InlineKeyboardMarkup()
        for p in utils.get_other_team(user).actors:
            callback_button = types.InlineKeyboardButton(text=p.name,callback_data='spitem' + str(p.chat_id))
            keyboard.add(callback_button)
        keyboard.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('spitemcancel')))
        chance = utils.get_hit_chance(user, 0)
        bot.send_message(user.chat_id, 'Выберите цель для копья. Шанс попасть - ' + str(int(chance)) + '%',reply_markup=keyboard)

    def use(self, user):
        n = 0
        d = 0
        dmax = 5
        while d != dmax:
            x = random.randint(1, 10)
            print(user.name + ' Выпало ' + str(x))
            if x > 10 - user.energy - user.accuracy - user.tempaccuracy - 1:
                n += 1
            d += 1
        for a in user.abilities:
            n = a.onhit(a, n, user)
        # бонусный урон персонажа
        if n != 0:
            n += user.bonusdamage + 1
        # уходит энергия
        user.energy -= 3
        utils.damage(user, user.itemtarget, n, 'melee')
        if n != 0:
            user.fight.string.add(u'\U0001F4A5' + " |" + user.name + ' кидает Копье Нарсил в '
                                  + user.itemtarget.name + '. Нанесено ' + str(n) + ' урона!')

        else:
            user.fight.string.add(u'\U0001F4A8' + " |" + user.name + ' кидает Копье Нарсил, но не попадает.')
        user.itemlist.remove(self)
        user.throwcd += 3
        user.lostweapon = Weapon_list.speareternal
        del user.itemtarget


zombie = Zombie('Поднять мертвеца', 'itemat6',standart=False)
shieldg = Shieldg('Щит|Генератор', 'itemat1',standart=False)
hypnosys = Hypnosys('Гипноз', 'itemat2',standart=False)
isaev = Isaev('Оскорбления', 'itemat7',standart=False)
steal = Steal('Украсть', 'itemat8',standart=False)
mental = Mental('Визор', 'mitem01',standart=False)
engineer = Engineer('Наводчик', 'itemat3',standart=False)
ritual = Ritual('Ритуал', 'itemat4',standart=False)
curse = Curse('Проклятие', 'itemat5',standart=False)
change_weapon = WeaponMaster('Сменить оружие', 'itemh03',standart=False)
explode_corpse = Explode_corpse('Взорвать труп', 'itema01',standart=False)
throwspear = ThrowingSpear('Метнуть', 'itemat9',standart=False)
id_items.append(shieldg)
id_items.append(hypnosys)
id_items.append(mental)
id_items.append(isaev)
id_items.append(change_weapon)
id_items.append(engineer)
id_items.append(ritual)
id_items.append(curse)
id_items.append(heal)
id_items.append(zombie)
id_items.append(steal)
id_items.append(explode_corpse)
id_items.append(throwspear)
items = {p.id:p for p in id_items}
