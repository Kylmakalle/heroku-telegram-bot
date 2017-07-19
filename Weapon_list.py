import utils
import random
import telebot
import config

types = telebot.types
bot = telebot.TeleBot(config.token)
weaponlist = []
fullweaponlist = []


class Weapon(object):
    def __init__(self, dice, damage, energy, bonus, mult, Melee, TwoHanded, Concealable, name, damagestring, standart=True, pellets=False):
        self.dice = dice
        self.damage = damage
        self.energy = energy
        self.mult = mult
        self.bonus = bonus
        self.Melee = Melee
        self.TwoHanded = TwoHanded
        self.Concealable = Concealable
        self.name = name
        self.damagestring = damagestring
        self.standart = standart
        self.pellets = pellets
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
            if x > 10 - user.energy - self.bonus - user.accuracy - user.tempaccuracy:

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
                n+=1
        for a in user.abilities:
            n = a.onhit(a,n, user)
        # уходит энергия

        user.energy -= self.energy
        # применяется урон
        user.target.damagetaken += n + user.truedamage
        # применяется потеря жизней
        if user.target.hploss < user.mult and n + user.truedamage != 0:
            user.target.hploss = user.mult
        # энергия загоняется в 0
        if user.energy < 0: user.energy = 0
        return n

    # При экипировке
    def aquare(self,user):
        pass

    # Создание описания
    def getDesc(self, damagetaken,user):
        if damagetaken != 0:
            if not self.Melee:
                d =  str(u'\U0001F4A5' + "|" + getattr(self,str('desc' + str(random.randint(1, 3)))) + " Нанесено " + str(damagetaken) + ' урона.')
            else:
                d =  str(u'\U0001F44A' + "|" + getattr(self,str('desc' + str(random.randint(1, 3)))) + " Нанесено " + str(damagetaken) + ' урона.')
                for a in user.abilities:
                    d = a.onhitdesc(a,d,user)
        else:
            d =  str(u'\U0001F4A8' + "|" + getattr(self,str('desc' + str(random.randint(4, 6)))))
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
                p.Fight.playerpool.remove(p)
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
            if x > 10 - user.energy - self.bonus - user.accuracy - user.bonusaccuracy - user.tempaccuracy:
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
        # применяется урон
        user.target.damagetaken += n + user.truedamage
        # применяется потеря жизней
        if user.target.hploss < self.mult and n + user.truedamage != 0:
            user.target.hploss = self.mult
        # энергия загоняется в 0
        if user.energy < 0: user.energy = 0
        return n

    def aquare(self,user):
        user.aimtarget = None
        user.bonusaccuracy = 0

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
        if user.aimtarget!=call.data[3:]:
            user.aimtarget = call.data[3:]
            user.bonusaccuracy = 5
        else:
            user.bonusaccuracy +=5
        if user.energy + self.bonus + user.accuracy + user.bonusaccuracy >= 10:
            bot.send_message(user.chat_id, 'Точность максимальна!')
        print ('scheck')


    desc1 = 'Игрок стреляет в Противник из Снайперской винтовки.'
    desc2 = 'Игрок стреляет в Противник из Снайперской винтовки.'
    desc3 = 'Игрок стреляет в Противник из Снайперской винтовки.'
    desc4 = 'Игрок стреляет в Противник из Снайперской винтовки, но не попадает.'
    desc5 = 'Игрок стреляет в Противник из Снайперской винтовки, но не попадает.'
    desc6 = 'Игрок стреляет в Противник из Снайперской винтовки, но не попадает.'


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
            if x > 10 - user.energy - self.bonus - user.accuracy - user.tempaccuracy:
                n += 1
            d += 1
        if n != 0:
            user.target.firecounter += 1
            user.target.offfire = user.Fight.round + 2

            n += user.bonusdamage + self.damage - 1
        else:
            pass
        n += user.truedamage
        user.target.damagetaken += n
        # применяется урон

        # применяется потеря жизней
        if user.target.hploss < self.mult and n!= 0:
            user.target.hploss = self.mult
        # энергия загоняется в 0
        if self.Melee:
            user.energy -= random.randint(1, 2)
        else:
            user.energy -= self.energy
        if user.energy < 0: user.energy = 0

        print('fire')
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
    def __init__(self, dice, damage, energy, bonus, mult, Melee, TwoHanded, Concealable, name, damagestring, chance,
                 standart=True):
        Weapon.__init__(self, dice, damage, energy, bonus, mult, Melee, TwoHanded, Concealable, name, damagestring,standart=standart)
        self.chance = chance
        if self.standart == True:
            weaponlist.append(self)

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
                n = a.onhit(a,n, user)
        else:
            pass
        n += user.truedamage
        user.target.damagetaken += n
        # применяется урон

        # применяется потеря жизней
        if user.target.hploss < self.mult and n!= 0:
            user.target.hploss = self.mult
        # энергия загоняется в 0

        if user.energy < 0: user.energy = 0

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


