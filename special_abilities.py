import utils
import config
import telebot
import Item_list
import random
import sys
import Weapon_list
import bot_handlers


bot = telebot.TeleBot(config.token)
types = telebot.types

abilities = []
usual_abilities = []
unique_abilities =[]

class Ability(object):
    effect = None
    name = None
    info = None

    def aquareonce(self, user):
        pass

    def aquare(self, user):
        pass

    def fightstart(self, user):
        pass

    def special_used(self, user):
        pass

    def special_first(self, user):
        pass

    def special_second(self, user):
        pass

    def special_last(self, user):
        pass

    def special_end(self, user):
        pass

    def stop(self, user):
        pass

    def onhit(self, n, user):
        return n

    def onhitdesc(self, d, user):
        return d

    def ondamage(self, source, target, damage, type):
        pass

sys.path.insert(0, '/abilities')
from abilities import Sturdy


class Sadist(Ability):
    name = 'Садист'
    info = 'Получает энергию за каждое потерянную жизнь твоей цели.'
    MeleeOnly = False
    RangeOnly = False
    TeamOnly = False

    def special_end(self, user):
        n = 0
        if user.target is not None and user.target.damagetaken > 0 and user.target.team.damagetaken != 0 \
                and user.team.damagetaken <= user.target.team.damagetaken:
            n = user.target.hploss
        user.energy += n
        if n != 0:
            user.fight.string.add(u'\U0001F603' + "|" + "Садист " + user.name + ' получает ' + str(n) + ' энергии.')


class Gasmask(Ability):
    name = 'Противогаз'
    info = 'Вы неуязвимы к ядовитому газу. Ваша сопротивляемость огню увеличена.'
    MeleeOnly = False
    RangeOnly = False
    TeamOnly = False

    def aquare(self, user):
        user.passive.append('Gasmask')

    def special_first(self, user):
        if user.firecounter > 0:
            if user.offfire > user.fight.round:
                user.offfire = user.fight.round


class Target(Ability):
    name = 'Прицел'
    info = 'Вероятность попасть по цели из огнестрельного оружия для вас существенно увеличена.'
    MeleeOnly = False
    RangeOnly = True
    TeamOnly = False

    def aquare(self, user):
        if not user.weapon.Melee:
            user.accuracy += 2


class Strength(Ability):
    name = 'Бицепс'
    info = 'Вы получаете 33% вероятность нанести удвоенный урон оружием ближнего боя.'
    MeleeOnly = True
    RangeOnly = False
    TeamOnly = False

    def aquare(self, user):
        if user.weapon.Melee:
            user.Crit = False

    def onhit(self, n, user):
        if random.randint(1, 3) == 2 and user.weapon.Melee:
            print('Crit')
            n *= 2
            user.Crit = True
        return n

    def onhitdesc(self, d, user):
        if user.Crit and user.weapon.Melee:
            d += u'\U00002757'
        return d

    def special_end(self, user):
        if user.weapon.Melee:
            user.Crit = False


class Shields(Ability):
    name = 'Генератор щитов'
    info = 'Вы получаете щит, который обновляется через 3 раунда после использования.'
    MeleeOnly = False
    RangeOnly = False
    TeamOnly = False

    def aquare(self, user):
        user.shieldrefresh = 3

    def special_end(self, user):
        if user.Alive:
            if Item_list.shieldg not in user.itemlist and user.shieldrefresh == user.fight.round:
                user.itemlist.append(Item_list.shieldg)
                bot.send_message(user.chat_id, 'Способность "Щит" обновлена!')
            else:
                if user.shieldrefresh - user.fight.round > 0:
                    bot.send_message(user.chat_id, 'Способность "Щит" обновится через '
                                                   + str(user.shieldrefresh - user.fight.round) + " ход(ов).")


