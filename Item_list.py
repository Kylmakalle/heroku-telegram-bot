import Main_classes
import utils
import config
import telebot
import random
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

    def __init__(self, name, id, standart = True):
        self.name = name
        self.id = id
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


class Grenade(Item):
    def use(self, user):
        damage = random.randint(2,3)
        enemycount = len(utils.GetOtherTeam(user).actors)
        if enemycount > 2:
            target1 = utils.GetOtherTeam(user).actors[random.randint(0,enemycount-1)]
            newtargets = list(utils.GetOtherTeam(user).actors)
            newtargets.remove(target1)
            target2 = newtargets[random.randint(0,enemycount-2)]
            target1.damagetaken += damage
            target2.damagetaken += damage
            user.Fight.string.add(u'\U0001F4A3' + " |" + user.name + ' кидает Гранату! Нанесено ' + str(damage) + ' урона по ' + target2.name + ' и ' + target1.name + '.')
        else:
            for c in utils.GetOtherTeam(user).actors:
                c.damagetaken += damage
            user.Fight.string.add(u'\U0001F4A3' + " |" + user.name + ' кидает Гранату! Нанесено ' + str(
            damage) + ' урона.')
        user.energy -= 2
        user.itemlist.remove(self)


class Firegrenade(Item):
    def use(self, user):
        enemycount = len(utils.GetOtherTeam(user).actors)
        targets = []
        if enemycount > 2:
            target1 = utils.GetOtherTeam(user).actors[random.randint(0,enemycount-1)]
            newtargets = list(utils.GetOtherTeam(user).actors)
            newtargets.remove(target1)
            target2 = newtargets[random.randint(0,enemycount-2)]
            newtargets = list(utils.GetOtherTeam(user).actors)
            newtargets.remove(target2)
            target1.firecounter += 1
            target1.offfire = user.Fight.round + 2
            targets.append(target1)
            if random.randint(1, 3) > 1:
                target2.firecounter += 1
                target2.offfire = user.Fight.round + 2
                targets.append(target2)

        else:
            utils.GetOtherTeam(user).actors[0].firecounter += 1
            utils.GetOtherTeam(user).actors[0].offfire = user.Fight.round + 2
            targets.append(utils.GetOtherTeam(user).actors[0])
            for c in utils.GetOtherTeam(user).actors[1:]:
                if random.randint(1, 3) > 1:
                    c.firecounter += 1
                    c.offfire = user.Fight.round + 2
                    targets.append(c)
        if targets != []:
            user.Fight.string.add(u'\U0001F378' + " |" + user.name + ' кидает Коктейль Молотова! ' + ', '.join([x.name for x in targets]) + ' в огне!')
        else:
            user.Fight.string.add(u'\U0001F378' + " |" + user.name + ' кидает Коктейль Молотова, но ни по кому не попадает!')
        user.energy -= 2
        user.itemlist.remove(self)


class GasGrenade(Item):
    def usefirst(self, user):
        user.Fight.string.add(u'\U0001F922' + " |" + user.name + ' кидает Газовую гранату! Противники задыхаются ядовитым газом! ( - 6 Энергии)')
        for c in utils.GetOtherTeam(user).actors:
            if special_abilities.Impaler in c.abilities:
                if c.turn == 'rhino_rest' + str(user.Fight.round):
                    c.turn = 'rhino_poisoned' + str(user.Fight.round)
                else:
                    user.Fight.string.add(u'\U0000274C' + "|" + c.name + ' игнорирует ядовитое облако.')
            elif special_abilities.Gasmask in c.abilities:
                user.Fight.string.add(u'\U0000274C' + "|" + c.name + ' защищен от ядовитого газа. (-1 Энергии)')
                c.energy -= 1
            else:
                c.energy -= 6
        user.itemlist.remove(self)


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
            user.Fight.string.add(u'\U0001F535' + " |" + user.name + ' использует щит. Урон отражен!')
        else:
            user.Fight.string.add(u'\U0001F535' + " |" + user.name + ' использует щит на ' + user.itemtarget.name + '. Урон отражен!')

    def uselast(self, user):
        user.itemtarget.damagetaken = 0
        user.itemlist.remove(self)
        del user.itemtarget


