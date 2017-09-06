import random
import telebot
import config
import utils
import Item_list

types = telebot.types
bot = telebot.TeleBot(config.token)
weaponlist = []
fullweaponlist = []


class Weapon(object):
    def __init__(self, dice, damage, energy, bonus, fixed, Melee, TwoHanded, Concealable, name, damagestring, standart=True, pellets=False, natural=False):
        self.dice = dice
        self.damage = damage
        self.energy = energy
        self.fixed = fixed
        self.bonus = bonus
        self.Melee = Melee
        self.TwoHanded = TwoHanded
        self.Concealable = Concealable
        self.name = name
        self.damagestring = damagestring
        self.standart = standart
        self.pellets = pellets
        self.natural = natural
        if self.standart == True:
            weaponlist.append(self)
        fullweaponlist.append(self)

    # Выстрел
    def hit(self,user):
        n = 0
        d = 0
        dmax = self.dice
        print(user.name + " стреляет из " + str(self.name) + '. Его энергия - ' + str(
            user.energy) + '. Его точность и бонусная точность оружия - '
              + str(user.accuracy) + ' ' + str(self.bonus) + ' ' +
              '. Шанс попасть - ' + str(10 - user.energy - self.bonus - user.accuracy - user.tempaccuracy) + "+!")
        while d != dmax:
            x = random.randint(1, 10)
            print(user.name + ' Выпало ' + str(x))
            if x > 10 - user.energy - self.bonus - user.accuracy - user.tempaccuracy + user.target.evasion:

                n += 1
                print('+1 суммарный урон.')
            else:
                print('мимо.')
            d += 1
        print('Всего урона ' + str(n))

        # бонусный урон персонажа
        if n != 0:
            n += user.bonusdamage + self.damage - 1
            if self.pellets and user.target.weapon.Melee and user.target.Inmelee:
                n += 1
        for a in user.abilities:
            n = a.onhit(a,n, user)
        # уходит энергия
        if self.fixed > 0 and n > 0:
            n = self.fixed
        user.energy -= self.energy
        # энергия загоняется в 0
        if user.energy < 0: user.energy = 0

        utils.damage(user, user.target, n, 'hit')
        return n

    # При экипировке
    def aquare(self,user):
        pass

    # Создание описания
    def getDesc(self, damagetaken,user):
        if damagetaken != 0:
            if not self.Melee:
                d = str(u'\U0001F4A5' + "|" + getattr(self,str('desc' + str(random.randint(1, 3)))) + " Нанесено " + str(damagetaken) + ' урона.')
            else:
                d = str(u'\U0001F44A' + "|" + getattr(self,str('desc' + str(random.randint(1, 3)))) + " Нанесено " + str(damagetaken) + ' урона.')
                for a in user.abilities:
                    d = a.onhitdesc(a,d,user)
        else:
            d = str(u'\U0001F4A8' + "|" + getattr(self,str('desc' + str(random.randint(4, 6)))))
        return d

    # Отправка вариантов
    def get_action(self, p, call):
        keyboard1 = types.InlineKeyboardMarkup()
        targets = p.targets
        p.turn = call.data
        if p.Blocked:
            for c in targets:
                keyboard1.add(types.InlineKeyboardButton(text=c.name, callback_data=str('op' + str(c.chat_id))))
            keyboard1.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('opcancel')))
            bot.send_message(p.chat_id, targets[0].name +' не дает вам подобраться к противнику.', reply_markup=keyboard1)

        elif len(targets) == 1:
            p.target = targets[0]
            try:
                p.fight.playerpool.remove(p)
            except:
                print('Упс.')
        else:
            for c in targets:
                keyboard1.add(types.InlineKeyboardButton(text=c.name, callback_data=str('op' + str(c.chat_id))))
            keyboard1.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('opcancel')))
            bot.send_message(p.chat_id, 'Выберите противника.', reply_markup=keyboard1)

    # Особое действие
    def special(self, user, call):
        pass

    #На конец хода
    def special_end(self, user):
        pass

    def special_second(self, user):
        pass

    def special_first(self, user):
        pass

    def lose(self,user):
        pass

    def effect(self, user):
        pass


class Tazer(Weapon):
    def effect(self, user):
        user.target.energy -= 1
        user.weaponeffect.remove(self)

    def getDesc(self, damagetaken, user):
        if damagetaken != 0:
            user.weaponeffect.append(self)
            d = str(u'\U0001F44A' + u'\U000026A1'+ "|" + getattr(self,str('desc' + str(random.randint(1, 3)))) + " Нанесено " + str(damagetaken) + ' урона. ' + user.target.name + ' теряет 1 Энергию.')
            for a in user.abilities:
                d = a.onhitdesc(a,d,user)
        else:
            d = str(u'\U0001F4A8' + "|" + getattr(self,str('desc' + str(random.randint(4, 6)))))
        return d

    desc1 = 'Игрок бьет Противник Полицейской Дубинкой.'
    desc2 = 'Игрок бьет Противник Полицейской Дубинкой.'
    desc3 = 'Игрок бьет Противник Полицейской Дубинкой.'
    desc4 = 'Игрок бьет Противник Полицейской Дубинкой, но не попадает.'
    desc5 = 'Игрок бьет Противник Полицейской Дубинкой, но не попадает.'
    desc6 = 'Игрок бьет Противник Полицейской Дубинкой, но не попадает.'


class Sniper(Weapon):
    def hit(self,user):
        if user.aimtarget is not None:
            if user.target.chat_id != int(user.aimtarget):
                print('сброс')
                user.bonusaccuracy = 0
        n = 0
        d = 0
        dmax = self.dice
        print(user.name + " стреляет из " + str(self.name) + '. Его энергия - ' + str(
            user.energy) + '. Его точность и бонусная точность оружия - ' + ' '
              + str(user.accuracy) + ' ' + str(user.bonusaccuracy) + ' ' + str(self.bonus) +
              '. Шанс попасть - ' + str(11 - user.energy - self.bonus - user.accuracy - user.bonusaccuracy - user.tempaccuracy) + "+!")
        while d != dmax:
            x = random.randint(1, 10)
            print(user.name + ' Выпало ' + str(x))
            if x > 10 - user.energy - self.bonus - user.accuracy - user.bonusaccuracy - user.tempaccuracy + user.target.evasion:
                n += 1
            d += 1
        user.bonusaccuracy = 0
        user.aimtarget = None

        # бонусный урон персонажа
        if n != 0:
            n += user.bonusdamage + self.damage - 1
        # уходит энергия
        if self.Melee:
            user.energy -= random.randint(1, 2)
        else:
            user.energy -= self.energy
        # энергия загоняется в 0
        if self.fixed > 0 and n > 0:
            n = self.fixed
        if user.energy < 0: user.energy = 0
        utils.damage(user, user.target, n, 'firearm')
        return n

    def aquare(self,user):
        user.aimtarget = None
        user.bonusaccuracy = 0

    def lose(self,user):
        del user.aimtarget
        del user.bonusaccuracy

    def get_action(self, p, call):
        keyboard1 = types.InlineKeyboardMarkup()
        enemyteam = p.targets
        p.turn = call.data
        for c in enemyteam:
            if p.energy + self.bonus + p.accuracy + p.bonusaccuracy >= 10:
                keyboard1.add(types.InlineKeyboardButton(text=c.name, callback_data=str('op' + str(c.chat_id))))
            else:
                keyboard1.add(types.InlineKeyboardButton(text=c.name, callback_data=str('op' + str(c.chat_id))),
                              types.InlineKeyboardButton(text="Выцелить", callback_data=str('aim' + str(c.chat_id))))

        keyboard1.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('opcancel')))
        bot.send_message(p.chat_id, 'Выберите противника.', reply_markup=keyboard1)

    def special(self, user, call):
        if user.aimtarget != call.data[3:]:
            user.aimtarget = call.data[3:]
            user.bonusaccuracy = 5
        else:
            user.bonusaccuracy +=5
        if user.energy + self.bonus + user.accuracy + user.bonusaccuracy >= 10:
            bot.send_message(user.chat_id, 'Точность максимальна!')
        user.fight.string.add(u'\U0001F3AF' + "|" + user.name + ' целится.')
        print('scheck')


    desc1 = 'Игрок стреляет в Противник из Снайперской винтовки.'
    desc2 = 'Игрок стреляет в Противник из Снайперской винтовки.'
    desc3 = 'Игрок стреляет в Противник из Снайперской винтовки.'
    desc4 = 'Игрок стреляет в Противник из Снайперской винтовки, но не попадает.'
    desc5 = 'Игрок стреляет в Противник из Снайперской винтовки, но не попадает.'
    desc6 = 'Игрок стреляет в Противник из Снайперской винтовки, но не попадает.'