class Revenge(Ability):
    name = 'Месть'
    info = 'Если умирает ваш союзник - ваши статы увеличиваются.'
    MeleeOnly = False
    RangeOnly = False
    TeamOnly = True

    def aquare(self, user):
        user.deadteammates = []
        user.revengecounter = 2

    def special_first(self, user):
        print('Есть ли трупы?')
        if user.deadteammates != user.team.deadplayers:
            print('Обнаружены трупы! ')
            deadbodies = len(user.team.deadplayers) - len(user.deadteammates)
            user.deadteammates = list(user.team.deadplayers)
            counter = 1

            while deadbodies != 0:
                if user.revengecounter != 0:
                    user.fight.string.add(u'\U0001F621' + "|" + 'Увидев неподвижное тело '
                                          + user.team.deadplayers[-counter].name +
                                          ', ' + user.name + ' впадает в ярость! + 1 жизни и урона.')
                    deadbodies -= 1
                    user.bonusdamage += 1
                    user.hp += 1
                    counter += 1
                    user.revengecounter -= 1
                else:
                    break
        else:
            print('Трупов нет!')


class Hoarder(Ability):
    name = 'Запасливый'
    info = 'Вы получаете 2 дополнительных предмета.'
    MeleeOnly = False
    RangeOnly = False
    TeamOnly = False

    def aquare(self, user):
        counter = 2
        defcounter = 0
        while defcounter < counter:
            item = Item_list.itemlist[random.randint(0, len(Item_list.itemlist)-1)]
            if item not in user.itemlist:
                user.itemlist.append(item)
                defcounter += 1


class Mentalist(Ability):
    name = 'Визор'
    info = 'Вы способны видеть информацию о ваших противниках!'
    MeleeOnly = False
    RangeOnly = False
    TeamOnly = False

    def aquare(self, user):
        if not user.weapon.Melee:
            user.accuracy += 1
        user.mentalrefresh = 0
        user.itemlist.append(Item_list.mental)

    def special_end(self, user):
        print('Визор ' + user.name)
        if user.Alive:
            if user.mentalrefresh == user.fight.round:
                user.itemlist.append(Item_list.mental)
                bot.send_message(user.chat_id, 'Способность "Визор" обновлена!')
            elif user.mentalrefresh - user.fight.round > 0:
                bot.send_message(user.chat_id, 'Способность "Визор" обновится через '
                                               + str(user.mentalrefresh - user.fight.round) + " ход(ов).")


class Hypnosyser(Ability):
    name = 'Гипнотизер'
    info = 'Вы можете изменить цель противника на его случайного союзника! Если он стреляет в этот ход, естественно.'
    MeleeOnly = False
    RangeOnly = False
    TeamOnly = False

    def aquare(self, user):
        user.hypnosysrefresh = 0
        user.itemlist.append(Item_list.hypnosys)

    def special_end(self, user):
        print('Гипноз ' + user.name)
        if user.Alive:
            if user.hypnosysrefresh == user.fight.round:
                user.itemlist.append(Item_list.hypnosys)
                bot.send_message(user.chat_id, 'Способность "Гипноз" обновлена!')
            elif user.hypnosysrefresh - user.fight.round > 0:
                bot.send_message(user.chat_id, 'Способность "Гипноз" обновится через '
                                               + str(user.hypnosysrefresh - user.fight.round) + " ход(ов).")



class Armorer(Ability):
    name = 'Крепкий череп'
    info = 'Отнять у вас несколько жизней за ход сложнее.'
    MeleeOnly = False
    RangeOnly = False
    TeamOnly = False
    def aquare(self, user):
        user.toughness += 4


class West(Ability):
    name = 'Бронежилет'
    info = 'Вы получает возможность отразить 1 урона с вероятностью 30%'
    MeleeOnly = False
    RangeOnly = False
    TeamOnly = False

    def aquare(self, user):
        user.armor += 1
        user.armorchance += 30


class Piromant(Ability):
    name = 'Пироман'
    info = 'Вы наносите на 1 урона больше любой атакой за каждого горящего человека.'
    MeleeOnly = False
    RangeOnly = False
    TeamOnly = False

    def special_last(self, user):
        fire = False
        user.bonusdamage = 0
        for p in user.fight.activeplayers:
            if p.firecounter > 0:
                fire = True
                user.bonusdamage += 1
        for p in user.fight.aiplayers:
            if p.firecounter > 0:
                fire = True
                user.bonusdamage += p.firecounter
        if fire is True:
            user.fight.string.add(u'\U0001F47A' + '| Пироман ' + user.name + ' получает бонус +'
                                  + str(user.bonusdamage) + " урона.")
        else:
            pass