class Drug(Item):

    def useact(self, user):
        user.energy += 3
        bot.send_message(user.chat_id, 'Энергия увеличена на 3!')
        user.useditems.append(self)
        user.itemlist.remove(self)

    def used(self, user):
        user.Fight.string.add(u'\U0001F489' + " |" + user.name + ' использует Адреналин, увеличивая энергию на 3.')
        user.useditems.remove(self)


class Heal(Item):

    def useact(self, user):
        keyboard = types.InlineKeyboardMarkup()
        for p in user.team.actors:
            callback_button = types.InlineKeyboardButton(text=p.name,callback_data='spitem' + str(p.chat_id))
            keyboard.add(callback_button)
        keyboard.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('spitemcancel')))
        bot.send_message(user.chat_id, 'Выберите цель для лечения.',reply_markup=keyboard)


    def use(self, user):
        if user.itemtarget == user:
            user.Fight.string.add(u'\U0001F489' + " |" + user.name + ' использует стимулятор.')
        else:
            user.Fight.string.add(u'\U0001F489' + " |" + user.name + ' использует стимулятор на ' + user.itemtarget.name + '.')
        user.enditems.append(self)
        user.itemlist.remove(self)

    def used(self, user):
        user.itemtarget.hp += 2
        if user.itemtarget.hp > user.itemtarget.maxhp: user.itemtarget.hp = user.itemtarget.maxhp
        user.Fight.string.add(u'\U00002665'*user.itemtarget.hp + u'\U0001F489' + " |" + user.itemtarget.name + ' получает 2 хп. Остается ' + str(user.itemtarget.hp)
                                     + ' хп.')
        user.enditems.remove(self)
        del user.itemtarget




drug = Drug('Адреналин','itemh01')
shield = Shield('Щит', 'itemt02')
gasgrenade = GasGrenade('Газовая Граната', 'item001')
grenade = Grenade('Граната', 'iteme01')
firegrenade = Firegrenade('Коктейль', 'iteme02')
heal = Heal('Стимулятор', 'itemt01')
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
            user.Fight.string.add(u'\U0001F535' + " |" + user.name + ' использует щит. Урон отражен!')
        else:
            user.Fight.string.add(u'\U0001F535' + " |" + user.name + ' использует щит на ' + user.itemtarget.name + '. Урон отражен!')
    def uselast(self, user):
        user.shieldrefresh = user.Fight.round + 4
        user.itemtarget.damagetaken = 0
        user.itemlist.remove(self)
        del user.itemtarget


class Hypnosys(Item):
    def useact(self, user):
        keyboard = types.InlineKeyboardMarkup()
        for p in utils.GetOtherTeam(user).actors:
            callback_button = types.InlineKeyboardButton(text=p.name, callback_data='spitem' + str(p.chat_id))
            keyboard.add(callback_button)
        keyboard.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('spitemcancel')))
        bot.send_message(user.chat_id, 'Выберите цель для гипноза.', reply_markup=keyboard)

    def usefirst(self, user):
        if not isinstance(user.itemtarget, Main_classes.Player):
            if random.randint(1,100) > user.itemtarget.hypnosysresist:
                user.itemtarget.target = user.itemtarget.team.actors[
                    random.randint(0, len(user.itemtarget.team.actors) - 1)]
                user.Fight.string.add(
                    u'\U0001F31A' + "|" + 'Гипнотизер ' + user.name + " сбивает прицел " + user.itemtarget.name
                    + '. Новая цель - ' + user.itemtarget.target.name + '!')

                user.itemtarget.tempaccuracy -= 2
            else:
                user.Fight.string.add(
                    u'\U0001F31D' + "|" + 'Гипнотизер ' + user.name + " сбивает прицел, но " + user.itemtarget.name
                    + ' сопротивляется Гипнозу!')
                user.itemtarget.tempaccuracy -= 10
        elif user.itemtarget.target != None:
            user.itemtarget.target = user.itemtarget.team.actors[
                random.randint(0, len(user.itemtarget.team.actors) - 1)]
            user.Fight.string.add(u'\U0001F31A' + "|" + 'Гипнотизер ' + user.name + " сбивает прицел " + user.itemtarget.name
                       + '. Новая цель - ' + user.itemtarget.target.name + '!')

            user.itemtarget.tempaccuracy -= 2
        else:
            user.Fight.string.add(u'\U0001F31D' + "|" + 'Гипнотизеру ' + user.name + " не удается сбить прицел " + user.itemtarget.name
                       + '.')

        user.hypnosysrefresh = user.Fight.round + 5
        user.itemlist.remove(self)
        del user.itemtarget