class Spear(Weapon):
    def hit(self,user):
        n = 0
        d = 0
        dmax = self.dice
        print(user.name + " стреляет из " + str(self.name) + '. Его энергия - ' + str(
            user.energy) + '. Его точность и бонусная точность оружия - ' + ' '
              + str(user.accuracy) + ' ' + str(self.bonus) +
              '. Шанс попасть - ' + str(11 - user.energy - self.bonus - user.accuracy - user.tempaccuracy) + "+!")
        while d != dmax:
            x = random.randint(1, 10)
            print(user.name + ' Выпало ' + str(x))
            if x > 10 - user.energy - self.bonus - user.accuracy - user.tempaccuracy + user.target.evasion:
                n += 1
            d += 1
        for a in user.abilities:
            n = a.onhit(a,n, user)

        # бонусный урон персонажа
        if n != 0:
            n += user.bonusdamage + self.damage - 1
        # уходит энергия
        user.energy -= self.energy
        # энергия загоняется в 0
        utils.damage(user, user.target, n, 'melee')
        return n

    def aquare(self,user):
        user.Counter = False
        user.countercd = 0
        user.counterhit = 2

    def lose(self,user):
        del user.Counter
        del user.countercd
        del user.counterhit

    def get_action(self, user, call):
        keyboard1 = types.InlineKeyboardMarkup()
        targets = user.targets
        user.turn = call.data
        for c in targets:
            keyboard1.add(types.InlineKeyboardButton(text=c.name, callback_data=str('op' + str(c.chat_id))))
        if user.countercd == 0 and user.energy > 1:
            keyboard1.add(types.InlineKeyboardButton(text="Контратака", callback_data=str('aim')))
        keyboard1.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('opcancel')))
        bot.send_message(user.chat_id, 'Выберите противника.', reply_markup=keyboard1)

    def special(self, user, call):
        user.Counter = True
        user.countercd = 2
        user.fight.string.add(u'\U00002694' + "|" + user.name + ' готовится контратаковать.')

    def special_second(self, user):
        if user.Counter:
            for player in user.targets:
                if player.turn == 'attack' + str(user.fight.round) and user.counterhit > 0 or player.turn == 'weaponspecial' and user.counterhit > 0:
                    user.target = player
                    user.action = str(user.attack())
                    if user.target == user:
                        user.action = user.action.replace('Противник', 'себя').\
                            replace('Игрок', user.name).replace('Цель', user.target.name).\
                            replace(u'\U0001F44A',u'\U00002694')
                    else:
                        user.action = user.action.replace('Противник', user.target.name). \
                            replace('Игрок', user.name).replace('Цель', user.target.name). \
                            replace(u'\U0001F44A', u'\U00002694')
                    user.fight.string.add(user.action)
                    user.energy += 3
                    user.counterhit -= 1
                    user.target = None
            user.counterhit = 2
            user.Counter = False
            user.energy -= 2

    def special_end(self, user):
        if user.countercd > 0:
            user.countercd -= 1
    desc1 = 'Игрок бьет Противник Копьем.'
    desc2 = 'Игрок бьет Противник Копьем.'
    desc3 = 'Игрок бьет Противник Копьем.'
    desc4 = 'Игрок бьет Противник Копьем, но не попадает.'
    desc5 = 'Игрок бьет Противник Копьем, но не попадает.'
    desc6 = 'Игрок бьет Противник Копьем, но не попадает.'


class SpearEternal(Weapon):
    def hit(self,user):
        n = 0
        d = 0
        dmax = self.dice
        print(user.name + " стреляет из " + str(self.name) + '. Его энергия - ' + str(
            user.energy) + '. Его точность и бонусная точность оружия - ' + ' '
              + str(user.accuracy) + ' ' + str(self.bonus) +
              '. Шанс попасть - ' + str(11 - user.energy - self.bonus - user.accuracy - user.tempaccuracy) + "+!")
        while d != dmax:
            x = random.randint(1, 10)
            print(user.name + ' Выпало ' + str(x))
            if x > 10 - user.energy - self.bonus - user.accuracy - user.tempaccuracy + user.target.evasion:
                n += 1
            d += 1
        for a in user.abilities:
            n = a.onhit(a,n, user)

        # бонусный урон персонажа
        if n != 0:
            n += user.bonusdamage + self.damage - 1
        # уходит энергия
        user.energy -= self.energy
        # энергия загоняется в 0
        utils.damage(user, user.target, n, 'melee')
        return n

    def aquare(self,user):
        user.countercd = 0
        user.counterhit = 2
        if user.fight.round > 1:
            user.throwcd = 3
        else:
            user.itemlist.append(Item_list.throwspear)
            user.throwcd = 0


    def lose(self, user):
        del user.countercd
        del user.counterhit

    def get_action(self, user, call):
        keyboard1 = types.InlineKeyboardMarkup()
        targets = user.targets
        user.turn = call.data
        for c in targets:
            keyboard1.add(types.InlineKeyboardButton(text=c.name, callback_data=str('op' + str(c.chat_id))))
        if user.countercd == 0 and user.energy > 1:
            keyboard1.add(types.InlineKeyboardButton(text="Контратака", callback_data=str('aim')))
        keyboard1.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('opcancel')))
        bot.send_message(user.chat_id, 'Выберите противника.', reply_markup=keyboard1)

    def special(self, user, call):

        user.fight.string.add(u'\U00002694' + "|" + user.name + ' готовится контратаковать.')

    def special_second(self, user):
        if user.turn == 'aim':
            user.bonusdamage += 1
            for player in user.targets:
                if player.turn == 'attack' + str(user.fight.round) and user.counterhit > 0 or player.turn == 'weaponspecial' and user.counterhit > 0:
                    user.target = player
                    user.action = str(user.attack())
                    if user.target == user:
                        user.action = user.action.replace('Противник', 'себя').\
                            replace('Игрок', user.name).replace('Цель', user.target.name).\
                            replace(u'\U0001F44A',u'\U00002694')
                    else:
                        user.action = user.action.replace('Противник', user.target.name). \
                            replace('Игрок', user.name).replace('Цель', user.target.name). \
                            replace(u'\U0001F44A', u'\U00002694')
                    user.fight.string.add(user.action)
                    user.energy += 3
                    user.counterhit -= 1
                    user.target = None
            user.energy -= 3
            user.counterhit = 2
            user.countercd = 3

    def special_end(self, user):
        if user.countercd > 0:
            user.countercd -= 1
        if user.throwcd > 0:
            user.throwcd -= 1
        elif user.throwcd == 0 and Item_list.throwspear not in user.itemlist and user.weapon == self:
            user.itemlist.append(Item_list.throwspear)
    desc1 = 'Игрок бьет Противник Копьем Нарсил.'
    desc2 = 'Игрок бьет Противник Копьем Нарсил.'
    desc3 = 'Игрок бьет Противник Копьем Нарсил.'
    desc4 = 'Игрок бьет Противник Копьем Нарсил, но не попадает.'
    desc5 = 'Игрок бьет Противник Копьем Нарсил, но не попадает.'
    desc6 = 'Игрок бьет Противник Копьем Нарсил, но не попадает.'