class Stunning(Weapon):
    def __init__(self, dice, damage, energy, bonus, mult, Melee, TwoHanded, Concealable, name, damagestring, chance,
                 standart=True):
        Weapon.__init__(self, dice, damage, energy, bonus, mult, Melee, TwoHanded, Concealable, name, damagestring,
                        standart=standart)
        self.chance = chance
        if self.standart == True:
            weaponlist.append(self)

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
        user.target.damagetaken += n
        # применяется урон

        # применяется потеря жизней
        if user.target.hploss < self.mult and n!= 0:
            user.target.hploss = self.mult
        # энергия загоняется в 0

        if user.energy < 0: user.energy = 0

        return n

    def effect(self, user):
        if random.randint(1,10)< self.chance:
            if user.target.stuncounter < 1:
                user.target.stuncounter = 1
            user.Fight.string.add(u'\U0001F300' + '|' + user.target.name + ' оглушен!')
        user.weaponeffect.remove(self)

    def getDesc(self, damagetaken,user):
        if damagetaken != 0:
            user.weaponeffect.append(self)
            if not self.Melee:
                d = str(u'\U0001F4A5' + "|" + getattr(self,str('desc' + str(random.randint(1, 3)))) + " Нанесено " + str(damagetaken) + ' урона.')
            else:
                d = str(u'\U0001F44A' + "|" + getattr(self,str('desc' + str(random.randint(1, 3)))) + " Нанесено " + str(damagetaken) + ' урона.')
            for a in user.abilities:
                d = a.onhitdesc(a,d,user)
            return d
        else:
            return str(u'\U0001F4A8' + "|" + getattr(self,str('desc' + str(random.randint(4, 6)))))


class BowBleeding(Weapon):
    def __init__(self, dice, damage, energy, bonus, mult, Melee, TwoHanded, Concealable, name, damagestring, chance,
                 standart=True):
        Weapon.__init__(self, dice, damage, energy, bonus, mult, Melee, TwoHanded, Concealable, name, damagestring,standart=standart)
        self.chance = chance
        if self.standart == True:
            weaponlist.append(self)

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
            if x > 10 - user.energy - self.bonus - user.accuracy - user.bonusaccuracy - user.tempaccuracy:
                n += 1
            d += 1

        # бонусный урон персонажа
        if n != 0:
            n += user.bonusdamage + self.damage - 1
            if user.bonusaccuracy > 0:
                n+= user.bonusaccuracy*2
        if n != 0 and random.randint(1,10)< self.chance + user.bonusaccuracy:
            user.target.bleedcounter += 1
            user.target.bloodloss = False
            user.Hitability = True
        # уходит энергия
        user.energy -= self.energy + user.bonusaccuracy
        # применяется урон
        user.target.damagetaken += n + user.truedamage
        # применяется потеря жизней
        if user.target.hploss < self.mult and n + user.truedamage != 0:
            user.target.hploss = self.mult
        # энергия загоняется в 0
        if user.energy < 0: user.energy = 0
        return n

    def aquare(self,user):
        user.bonusaccuracy = 0

    def get_action(self, p, call):
        keyboard1 = types.InlineKeyboardMarkup()
        enemyteam = p.targets
        p.turn = call.data
        for c in p.targets:
                keyboard1.add(types.InlineKeyboardButton(text=c.name, callback_data=str('op' + str(c.chat_id))))
        if p.energy - p.bonusaccuracy > 1 and p.bonusaccuracy < 3:
            keyboard1.add(types.InlineKeyboardButton(text="Натянуть", callback_data=str('draw')))
        keyboard1.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('opcancel')))
        bot.send_message(p.chat_id, 'Выберите противника.', reply_markup=keyboard1)

    def special(self, user, call):
        user.bonusaccuracy +=1
        user.Armed = True
        print ('scheck')

    def effect(self, user):
        x = random.randint(1, 10)
        if user.Hit:
            print('Оглушение ' + str(x) + ' < '+ str(user.bonusaccuracy-1)*6)
            if random.randint(1, 10) < (user.bonusaccuracy-1)*6:
                if user.target.stuncounter < 1:
                    user.target.stuncounter = 1
                user.Fight.string.add(u'\U0001F300' + '|' + user.target.name + ' оглушен!')
        user.weaponeffect.remove(self)

        user.bonusaccuracy = 0
        user.Armed = False