class Mental(Item):
    def useact(self, user):
        keyboard = types.InlineKeyboardMarkup()
        for p in utils.GetOtherTeam(user).actors:
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
        user.Fight.string.add(u'\U0001F527' + " |" + user.name + ' перезаряжает оружие ' + user.itemtarget.name + '. Энергия восстановлена до максимальной! (' + str(
            user.itemtarget.maxenergy) + ')')
        user.itemtarget.energy = user.itemtarget.maxenergy
        user.engineerrefresh = user.Fight.round + 3


    def uselast(self, user):
        user.itemtarget.accuracy += 1
        user.itemtarget.accuracyfix += 1
        user.itemlist.remove(self)
        del user.itemtarget


class Ritual(Item):
    def useact(self, user):
        keyboard = types.InlineKeyboardMarkup()
        cureses = list(user.Fight.actors)
        for p in cureses:
            callback_button = types.InlineKeyboardButton(text=p.name, callback_data='spitem' + str(p.chat_id))
            keyboard.add(callback_button)
        keyboard.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('spitemcancel')))
        bot.send_message(user.chat_id, 'Выберите жертву.', reply_markup=keyboard)

    def use(self, user):
        user.Fight.string.add(u'\U0001F47F' + " |" + user.name + ' чертит странные символы на земле.')
        user.cursecounter = 4
        user.cursetarget = user.itemtarget
        user.itemlist.remove(self)


class Curse(Item):
    def useact(self, user):
        keyboard = types.InlineKeyboardMarkup()
        for p in user.Fight.actors:
            callback_button = types.InlineKeyboardButton(text=p.name, callback_data='spitem' + str(p.chat_id))
            keyboard.add(callback_button)
        keyboard.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('spitemcancel')))
        bot.send_message(user.chat_id, 'Выберите цель для проклятия.', reply_markup=keyboard)

    def use(self, user):
        user.Fight.string.add(u'\U0001F47F' + " |" + user.name + ' поднимает руки к небу. Разряд молнии'
                                                                 ' бьет в ' + user.itemtarget.name + '.')
        user.itemtarget.hp -= 2
        user.Fight.string.add(u'\U00002665' * user.itemtarget.hp + ' |' + str(user.itemtarget.name) +
                         " теряет " + str(2) + " жизнь(ей). Остается " + str(user.itemtarget.hp) + " хп.")
        user.itemlist.remove(self)

shieldg = Shieldg('Щит|Генератор', 'itemat1',standart=False)
hypnosys = Hypnosys('Гипноз', 'itemat2',standart=False)
mental = Mental('Визор', 'mitem01',standart=False)
engineer = Engineer('Оружейник', 'itemat3',standart=False)
ritual = Ritual('Ритуал', 'itemat4',standart=False)
curse = Curse('Проклятие', 'itemat5',standart=False)
id_items.append(shieldg)
id_items.append(hypnosys)
id_items.append(mental)
id_items.append(engineer)
id_items.append(ritual)
id_items.append(curse)
items = {p.id:p for p in id_items}