class Flamethrower(Weapon):
    def hit(self,user):
        n = 0
        d = 0
        dmax = self.dice
        print(user.name + " стреляет из " + str(self.name) + '. Его энергия - ' + str(
            user.energy) + '. Его точность и бонусная точность оружия - ' + ' '
              + str(user.accuracy) + ' ' + str(self.bonus) +
              '. Шанс попасть - ' + str(11 - user.energy - self.bonus - user.accuracy - user.tempaccuracy) + "+!")
        while d != dmax:
            x = random.randint(1, 10)
            print(user.name + ' Выпало ' + str(x))
            if x > 10 - user.energy - self.bonus - user.accuracy - user.tempaccuracy + user.target.evasion:
                n += 1
            d += 1
        if n != 0:
            user.target.firecounter += 1
            user.target.offfire = user.fight.round + 2
            n += user.bonusdamage + self.damage - 1
        else:
            pass
        n += user.truedamage
        # энергия загоняется в 0
        if self.Melee:
            user.energy -= random.randint(1, 2)
        else:
            user.energy -= self.energy
        if user.energy < 0 :
            user.energy = 0
        if self.fixed > 0 and n > 0:
            n = self.fixed
        utils.damage(user, user.target, n, 'fire')
        return n

    def getDesc(self, damagetaken,user):
        if damagetaken != 0:
            d = str(u'\U0001F4A5' + "|"
                           + getattr(self,str('desc' + str(random.randint(1, 3)))) + " Нанесено "
                                              + str(damagetaken) + ' урона.')
            if user.target.firecounter == 1:
                d += u'\U0001F525' + "|" + user.target.name + ' загорелся!'
            return d
        else:
            return str(u'\U0001F4A8' + "|" + getattr(self, str('desc' + str(random.randint(4, 6)))))


    desc1 = 'Игрок стреляет в Противник из Огнемета!'
    desc2 = 'Игрок стреляет в Противник из Огнемета!'
    desc3 = 'Игрок стреляет в Противник из Огнемета!'
    desc4 = 'Игрок стреляет в Противник из Огнемета, но не попадает.'
    desc5 = 'Игрок стреляет в Противник из Огнемета, но не попадает.'
    desc6 = 'Игрок стреляет в Противник из Огнемета, но не попадает.'


class Bleeding(Weapon):
    def __init__(self, dice, damage, energy, bonus, fixed, Melee, TwoHanded, Concealable, name, damagestring, chance,
                 standart=True,natural=False):
        Weapon.__init__(self, dice, damage, energy, bonus, fixed, Melee, TwoHanded, Concealable, name, damagestring,standart=standart,natural=natural)
        self.chance = chance

    def hit(self,user):
        n = 0
        d = 0
        dmax = self.dice
        print(user.name + " стреляет из " + str(self.name) + '. Его энергия - ' + str(
            user.energy) + '. Его точность и бонусная точность оружия - ' + ' '
              + str(user.accuracy) + ' ' + str(self.bonus) +
              '. Шанс попасть - ' + str(11 - user.energy - self.bonus - user.accuracy - user.tempaccuracy) + "+!")
        while d != dmax:
            x = random.randint(1, 10)
            print(user.name + ' Выпало ' + str(x))
            if x > 10 - user.energy - self.bonus - user.accuracy - user.tempaccuracy + user.target.evasion:
                n += 1
            d += 1
        if n != 0 and random.randint(1,10)< self.chance:
            user.target.bleedcounter += 1
            user.target.bloodloss = False
            user.Hitability = True

            # бонусный урон персонажа
        # уходит энергия
        user.energy -= self.energy
        if n!=0:
            n += user.bonusdamage + self.damage - 1

        for a in user.abilities:
            n = a.onhit(a, n, user)
        else:
            pass
        n += user.truedamage
        # энергия загоняется в 0

        if user.energy < 0: user.energy = 0
        utils.damage(user, user.target, n, 'melee')
        print('bleed')
        return n

    def getDesc(self, damagetaken,user):
        if damagetaken != 0:
            if not self.Melee:
                d =  str(u'\U0001F4A5' + "|" + getattr(self,str('desc' + str(random.randint(1, 3)))) + " Нанесено " + str(damagetaken) + ' урона.')
            else:
                d =  str(u'\U0001F44A' + "|" + getattr(self,str('desc' + str(random.randint(1, 3)))) + " Нанесено " + str(damagetaken) + ' урона.')
            if user.target.bleedcounter == 1 and user.Hitability:
                d += u'\U00002763' + "|" + user.target.name + ' истекает кровью!'
            elif user.target.bleedcounter > 1 and user.Hitability:
                d += u'\U00002763' + "|" 'Кровотечение усиливается!'
            for a in user.abilities:
                d = a.onhitdesc(a,d,user)
            return d
        else:
            return str(u'\U0001F4A8' + "|" + getattr(self,str('desc' + str(random.randint(4, 6)))))


class Burning(Weapon):
    def __init__(self, dice, damage, energy, bonus, fixed, Melee, TwoHanded, Concealable, name, damagestring, chance,
                 standart=True,natural=False):
        Weapon.__init__(self, dice, damage, energy, bonus, fixed, Melee, TwoHanded, Concealable, name, damagestring,standart=standart,natural=natural)
        self.chance = chance

    def hit(self,user):
        n = 0
        d = 0
        dmax = self.dice
        print(user.name + " стреляет из " + str(self.name) + '. Его энергия - ' + str(
            user.energy) + '. Его точность и бонусная точность оружия - ' + ' '
              + str(user.accuracy) + ' ' + str(self.bonus) +
              '. Шанс попасть - ' + str(11 - user.energy - self.bonus - user.accuracy - user.tempaccuracy) + "+!")
        while d != dmax:
            x = random.randint(1, 10)
            print(user.name + ' Выпало ' + str(x))
            if x > 10 - user.energy - self.bonus - user.accuracy - user.tempaccuracy + user.target.evasion:
                n += 1
            d += 1
        if n != 0 and random.randint(1,10)< self.chance:
            user.target.firecounter += 1
            user.target.offfire = user.fight.round + 2
            user.Hitability = True

            # бонусный урон персонажа
        # уходит энергия
        user.energy -= self.energy
        if n!=0:
            n += user.bonusdamage + self.damage - 1

        for a in user.abilities:
            n = a.onhit(a, n, user)
        else:
            pass
        n += user.truedamage
        # энергия загоняется в 0

        if user.energy < 0: user.energy = 0
        utils.damage(user, user.target, n, 'melee')
        print('bleed')
        return n

    def getDesc(self, damagetaken,user):
        if damagetaken != 0:
            if not self.Melee:
                d = str(u'\U0001F4A5' + "|" + getattr(self,str('desc' + str(random.randint(1, 3)))) + " Нанесено " + str(damagetaken) + ' урона.')
            else:
                d = str(u'\U0001F44A' + "|" + getattr(self,str('desc' + str(random.randint(1, 3)))) + " Нанесено " + str(damagetaken) + ' урона.')
            if user.target.firecounter == 1 and user.Hitability:
                d += u'\U0001F525' + "|" + user.target.name + ' загорелся!'
            elif user.target.firecounter > 1 and user.Hitability:
                d += u'\U0001F525' + "|" 'Огонь усиливается!'
            for a in user.abilities:
                d = a.onhitdesc(a,d,user)
            return d
        else:
            return str(u'\U0001F4A8' + "|" + getattr(self,str('desc' + str(random.randint(4, 6)))))