class Berserk(Ability):
    name = 'Берсерк'
    info = 'Ваш максимум энергии уменьшается на 2. Он увеличивается за каждую недостающую жизнь. Вы наносите бонусный урон' \
           'пока у вас ровно 1 хп.'
    MeleeOnly = True
    RangeOnly = False
    TeamOnly = False

    def aquare(self, user):
        user.energy -= 2
        user.maxenergy -= 2
        user.berserkenergy = user.maxenergy
        user.Rage = False

    def special_end(self, user):
        berserkenergy = user.berserkenergy + user.maxhp - user.hp
        if user.hp < 1:
            user.energy = user.berserkenergy
        elif berserkenergy < user.maxenergy:
            user.maxenergy = berserkenergy
        elif berserkenergy > user.maxenergy:
            newenergy = berserkenergy - user.maxenergy
            user.maxenergy = berserkenergy
            user.energy += newenergy
            user.fight.string.add(u'\U0001F621' + "| Берсерк " + user.name + ' получает ' + str(newenergy) + ' энергию')
        if user.hp == 1 and not user.Rage:
            user.Rage = True
            user.bonusdamage += 2
            user.fight.string.add(u'\U0001F621' + "| Берсерк " + user.name + ' входит в боевой транс!')
        elif user.hp != 1 and user.Rage == True:
            user.Rage = False


class Healer(Ability):
    name = 'Медик'
    info = 'Вы получаете дополнительный стимулятор.'
    MeleeOnly = False
    RangeOnly = False
    TeamOnly = False

    def aquare(self, user):
        user.itemlist.append(Item_list.heal)


class Undead(Ability):
    name = 'Зомби'
    info = 'После смерти вы получаете шанс отомстить.'
    MeleeOnly = False
    RangeOnly = False
    TeamOnly = False

    def aquare(self, user):
        if 'Zombie' not in user.passive:
            user.passive.append('Zombie')

    def stop(self, user):
        if user.Alive:
            user.passive.remove('Zombie')


class Engineer(Ability):
    name = 'Оружейник'
    info = 'Вы можете перезарядить оружие союзника. Его точность при этом увеличивается на 1 на следующий ход.' \
           'Действует только на оружие дальнего боя.'
    MeleeOnly = False
    RangeOnly = False
    TeamOnly = True

    def aquare(self, user):
        user.engineerrefresh = 0
        user.itemlist.append(Item_list.engineer)

    def stop(self, user):
        user.engineerrefresh = 0

    def special_end(self, user):
        print('Перезарядка ' + user.name)
        if user.Alive:
            if user.engineerrefresh == user.fight.round:
                user.itemlist.append(Item_list.engineer)
                bot.send_message(user.chat_id, 'Способность "Оружейник" обновлена!')
            elif user.engineerrefresh - user.fight.round > 0:
                bot.send_message(user.chat_id, 'Способность "Оружейник" обновится через '
                                               + str(user.engineerrefresh - user.fight.round) + " ход(ов).")


class Impaler(Ability):
    name = 'Таран'


class Ritual(Ability):
    name = 'Ритуалист'
    info = 'Выберите жертву. Если она умрет в течение трех раундов - вы сможете отнять ' \
           '2 жизни у любого игрока на ваш выбор.'
    MeleeOnly = False
    RangeOnly = False
    TeamOnly = False

    def aquare(self, user):
        user.itemlist.append(Item_list.ritual)
        user.cursecounter = 0
        user.cursetarget = None

    def special_end(self, user):
        if user.cursetarget is not None:
            if not user.cursetarget.Alive:
                user.itemlist.append(Item_list.curse)
                bot.send_message(user.chat_id, 'Вы выполнили условие ритуала!')
                user.cursetarget = None
            user.cursecounter -= 1
            if user.cursecounter == 0 and user.cursetarget is not None:
                bot.send_message(user.chat_id, 'Вы потратили ритуал напрасно')
                user.cursetarget = None


class Blocker(Ability):
    name = 'Защитник'
    info = 'Пока вы живы - противник не может атаковать других игроков в ближнем бою. Не работает против ботов.'
    MeleeOnly = True
    RangeOnly = False
    TeamOnly = True