tazer = Tazer(3, 1, 2, 2, 1, True, False, True, 'Полицейская Дубинка', '1-3' + u'\U0001F44A' + "|" + '2' + u'\U000026A1')
sniper = Sniper(1, 8, 5, -3, 1, False, False, False, 'Снайперская винтовка','8' + u'\U0001F4A5' + "|" + '5' + u'\U000026A1')
flamethrower = Flamethrower(1, 1, 3, 3, 1, False, False, False, 'Огнемет','1' + u'\U0001F525' + "|" + '3' + u'\U000026A1')
knife = Bleeding(3, 1, 2, 2, 1, True, False, False, 'Нож','1-3' + u'\U0001F525' + "|" + '2' + u'\U000026A1',6)
knife.desc1 = 'Игрок бьет Противник Ножом!'
knife.desc2 = 'Игрок бьет Противник Ножом!'
knife.desc3 = 'Игрок бьет Противник Ножом!'
knife.desc4 = 'Игрок бьет Противник Ножом, но не попадает.'
knife.desc5 = 'Игрок бьет Противник Ножом, но не попадает.'
knife.desc6 = 'Игрок бьет Противник Ножом, но не попадает.'
bow = BowBleeding(2, 2, 1, 0, 1, False, False, False, 'Лук Асгард','2-3!' + u'\U0001F525' + "|" + '1!' + u'\U000026A1',3, standart=False)
bow.desc1 = 'Игрок стреляет в Противник из Лука Асгард.'
bow.desc2 = 'Игрок стреляет в Противник из Лука Асгард.'
bow.desc3 = 'Игрок стреляет в Противник из Лука Асгард.'
bow.desc4 = 'Игрок стреляет в Противник из Лука Асгард, но не попадает.'
bow.desc5 = 'Игрок стреляет в Противник из Лука Асгард, но не попадает.'
bow.desc6 = 'Игрок стреляет в Противник из Лука Асгард, но не попадает.'

Sawn_off = Weapon(4, 1, 3, 1, 1, False, True, True, 'Обрез', '1-4' + u'\U0001F4A5' + "|" + '3' + u'\U000026A1', pellets=True)
Sawn_off.desc1 = 'Игрок стреляет в Противник из Обреза.'
Sawn_off.desc2 = 'Игрок стреляет в Противник из Обреза.'
Sawn_off.desc3 = 'Игрок стреляет в Противник из Обреза.'
Sawn_off.desc4 = 'Игрок стреляет в Противник из Обреза, но не попадает.'
Sawn_off.desc5 = 'Игрок стреляет в Противник из Обреза, но не попадает.'
Sawn_off.desc6 = 'Игрок стреляет в Противник из Обреза, но не попадает.'
Shotgun = Weapon(6, 2, 4, -2, 1, False, True, True, 'Дробовик', '2-7' + u'\U0001F4A5' + "|" + '4' + u'\U000026A1', pellets=True)
Shotgun.desc1 = 'Игрок стреляет в Противник из Дробовика.'
Shotgun.desc2 = 'Игрок стреляет в Противник из Дробовика.'
Shotgun.desc3 = 'Игрок стреляет в Противник из Дробовика.'
Shotgun.desc4 = 'Игрок стреляет в Противник из Дробовика, но не попадает.'
Shotgun.desc5 = 'Игрок стреляет в Противник из Дробовика, но не попадает.'
Shotgun.desc6 = 'Игрок стреляет в Противник из Дробовика, но не попадает.'
Magnum = Weapon(1, 3, 3, 3, 1, False, False, True, 'Револьвер', '3' + u'\U0001F4A5' + "|" + '3' + u'\U000026A1')
Magnum.desc1 = 'Игрок стреляет в Противник из Револьвера.'
Magnum.desc2 = 'Игрок стреляет в Противник из Револьвера.'
Magnum.desc3 = 'Игрок стреляет в Противник из Револьвера.'
Magnum.desc4 = 'Игрок стреляет в Противник из Револьвера, но не попадает.'
Magnum.desc5 = 'Игрок стреляет в Противник из Револьвера, но не попадает.'
Magnum.desc6 = 'Игрок стреляет в Противник из Револьвера, но не попадает.'
Makarov = Weapon(2, 2, 3, 2, 1, False, False, True, 'Пистолет', '2-3' + u'\U0001F4A5' + "|" + '3' + u'\U000026A1')
Makarov.desc1 = 'Игрок стреляет в Противник из Пистолета.'
Makarov.desc2 = 'Игрок стреляет в Противник из Пистолета.'
Makarov.desc3 = 'Игрок стреляет в Противник из Пистолета.'
Makarov.desc4 = 'Игрок стреляет в Противник из Пистолета, но не попадает.'
Makarov.desc5 = 'Игрок стреляет в Противник из Пистолета, но не попадает.'
Makarov.desc6 = 'Игрок стреляет в Противник из Пистолета, но не попадает.'
Bat = Stunning(3, 1, 2, 2, 1, True, False, True, 'Бейсбольная Бита', '1-3' + u'\U0001F44A' + "|" + '2' +  u'\U000026A1', 3)
Bat.desc1 = 'Игрок бьет Противник Бейсбольной Битой.'
Bat.desc2 = 'Игрок бьет Противник Бейсбольной Битой.'
Bat.desc3 = 'Игрок бьет Противник Бейсбольной Битой.'
Bat.desc4 = 'Игрок бьет Противник Бейсбольной Битой, но не попадает.'
Bat.desc5 = 'Игрок бьет Противник Бейсбольной Битой, но не попадает.'
Bat.desc6 = 'Игрок бьет Противник Бейсбольной Битой, но не попадает.'