class Stunning(Weapon):
    def __init__(self, dice, damage, energy, bonus, fixed, Melee, TwoHanded, Concealable, name, damagestring, chance,
                 standart=True,natural=False):
        Weapon.__init__(self, dice, damage, energy, bonus, fixed, Melee, TwoHanded, Concealable, name, damagestring,
                        standart=standart,natural=natural)
        self.chance = chance

    def hit(self,user):
        n = 0
        d = 0
        dmax = self.dice
        print(user.name + " стреляет из " + str(self.name) + '. Его энергия - ' + str(
            user.energy) + '. Его точность и бонусная точность оружия - ' + ' '
              + str(user.accuracy) + ' ' + str(self.bonus) +
              '. Шанс попасть - ' + str(11 - user.energy - self.bonus - user.accuracy - user.tempaccuracy) + "+!")
        while d != dmax:
            x = random.randint(1, 10)
            print(user.name + ' Выпало ' + str(x))
            if x > 10 - user.energy - self.bonus - user.accuracy - user.tempaccuracy + user.target.evasion:
                n += 1
            d += 1


            # бонусный урон персонажа
        # уходит энергия
        user.energy -= self.energy
        if n!=0:
            n += user.bonusdamage + self.damage - 1
            for a in user.abilities:
                n = a.onhit(a,n, user)
        else:
            pass
        n += user.truedamage
        # применяется урон
        # энергия загоняется в 0

        if user.energy < 0: user.energy = 0

        utils.damage(user, user.target, n, 'melee')
        return n

    def effect(self, user):
        if random.randint(1,10)< self.chance:
            if user.target.stuncounter < 1:
                user.target.stuncounter = 1
            user.fight.string.add(u'\U0001F300' + '|' + user.target.name + ' оглушен!')
        user.weaponeffect.remove(self)

    def getDesc(self, damagetaken,user):
        if damagetaken != 0:
            user.weaponeffect.append(self)
            if not self.Melee:
                d = str(u'\U0001F4A5' + "|" + getattr(self,str('desc' + str(random.randint(1, 3)))) + " Нанесено " + str(damagetaken) + ' урона.')
            else:
                d = str(u'\U0001F44A' + "|" + getattr(self,str('desc' + str(random.randint(1, 3)))) + " Нанесено " + str(damagetaken) + ' урона.')
            for a in user.abilities:
                d = a.onhitdesc(a, d, user)
            return d
        else:
            return str(u'\U0001F4A8' + "|" + getattr(self,str('desc' + str(random.randint(4, 6)))))


class Crippling(Weapon):
    def __init__(self, dice, damage, energy, bonus, fixed, Melee, TwoHanded, Concealable, name, damagestring, chance,
                 standart=True,natural=False):
        Weapon.__init__(self, dice, damage, energy, bonus, fixed, Melee, TwoHanded, Concealable, name, damagestring,
                        standart=standart,natural=natural)
        self.chance = chance

    def hit(self, user):
        n = 0
        d = 0
        dmax = self.dice
        print(user.name + " стреляет из " + str(self.name) + '. Его энергия - ' + str(
            user.energy) + '. Его точность и бонусная точность оружия - ' + ' '
              + str(user.accuracy) + ' ' + str(self.bonus) +
              '. Шанс попасть - ' + str(11 - user.energy - self.bonus - user.accuracy - user.tempaccuracy) + "+!")
        while d != dmax:
            x = random.randint(1, 10)
            print(user.name + ' Выпало ' + str(x))
            if x > 10 - user.energy - self.bonus - user.accuracy - user.tempaccuracy + user.target.evasion:
                n += 1
            d += 1


            # бонусный урон персонажа
        # уходит энергия
        user.energy -= self.energy
        if n!=0:
            n += user.bonusdamage + self.damage - 1

        for a in user.abilities:
            n = a.onhit(a,n, user)
        else:
            pass
        n += user.truedamage
        # применяется урон
        # энергия загоняется в 0
        if user.energy < 0: user.energy = 0

        utils.damage(user, user.target, n, 'melee')
        return n

    def effect(self, user):
        if random.randint(1, 10) <= self.chance:
            if user.target.toughness > 2:
                user.target.toughness -= 1
            if user.target.toughness > 2:
                user.fight.string.add(u'\U0001F915' + '|' + user.target.name + ' покалечен!')
            else:
                user.fight.string.add(u'\U0001F915' + '|' + user.target.name + ' покалечен! Эффект максимален.')
        user.weaponeffect.remove(self)

    def getDesc(self, damagetaken,user):
        if damagetaken != 0:
            user.weaponeffect.append(self)
            if not self.Melee:
                d = str(u'\U0001F4A5' + "|" + getattr(self,str('desc' + str(random.randint(1, 3)))) + " Нанесено " + str(damagetaken) + ' урона.')
            else:
                d = str(u'\U0001F44A' + "|" + getattr(self,str('desc' + str(random.randint(1, 3)))) + " Нанесено " + str(damagetaken) + ' урона.')
            for a in user.abilities:
                d = a.onhitdesc(a, d, user)
            return d
        else:
            return str(u'\U0001F4A8' + "|" + getattr(self,str('desc' + str(random.randint(4, 6)))))


class Dropping(Weapon):
    def __init__(self, dice, damage, energy, bonus, fixed, Melee, TwoHanded, Concealable, name, damagestring, chance,
                 standart=True,natural=False):
        Weapon.__init__(self, dice, damage, energy, bonus, fixed, Melee, TwoHanded, Concealable, name, damagestring,
                        standart=standart,natural=natural)
        self.chance = chance

    def aquare(self, user):
        user.dropcd = 0

    def lose(self, user):
        del user.dropcd

    def get_action(self, p, call):
        keyboard1 = types.InlineKeyboardMarkup()
        enemyteam = p.targets
        p.turn = call.data
        for c in enemyteam:
            if p.dropcd != 0 or c.weapon.natural:
                keyboard1.add(types.InlineKeyboardButton(text=c.name, callback_data=str('op' + str(c.chat_id))))
            else:
                keyboard1.add(types.InlineKeyboardButton(text=c.name, callback_data=str('op' + str(c.chat_id))),
                              types.InlineKeyboardButton(text="Выбить оружие", callback_data=str('weaponspecial'
                                                                                                 + str(c.chat_id))))

        keyboard1.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('opcancel')))
        bot.send_message(p.chat_id, 'Выберите противника.', reply_markup=keyboard1)

    def hit(self,user):
        n = 0
        d = 0
        dmax = self.dice
        print(user.name + " стреляет из " + str(self.name) + '. Его энергия - ' + str(
            user.energy) + '. Его точность и бонусная точность оружия - ' + ' '
              + str(user.accuracy) + ' ' + str(self.bonus) +
              '. Шанс попасть - ' + str(11 - user.energy - self.bonus - user.accuracy - user.tempaccuracy) + "+!")
        while d != dmax:
            x = random.randint(1, 10)
            print(user.name + ' Выпало ' + str(x))
            if x > 10 - user.energy - self.bonus - user.accuracy - user.tempaccuracy:
                n += 1
            d += 1


            # бонусный урон персонажа
        # уходит энергия
        user.energy -= self.energy
        if n!=0:
            n += user.bonusdamage + self.damage - 1

        for a in user.abilities:
            n = a.onhit(a,n, user)
        else:
            pass
        n += user.truedamage
        if user.energy < 0: user.energy = 0
        utils.damage(user, user.target, n, 'melee')
        return n

    def effect(self, user):
        if user.target.turn == 'attack' + str(user.fight.round) and random.randint(1, 10) or \
                user.target.turn == 'weaponspecial' and random.randint(1, 10) <= self.chance:
            if not user.target.weapon.natural:
                user.target.lostweapon = user.target.weapon
                user.fight.string.add(u'\U0001F450' + '|' + user.target.name + ' теряет свое оружие!')
        elif user.target.turn == 'reload' + str(user.fight.round):
            if not user.target.weapon.natural:
                user.target.lostweapon = user.target.weapon
                user.fight.string.add(u'\U0001F450' + '|' + user.target.name + ' теряет свое оружие!')
        user.weaponeffect.remove(self)

    def getDesc(self, damagetaken, user):
        if damagetaken != 0:
            if not self.Melee:
                d = str(u'\U0001F4A5' + "|" + getattr(self,str('desc' + str(random.randint(1, 3)))) + " Нанесено " + str(damagetaken) + ' урона.')
            else:
                d = str(u'\U0001F44A' + "|" + getattr(self,str('desc' + str(random.randint(1, 3)))) + " Нанесено " + str(damagetaken) + ' урона.')
            for a in user.abilities:
                d = a.onhitdesc(a, d, user)
            return d
        else:
            return str(u'\U0001F4A8' + "|" + getattr(self,str('desc' + str(random.randint(4, 6)))))

    def special(self, user, call):
        user.target = utils.actor_from_id(call, user.game)
        user.dropcd = 4

    def special_second(self, user):
        if user.dropcd > 0:
            user.dropcd -= 1
        if user.turn == 'weaponspecial':
            damagetaken = self.hit(user)
            user.energy -= 1
            if damagetaken != 0:
                user.weaponeffect.append(self)
                d = str(
                    u'\U000026D3' + "|" + user.name + ' пытается выбить оружие из рук '
                    + user.target.name + "! Нанесено " + str(damagetaken) + ' урона.')
            else:
                d = str(
                    u'\U0001F4A8' + "|" + user.name + ' пытается выбить оружие из рук ' + user.target.name + "!")
            for a in user.abilities:
                d = a.onhitdesc(a, d, user)
            user.fight.string.add(d)