class Necromancer(Ability):
    name = 'Некромант'
    info = 'Вы можете поднять зомби.'
    MeleeOnly = True
    RangeOnly = False
    TeamOnly = True

    def aquare(self, user):
        user.itemlist.append(Item_list.zombie)
    def special_end(self, user):
        if Item_list.zombie not in user.itemlist:
            user.itemlist.append(Item_list.zombie)


class Zombie(Ability):
    name = 'Мертвец'
    def aquare(self, user):
        user.energy = 0
        user.hp = 0

    def special_end(self, user):
        if user.Hit and user.target.Losthp:
            user.hungercounter = 2
        else:
            user.fight.string.add(u'\U0001F631' + '| Зомби ' + user.name + ' страдает от голода!')
            user.hungercounter -= 1
        if user.hungercounter == 0:
            user.abilities.remove(Zombie)
            user.team.actors.remove(user)
            user.team.players.remove(user)
            user.team.deadplayers.append(user)
            user.fight.activeplayers.remove(user)
            user.fight.actors.remove(user)
            user.fight.string.add(u'\U00002620' + '| Зомби ' + user.name + ' не может больше двигаться.')
        user.accuracy = 6 - user.hungercounter*2


class Isaev(Ability):
    name = 'Исаев'
    info = 'Вы можете изменить цель противника на его случайного союзника! Если он стреляет в этот ход, естественно.'
    MeleeOnly = False
    RangeOnly = False
    TeamOnly = False

    def aquare(self, user):
        user.isaevrefresh = 0
        user.itemlist.append(Item_list.isaev)

    def special_end(self, user):
        if user.Alive:
            if user.isaevrefresh == user.fight.round:
                user.itemlist.append(Item_list.isaev)
                bot.send_message(user.chat_id, 'Способность "Исаев" обновлена!')
            elif user.isaevrefresh - user.fight.round > 0:
                bot.send_message(user.chat_id, 'Способность "Исаев" обновится через '
                                 + str(user.isaevrefresh - user.fight.round) + " ход(ов).")


class Thieve(Ability):

    name = 'Вор'
    info = 'Вы можете украсть используемый предмет.'
    MeleeOnly = False
    RangeOnly = False
    TeamOnly = False

    def aquare(self, user):
        user.accuracy += 1
        user.stealrefresh = 0
        user.itemlist.append(Item_list.steal)

    def special_end(self, user):
        if user.Alive:
            if user.stealrefresh == user.fight.round:
                user.itemlist.append(Item_list.steal)
                bot.send_message(user.chat_id, 'Способность "Украсть" обновлена!')
            elif user.stealrefresh - user.fight.round > 0:
                bot.send_message(user.chat_id, 'Способность "Украсть" обновится через '
                                               + str(user.stealrefresh - user.fight.round) + " ход(ов).")


class WeaponMaster(Ability):

    name = 'Оружейник'
    info = 'Вы можете менять оружие во время игры.'
    MeleeOnly = False
    RangeOnly = False
    TeamOnly = False

    def aquare(self, user):
        if user.sec_weapon is None:
            user.sec_weapon = Weapon_list.fists
        user.change_refresh = 0
        user.itemlist.append(Item_list.change_weapon)

    def set(self, user):
        keyboard = types.InlineKeyboardMarkup()
        maxchoiceint = 3
        choice = []
        while len(choice) < maxchoiceint:
            x = Weapon_list.weaponlist[random.randint(0, len(Weapon_list.weaponlist) - 1)]
            if x not in choice:
                choice.append(x)
        for c in choice:
            callback_button1 = types.InlineKeyboardButton(text=c.name,
                                                          callback_data=str(
                                                              'sec-wep' + c.name))
            keyboard.add(callback_button1)
        bot.edit_message_text('Выберите оружие для смены.', message_id=self.message.message_id, chat_id=self.message.chat.id,
                         reply_markup=keyboard)

    def special_end(self, user):
        if user.Alive:
            if user.change_refresh == user.fight.round:
                user.itemlist.append(Item_list.change_weapon)
                bot.send_message(user.chat_id, 'Способность "Оружейник" обновлена!')
            elif user.change_refresh - user.fight.round > 0:
                bot.send_message(user.chat_id, 'Способность "Оружейник" обновится через '
                                               + str(user.change_refresh - user.fight.round) + " ход(ов).")