class Crushing(Weapon):

    def aquare(self, user):
        user.crushcd = 0

    def lose(self, user):
        del user.crushcd

    def get_action(self, p, call):
        keyboard1 = types.InlineKeyboardMarkup()
        enemyteam = p.targets
        p.turn = call.data
        for c in enemyteam:
            if p.crushcd != 0 or p.energy < 4:
                keyboard1.add(types.InlineKeyboardButton(text=c.name, callback_data=str('op' + str(c.chat_id))))
            else:
                keyboard1.add(types.InlineKeyboardButton(text=c.name, callback_data=str('op' + str(c.chat_id))),
                              types.InlineKeyboardButton(text="Сокрушить", callback_data=str('weaponspecial'
                                                                                                 + str(c.chat_id))))

        keyboard1.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('opcancel')))
        bot.send_message(p.chat_id, 'Выберите противника.', reply_markup=keyboard1)

    def special(self, user, call):
        user.target = utils.actor_from_id(call, user.game)

    def hit_sp(self, user):
        n = 0
        d = 0
        dmax = self.dice
        print(user.name + " стреляет из " + str(self.name) + '. Его энергия - ' + str(
            user.energy) + '. Его точность и бонусная точность оружия - ' + ' '
              + str(user.accuracy) + ' ' + str(self.bonus) +
              '. Шанс попасть - ' + str(11 - user.energy - self.bonus - user.accuracy - user.tempaccuracy) + "+!")
        while d != dmax:
            x = random.randint(1, 10)
            print(user.name + ' Выпало ' + str(x))
            if x > 10 - user.energy - self.bonus - user.accuracy - user.tempaccuracy + user.target.evasion:
                n += 1
            d += 1
        # бонусный урон персонажа
        # уходит энергия
        user.energy -= self.energy
        if n != 0:
            n += user.bonusdamage + self.damage + user.crushdamage

        for a in user.abilities:
            n = a.onhit(a, n, user)
        else:
            pass
        n += user.truedamage
        # энергия загоняется в 0

        if user.energy < 0: user.energy = 0

        print('bleed')
        utils.damage(user, user.target, n, 'melee')
        return n

    def special_second(self, user):
        if user.crushcd > 0:
            user.crushcd -= 1
        if user.turn == 'weaponspecial':
            user.crushdamage = user.target.maxenergy - user.target.energy - 1
            user.tempaccuracy -= 1
            damagetaken = self.hit_sp(user)
            if damagetaken != 0:
                d = str(
                    u'\U0001F528' + "|" + user.name + ' наносит сокрушительный удар по ' + user.target.name
                    + "! Нанесено " + str(damagetaken) + ' урона.')
            else:
                d = str(
                    u'\U0001F4A8' + "|" + user.name
                    + ' пытается нанести сокрушительный удар Кувалдой, но не попадает по ' + user.target.name + "!")
            for a in user.abilities:
                d = a.onhitdesc(a, d, user)
            user.fight.string.add(d)
            user.energy -= 2
            user.crushcd = 3
            del user.crushdamage


class MasterFist(Weapon):

    def get_action(self, p, call):
        keyboard1 = types.InlineKeyboardMarkup()
        enemyteam = p.targets
        p.turn = call.data
        for c in enemyteam:
            if p.energy < 3:
                keyboard1.add(types.InlineKeyboardButton(text=c.name, callback_data=str('op' + str(c.chat_id))))
            else:
                keyboard1.add(types.InlineKeyboardButton(text=c.name, callback_data=str('op' + str(c.chat_id))),
                              types.InlineKeyboardButton(text="Серия ударов", callback_data=str('weaponspecial'
                                                                                                 + str(c.chat_id))))

        keyboard1.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('opcancel')))
        bot.send_message(p.chat_id, 'Выберите противника.', reply_markup=keyboard1)

    def hit(self,user):
        n = 0
        d = 0
        dmax = self.dice
        print(user.name + " стреляет из " + str(self.name) + '. Его энергия - ' + str(
            user.energy) + '. Его точность и бонусная точность оружия - ' + ' '
              + str(user.accuracy) + ' ' + str(self.bonus) +
              '. Шанс попасть - ' + str(11 - user.energy - self.bonus - user.accuracy - user.tempaccuracy) + "+!")
        while d != dmax:
            x = random.randint(1, 10)
            print(user.name + ' Выпало ' + str(x))
            if x > 10 - user.energy - self.bonus - user.accuracy - user.tempaccuracy + user.target.evasion:
                n += 1
            d += 1


            # бонусный урон персонажа
        # уходит энергия
        user.energy -= self.energy
        if n!=0:
            n += user.bonusdamage + self.damage - 1

        for a in user.abilities:
            n = a.onhit(a,n, user)
        else:
            pass
        n += user.truedamage
        # энергия загоняется в 0
        if user.energy < 0: user.energy = 0
        utils.damage(user, user.target, n, 'melee')
        return n

    def special(self, user, call):
        user.target = utils.actor_from_id(call, user.game)

    def special_second(self, user):
        if user.turn == 'weaponspecial':
            damagetaken = 0
            combo = 0
            while user.energy > 0 and combo < 3:
                damagetaken += self.hit(user)
                combo += 1
            if damagetaken != 0:
                d = str(
                    u'\U0001F91C' + "|" + user.name + ' проводит серию из ' + str(combo) + ' ударов на '
                    + user.target.name + "! Нанесено " + str(damagetaken) + ' урона.')
            else:
                d = str(
                    u'\U0001F4A8' + "|" + user.name + ' не удается нанести ни одного удара ' + user.target.name + "!")
            for a in user.abilities:
                d = a.onhitdesc(a, d, user)
            user.fight.string.add(d)


class Katana(Weapon):
    def __init__(self, dice, damage, energy, bonus, fixed, Melee, TwoHanded, Concealable, name, damagestring, chance,
                 standart=True, natural=False):
        Weapon.__init__(self, dice, damage, energy, bonus, fixed, Melee, TwoHanded, Concealable, name, damagestring,
                        standart=standart, natural=natural)
        self.chance = chance

    def hit(self,user):
        n = 0
        d = 0
        dmax = self.dice
        print(user.name + " стреляет из " + str(self.name) + '. Его энергия - ' + str(
            user.energy) + '. Его точность и бонусная точность оружия - ' + ' '
              + str(user.accuracy) + ' ' + str(self.bonus) +
              '. Шанс попасть - ' + str(11 - user.energy - self.bonus - user.accuracy - user.tempaccuracy) + "+!")
        while d != dmax:
            x = random.randint(1, 10)
            print(user.name + ' Выпало ' + str(x))
            if x > 10 - user.energy - self.bonus - user.accuracy - user.tempaccuracy + user.target.evasion:
                n += 1
            d += 1
        if n != 0 and random.randint(1,10)< self.chance:
            user.target.bleedcounter += 1
            user.target.bloodloss = False
            user.Hitability = True

            # бонусный урон персонажа
        # уходит энергия
        user.energy -= self.energy
        if n!=0:
            n += user.bonusdamage + self.damage - 1

        for a in user.abilities:
            n = a.onhit(a, n, user)
        else:
            pass
        n += user.truedamage
        # энергия загоняется в 0

        if user.energy < 0: user.energy = 0

        print('bleed')
        utils.damage(user, user.target, n, 'melee')
        return n

    def get_action(self, p, call):
        keyboard1 = types.InlineKeyboardMarkup()
        enemyteam = p.targets
        p.turn = call.data
        for c in enemyteam:
            if c.hp > 1 or p.energy < 3:
                keyboard1.add(types.InlineKeyboardButton(text=c.name, callback_data=str('op' + str(c.chat_id))))
            else:
                keyboard1.add(types.InlineKeyboardButton(text=c.name, callback_data=str('op' + str(c.chat_id))),
                              types.InlineKeyboardButton(text="Казнь", callback_data=str('weaponspecial' + str(c.chat_id))))

        keyboard1.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('opcancel')))
        bot.send_message(p.chat_id, 'Выберите противника.', reply_markup=keyboard1)

    def special(self, user, call):
        user.target = utils.actor_from_id(call, user.game)

    def special_second(self, user):
        if user.turn == 'weaponspecial':
            if user.target.hp == 1:
                user.tempaccuracy += 3
                damagetaken = self.hit(user)
                if damagetaken != 0:
                    user.target.hp = 0
                    d = str(
                        u'\U00003299' + u'\U0001F494' + "|" + user.name + ' наносит стремительный удар по ' + user.target.name
                        + " оставляя страшную рану! Нанесено " + str(damagetaken) + ' урона. ' + user.target.name +
                        ' теряет жизнь!')
                else:
                    d = str(
                        u'\U0001F4A8' + "|" + user.name
                        + ' стремительно взмахивает Катаной, но не попадает по ' + user.target.name + "!")
                for a in user.abilities:
                    d = a.onhitdesc(a, d, user)
                user.fight.string.add(d)
                user.energy -= 3

    def getDesc(self, damagetaken, user):
        if damagetaken != 0:
            if not self.Melee:
                d = str(
                    u'\U0001F4A5' + "|" + getattr(self, str('desc' + str(random.randint(1, 3)))) + " Нанесено " + str(
                        damagetaken) + ' урона.')
            else:
                d = str(
                    u'\U0001F44A' + "|" + getattr(self, str('desc' + str(random.randint(1, 3)))) + " Нанесено " + str(
                        damagetaken) + ' урона.')
            if user.target.bleedcounter == 1 and user.Hitability:
                d += u'\U00002763' + "|" + user.target.name + ' истекает кровью!'
            elif user.target.bleedcounter > 1 and user.Hitability:
                d += u'\U00002763' + "|" 'Кровотечение усиливается!'
            for a in user.abilities:
                d = a.onhitdesc(a, d, user)
            return d
        else:
            return str(u'\U0001F4A8' + "|" + getattr(self, str('desc' + str(random.randint(4, 6)))))


class Knuckles(Weapon):

    def special_end(self, user):
        if user.turn == 'attack' + str(user.fight.round):
            if user.target.turn == 'reload' + str(user.fight.round) or user.target.turn == \
                            'dog_rest' + str(user.fight.round):
                user.target.energy -= 2
                user.fight.string.add(u'\U000026A1' + user.target.name + ' теряет 2 Энергии.')


class Club(Weapon):

    def hit(self,user):
        n = 0
        d = 0
        dmax = self.dice
        while d != dmax:
            x = random.randint(1, 10)
            print(user.name + ' Выпало ' + str(x))
            if x > 10 - user.energy - self.bonus - user.accuracy - user.tempaccuracy + user.target.evasion:
                n += 1
            d += 1

        # уходит энергия
        user.energy -= self.energy
        if n!=0:
            n += user.bonusdamage + self.damage + user.combo_counter - 1

        for a in user.abilities:
            n = a.onhit(a, n, user)
        else:
            pass
        n += user.truedamage
        # энергия загоняется в 0
        if user.energy < 0: user.energy = 0
        utils.damage(user, user.target, n, 'melee')
        return n

    def aquare(self ,user):
        user.combo_counter = 0

    def lose(self, user):
        del user.combo_counter

    def special_end(self, user):
        if user.turn == 'attack' + str(user.fight.round):
            if user.combo_counter < 2:
                user.combo_counter += 1
        else:
            user.combo_counter = 0


class ULTRA(Weapon):
    def __init__(self, dice, damage, energy, bonus, fixed, Melee, TwoHanded, Concealable, name, damagestring, double,
                 standart=True):
        Weapon.__init__(self, dice, damage, energy, bonus, fixed, Melee, TwoHanded, Concealable, name, damagestring,standart=standart)
        self.double=double
            
    def aquare(self,user):
        user.longreload = 0
        user.DisabledReload = False
        
    def special_second(self, user):
        if user.turn == 'reload' + str(user.fight.round):
            user.DisabledReload = True
            user.Disabled = True
            user.longreload = user.fight.round + 1
        if user.fight.round == user.longreload:
            user.Disabled = False
            user.DisabledReload = False
            