class Jet(Ability):

    name = 'Джет'
    info = 'Вы можете украсть используемый предмет.'
    MeleeOnly = False
    RangeOnly = False
    TeamOnly = False

    def special_end(self, user):
        if user.jetturn == user.fight.round:
            user.energy = user.maxenergy
            user.fight.string.add(u'\U0001F489' + " |" + 'Энергия ' + user.name
                                  + ' восстановлена до максимальной! (' + str(user.energy) + ')')

            user.tempabilities.append(self)


class Chitin(Ability):

    name = 'Хитин'
    info = 'Вы можете украсть используемый предмет.'
    MeleeOnly = False
    RangeOnly = False
    TeamOnly = False

    def special_end(self, user):
        if user.chitinoff == user.fight.round:
            user.armor -= 2
            user.armorchance -= 100
            user.stuncounter += 1
            user.fight.string.add(u'\U0001F300' + " |" + user.name + ' теряет эффект Хитина. Игрок оглушен!')
            user.tempabilities.append(self)


class Junkie(Ability):

    name = 'Наркоман'
    info = 'Вы теряет 1 точность. Каждый раз, когда вы используете Адреналин, Хитин, Стимулятор или Джет - ' \
           'вы получаете 2 точности и 1 урон. Вы получаете одно из этих веществ.'

    MeleeOnly = False
    RangeOnly = False
    TeamOnly = False

    def aquare(self, user):
        x = random.randint(1, 4)
        if x == 1:
            user.itemlist.append(Item_list.drug)
        elif x == 2:
            user.itemlist.append(Item_list.chitin)
        elif x == 3:
            user.itemlist.append(Item_list.heal)
        elif x == 4:
            user.itemlist.append(Item_list.jet)
        user.accuracy -= 1

    def special_used(self, user):
        if user.Drugged:
            user.tempaccuracy += 2
            user.bonusdamage += 1
            user.damagefix += 1
            user.fight.string.add(u'\U0001F643' + " |" + user.name + ' получает бонусную точность и урон!')

class IronFist(Ability):

    name = 'Железный кулак'
    info = 'Вы теряете свое оружие. Деритесь голыми руками. В отчете оружия не отображается.'

    MeleeOnly = False
    RangeOnly = False
    TeamOnly = False

    def aquare(self, user):
        user.weapon = Weapon_list.master_fist

abilities.append(Piromant)
abilities.append(Armorer)
abilities.append(Revenge)
abilities.append(Hypnosyser)
abilities.append(Sadist)
abilities.append(Mentalist)
abilities.append(Gasmask)
abilities.append(Target)
abilities.append(Shields)
abilities.append(Strength)
abilities.append(Hoarder)
abilities.append(Undead)
abilities.append(Engineer)
abilities.append(WeaponMaster)
abilities.append(West)
abilities.append(Healer)
abilities.append(Ritual)
abilities.append(Blocker)
abilities.append(Berserk)
abilities.append(Necromancer)
abilities.append(Thieve)
abilities.append(Junkie)
unique_abilities.append(IronFist)
usual_abilities.append(Sturdy.Sturdy)
usual_abilities.append(Piromant)
usual_abilities.append(Armorer)
usual_abilities.append(Revenge)
usual_abilities.append(Sadist)
usual_abilities.append(Mentalist)
usual_abilities.append(Gasmask)
usual_abilities.append(Target)
usual_abilities.append(Shields)
usual_abilities.append(Strength)
usual_abilities.append(Hoarder)
usual_abilities.append(Undead)
usual_abilities.append(Engineer)
usual_abilities.append(West)
usual_abilities.append(Healer)
usual_abilities.append(Ritual)
usual_abilities.append(Blocker)
usual_abilities.append(Berserk)
usual_abilities.append(Necromancer)
usual_abilities.append(WeaponMaster)
usual_abilities.append(Thieve)
usual_abilities.append(Junkie)
unique_abilities.append(IronFist)