class BowBleeding(Weapon):
    def __init__(self, dice, damage, energy, bonus, fixed, Melee, TwoHanded, Concealable, name, damagestring, chance,
                 standart=True,natural=False):
        Weapon.__init__(self, dice, damage, energy, bonus, fixed, Melee, TwoHanded, Concealable, name, damagestring,standart=standart,natural=natural)
        self.chance = chance

    def getDesc(self, damagetaken,user):
        user.weaponeffect.append(self)
        if damagetaken != 0:
            if not self.Melee:

                d =  str(u'\U0001F4A5' + "|" + getattr(self,str('desc' + str(random.randint(1, 3)))) + " Нанесено " + str(damagetaken) + ' урона.')
            else:
                d =  str(u'\U0001F44A' + "|" + getattr(self,str('desc' + str(random.randint(1, 3)))) + " Нанесено " + str(damagetaken) + ' урона.')
            if user.target.bleedcounter == 1 and user.Hitability:
                d += u'\U00002763' + "|" + user.target.name + ' истекает кровью!'
            elif user.target.bleedcounter > 1 and user.Hitability:
                d += u'\U00002763' + "|" 'Кровотечение усиливается!'
            return d
        else:
            return str(u'\U0001F4A8' + "|" + getattr(self,str('desc' + str(random.randint(4, 6)))))


    def hit(self,user):
        n = 0
        d = 0
        dmax = self.dice
        print(user.name + " стреляет из " + str(self.name) + '. Его энергия - ' + str(
            user.energy) + '. Его точность и бонусная точность оружия - ' + ' '
              + str(user.accuracy) + ' ' + str(user.bonusaccuracy) + ' ' + str(self.bonus) +
              '. Шанс попасть - ' + str(11 - user.energy - self.bonus - user.accuracy - user.bonusaccuracy - user.tempaccuracy) + "+!")
        while d != dmax:
            x = random.randint(1, 10)
            print(user.name + ' Выпало ' + str(x))
            if x > 10 - user.energy - self.bonus - user.accuracy - user.bonusaccuracy - user.tempaccuracy + user.target.evasion:
                n += 1
            d += 1

        # бонусный урон персонажа
        if n != 0:
            n += user.bonusdamage + self.damage - 1
            if user.bonusaccuracy > 0:
                n += user.bonusaccuracy*2
        if n != 0 and random.randint(1, 10) < self.chance + user.bonusaccuracy:
            user.target.bleedcounter += 1
            user.target.bloodloss = False
            user.Hitability = True
        # уходит энергия
        user.energy -= self.energy + user.bonusaccuracy
        # применяется урон
        user.target.damagetaken += n + user.truedamage
        # энергия загоняется в 0
        if user.energy < 0: user.energy = 0
        return n

    def aquare(self,user):
        user.bonusaccuracy = 0

    def lose(self,user):
        user.bonusaccuracy = 0
        user.Armed = False

    def get_action(self, p, call):
        keyboard1 = types.InlineKeyboardMarkup()
        p.turn = call.data
        for c in p.targets:
                keyboard1.add(types.InlineKeyboardButton(text=c.name, callback_data=str('op' + str(c.chat_id))))
        if p.energy - p.bonusaccuracy > 1 and p.bonusaccuracy < 3:
            keyboard1.add(types.InlineKeyboardButton(text="Натянуть", callback_data=str('draw')))
        keyboard1.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('opcancel')))
        bot.send_message(p.chat_id, 'Выберите противника.', reply_markup=keyboard1)

    def special(self, user, call):
        user.bonusaccuracy += 1
        user.Armed = True
        print ('scheck')

    def effect(self, user):
        x = random.randint(1, 10)
        if user.Hit:
            print('Оглушение ' + str(x) + ' < '+ str(user.bonusaccuracy-1)*6)
            if random.randint(1, 10) < (user.bonusaccuracy-1)*6:
                if user.target.stuncounter < 1:
                    user.target.stuncounter = 1
                user.fight.string.add(u'\U0001F300' + '|' + user.target.name + ' оглушен!')
        user.weaponeffect.remove(self)

        user.bonusaccuracy = 0
        user.Armed = False


katana = Katana(3, 1, 2, 2, 0, True, False, False, 'Катана','1-3' + u'\U0001F525' + "|" + '2' + u'\U000026A1', 3, standart=False)
katana.desc1 = 'Игрок бьет Противник Катаной!'
katana.desc2 = 'Игрок бьет Противник Катаной!'
katana.desc3 = 'Игрок бьет Противник Катаной!'
katana.desc4 = 'Игрок бьет Противник Катаной, но не попадает.'
katana.desc5 = 'Игрок бьет Противник Катаной, но не попадает.'
katana.desc6 = 'Игрок бьет Противник Катаной, но не попадает.'

knuckles = Knuckles(2, 1, 2, 3, 0, True, False, False, "Кастет",'1-2' + u'\U0001F525' + "|" + '2' + u'\U000026A1')
knuckles.desc1 = 'Игрок бьет Противник Кастетом!'
knuckles.desc2 = 'Игрок бьет Противник Кастетом!'
knuckles.desc3 = 'Игрок бьет Противник Кастетом!'
knuckles.desc4 = 'Игрок бьет Противник Кастетом, но не попадает.'
knuckles.desc5 = 'Игрок бьет Противник Кастетом, но не попадает.'
knuckles.desc6 = 'Игрок бьет Противник Кастетом, но не попадает.'

club = Club(3, 1, 2, 2, 0, True, False, False, "Булава",'1-3' + u'\U0001F525' + "|" + '2' + u'\U000026A1')
club.desc1 = 'Игрок бьет Противник Булавой!'
club.desc2 = 'Игрок бьет Противник Булавой!'
club.desc3 = 'Игрок бьет Противник Булавой!'
club.desc4 = 'Игрок бьет Противник Булавой, но не попадает.'
club.desc5 = 'Игрок бьет Противник Булавой, но не попадает.'
club.desc6 = 'Игрок бьет Противник Булавой, но не попадает.'

ultra=ULTRA(3,1,2,2,0,True,False,True,'анусосжигатеь','500' , True, standart=False)
ultra.desc1 = 'Игрок бьет Противник Ножом!'
ultra.desc2 = 'Игрок бьет Противник Ножом!'
ultra.desc3 = 'Игрок бьет Противник Ножом!'
ultra.desc4 = 'Игрок бьет Противник Ножом, но не попадает.'
ultra.desc5 = 'Игрок бьет Противник Ножом, но не попадает.'
ultra.desc6 = 'Игрок бьет Противник Ножом, но не попадает.'
tazer = Tazer(3, 1, 2, 2, 0, True, False, True, 'Полицейская Дубинка', '1-3' + u'\U0001F44A' + "|" + '2' + u'\U000026A1')
sniper = Sniper(1, 1, 5, -4, 8, False, False, False, 'Снайперская винтовка','8' + u'\U0001F4A5' + "|" + '5' + u'\U000026A1')
flamethrower = Flamethrower(2, 1, 3, 2, 1, False, False, False, 'Огнемет','1' + u'\U0001F525' + "|" + '3' + u'\U000026A1')
knife = Bleeding(3, 1, 2, 2, 0, True, False, False, 'Нож','1-3' + u'\U0001F525' + "|" + '2' + u'\U000026A1',6)
knife.desc1 = 'Игрок бьет Противник Ножом!'
knife.desc2 = 'Игрок бьет Противник Ножом!'
knife.desc3 = 'Игрок бьет Противник Ножом!'
knife.desc4 = 'Игрок бьет Противник Ножом, но не попадает.'
knife.desc5 = 'Игрок бьет Противник Ножом, но не попадает.'
knife.desc6 = 'Игрок бьет Противник Ножом, но не попадает.'
tourch = Burning(2, 1, 2, 3, 0, True, False, False, 'Факел','1-2' + u'\U0001F525' + "|" + '2' + u'\U000026A1', 8)
tourch.desc1 = 'Игрок бьет Противник Факелом!'
tourch.desc2 = 'Игрок бьет Противник Факелом!'
tourch.desc3 = 'Игрок бьет Противник Факелом!'
tourch.desc4 = 'Игрок бьет Противник Факелом, но не попадает.'
tourch.desc5 = 'Игрок бьет Противник Факелом, но не попадает.'
tourch.desc6 = 'Игрок бьет Противник Факелом, но не попадает.'
hatchet = Crippling(3, 1, 2, 2, 0, True, False, False, 'Топор','1-3' + u'\U0001F525' + "|" + '2' + u'\U000026A1', 8)
hatchet.desc1 = 'Игрок бьет Противник Топором!'
hatchet.desc2 = 'Игрок бьет Противник Топором!'
hatchet.desc3 = 'Игрок бьет Противник Топором!'
hatchet.desc4 = 'Игрок бьет Противник Топором, но не попадает.'
hatchet.desc5 = 'Игрок бьет Противник Топором, но не попадает.'
hatchet.desc6 = 'Игрок бьет Противник Топором, но не попадает.'
chain = Dropping(3, 1, 2, 2, 0, True, False, False, 'Цепь','1-3' + u'\U0001F525' + "|" + '2' + u'\U000026A1', 4)
chain.desc1 = 'Игрок бьет Противник Цепью!'
chain.desc2 = 'Игрок бьет Противник Цепью!'
chain.desc3 = 'Игрок бьет Противник Цепью!'
chain.desc4 = 'Игрок бьет Противник Цепью, но не попадает.'
chain.desc5 = 'Игрок бьет Противник Цепью, но не попадает.'
chain.desc6 = 'Игрок бьет Противник Цепью, но не попадает.'
sledge = Crushing(3, 1, 2, 2, 0, True, False, False, 'Кувалда','1-3' + u'\U0001F525' + "|" + '2' + u'\U000026A1', standart=False)
sledge.desc1 = 'Игрок бьет Противник Кувалдой!'
sledge.desc2 = 'Игрок бьет Противник Кувалдой!'
sledge.desc3 = 'Игрок бьет Противник Кувалдой!'
sledge.desc4 = 'Игрок бьет Противник Кувалдой, но не попадает.'
sledge.desc5 = 'Игрок бьет Противник Кувалдой, но не попадает.'
sledge.desc6 = 'Игрок бьет Противник Кувалдой, но не попадает.'
bow = BowBleeding(3, 1, 2, -1, 0, False, False, False, 'Лук Асгард','1-3!' + u'\U0001F525' + "|" + '2!' + u'\U000026A1', 3, standart=False)
bow.desc1 = 'Игрок стреляет в Противник из Лука Асгард.'
bow.desc2 = 'Игрок стреляет в Противник из Лука Асгард.'
bow.desc3 = 'Игрок стреляет в Противник из Лука Асгард.'
bow.desc4 = 'Игрок стреляет в Противник из Лука Асгард, но не попадает.'
bow.desc5 = 'Игрок стреляет в Противник из Лука Асгард, но не попадает.'
bow.desc6 = 'Игрок стреляет в Противник из Лука Асгард, но не попадает.'
spear = Spear(4, 1, 3, 1, 0, True, False, True, 'Копье', '1-4' + u'\U0001F44A' + "|" + '3' +  u'\U000026A1')
speareternal = SpearEternal(4, 1, 3, 1, 0, True, False, True, 'Копье Нарсил', '1-4' + u'\U0001F44A' + "|" + '3' +  u'\U000026A1', standart=False)
Sawn_off = Weapon(4, 1, 3, 1, 0, False, True, True, 'Обрез', '1-4' + u'\U0001F4A5' + "|" + '3' + u'\U000026A1', pellets=True)
Sawn_off.desc1 = 'Игрок стреляет в Противник из Обреза.'
Sawn_off.desc2 = 'Игрок стреляет в Противник из Обреза.'
Sawn_off.desc3 = 'Игрок стреляет в Противник из Обреза.'
Sawn_off.desc4 = 'Игрок стреляет в Противник из Обреза, но не попадает.'
Sawn_off.desc5 = 'Игрок стреляет в Противник из Обреза, но не попадает.'
Sawn_off.desc6 = 'Игрок стреляет в Противник из Обреза, но не попадает.'
Shotgun = Weapon(6, 2, 4, -2, 0, False, True, True, 'Дробовик', '2-7' + u'\U0001F4A5' + "|" + '4' + u'\U000026A1', pellets=True)
Shotgun.desc1 = 'Игрок стреляет в Противник из Дробовика.'
Shotgun.desc2 = 'Игрок стреляет в Противник из Дробовика.'
Shotgun.desc3 = 'Игрок стреляет в Противник из Дробовика.'
Shotgun.desc4 = 'Игрок стреляет в Противник из Дробовика, но не попадает.'
Shotgun.desc5 = 'Игрок стреляет в Противник из Дробовика, но не попадает.'
Shotgun.desc6 = 'Игрок стреляет в Противник из Дробовика, но не попадает.'
Magnum = Weapon(2, 1, 3, 2, 3, False, False, True, 'Револьвер', '3' + u'\U0001F4A5' + "|" + '3' + u'\U000026A1')
Magnum.desc1 = 'Игрок стреляет в Противник из Револьвера.'
Magnum.desc2 = 'Игрок стреляет в Противник из Револьвера.'
Magnum.desc3 = 'Игрок стреляет в Противник из Револьвера.'
Magnum.desc4 = 'Игрок стреляет в Противник из Револьвера, но не попадает.'
Magnum.desc5 = 'Игрок стреляет в Противник из Револьвера, но не попадает.'
Magnum.desc6 = 'Игрок стреляет в Противник из Револьвера, но не попадает.'
Makarov = Weapon(3, 1, 3, 2, 0, False, False, True, 'Пистолет', '1-3' + u'\U0001F4A5' + "|" + '3' + u'\U000026A1')
Makarov.desc1 = 'Игрок стреляет в Противник из Пистолета.'
Makarov.desc2 = 'Игрок стреляет в Противник из Пистолета.'
Makarov.desc3 = 'Игрок стреляет в Противник из Пистолета.'
Makarov.desc4 = 'Игрок стреляет в Противник из Пистолета, но не попадает.'
Makarov.desc5 = 'Игрок стреляет в Противник из Пистолета, но не попадает.'
Makarov.desc6 = 'Игрок стреляет в Противник из Пистолета, но не попадает.'
Bat = Stunning(3, 1, 2, 2, 0, True, False, True, 'Бейсбольная Бита', '1-3' + u'\U0001F44A' + "|" + '2' +  u'\U000026A1', 3)
Bat.desc1 = 'Игрок бьет Противник Бейсбольной Битой.'
Bat.desc2 = 'Игрок бьет Противник Бейсбольной Битой.'
Bat.desc3 = 'Игрок бьет Противник Бейсбольной Битой.'
Bat.desc4 = 'Игрок бьет Противник Бейсбольной Битой, но не попадает.'
Bat.desc5 = 'Игрок бьет Противник Бейсбольной Битой, но не попадает.'
Bat.desc6 = 'Игрок бьет Противник Бейсбольной Битой, но не попадает.'
fangs = Bleeding(3, 1, 2, 1, 0, True, True, True, 'Клыки', '1-3' + u'\U0001F4A5' + "|" + '2' + u'\U000026A1', 4, standart=False, natural=True)
fangs.desc1 = 'Игрок набрасывается на Противник.'
fangs.desc2 = 'Игрок набрасывается на Противник.'
fangs.desc3 = 'Игрок набрасывается на Противник.'
fangs.desc4 = 'Игрок пытается укусить Противник, но не попадает.'
fangs.desc5 = 'Игрок пытается укусить Противник, но не попадает.'
fangs.desc6 = 'Игрок пытается укусить Противник, но не попадает.'
fists = Weapon(1, 1, 2, 4, 0, True, True, True, 'Кулаки', '1' + u'\U0001F4A5' + "|" + '2' + u'\U000026A1', standart=False, natural=True)
fists.desc1 = 'Игрок бьет Противник Кулаком.'
fists.desc2 = 'Игрок бьет Противник Кулаком.'
fists.desc3 = 'Игрок бьет Противник Кулаком.'
fists.desc4 = 'Игрок бьет Противник Кулаком, но не попадает.'
fists.desc5 = 'Игрок бьет Противник Кулаком, но не попадает.'
fists.desc6 = 'Игрок бьет Противник Кулаком, но не попадает.'
master_fist = MasterFist(3, 1, 2, 2, 0, True, True, True, 'Кулаки','1-3' + u'\U0001F525' + "|" + '2' + u'\U000026A1', standart=False, natural=True)
master_fist.desc1 = 'Игрок бьет Противник Кулаком.'
master_fist.desc2 = 'Игрок бьет Противник Кулаком.'
master_fist.desc3 = 'Игрок бьет Противник Кулаком.'
master_fist.desc4 = 'Игрок бьет Противник Кулаком, но не попадает.'
master_fist.desc5 = 'Игрок бьет Противник Кулаком, но не попадает.'
master_fist.desc6 = 'Игрок бьет Противник Кулаком, но не попадает.'