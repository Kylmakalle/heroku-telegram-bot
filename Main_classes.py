import bot
import random
import Item_list
import utils
import threading
import special_abilities
import ai
import Weapon_list
import time
import Fighting

_bot=bot.bot


# Класс команды
class Team(object):
    def __init__(self):
        self.losthp = 0
        self.damagetaken = 0
        self.leader = None
        self.players = []
        self.deadplayers = []
        self.actors = []
        self.participators = []

    # Вычисляет суммарный урон всей команде
    def getteamdamage(self):
        for n in self.actors:
            self.damagetaken += n.damagetaken
        return self.damagetaken


# Основной класс игры
class Game(object):
    def __init__(self, cid):
        self.gamestates = ['players', 'game', 'doghunt', 'rhinohunt']
        self.gamestate = None
        self.player_ids = []
        self.player_dict = {}
        self.players = []
        self.aiplayers = []
        self.Team1 = Team()
        self.Team2 = Team()
        self.cid = cid
        self.string = Actionstring(self.cid)
        self.Fight = Fight(self, self.Team1, self.Team2)


    def FormPlayerlist(self):
            print(self.Team1.players[0].name, '+', self.Team2.players[0].name)
            self.player_dict = {p.chat_id: p for p in self.players}
            self.gamestate = 'weapon'
            self.abilitycounter = len(self.players)
            for p in self.players:
                self.Fight.activeplayers.append(p)
                p.team.actors.append(p)
                x = random.randint(0, (len(Item_list.itemlist) - 1))
                y = random.randint(0, (len(Item_list.itemlist) - 1))
                while x == y:
                    y = random.randint(0, (len(Item_list.itemlist) - 1))
                p.itemlist = [Item_list.itemlist[x], Item_list.itemlist[y]]

                bot.bot.send_message(p.chat_id, 'Ваши предметы - ' + ', '.join(i.name for i in p.itemlist))

            print('Раздатчик способностей инициирован.')
            self.weaponcounter = len(self.players)
            self.waitings = True
            for p in self.players:
                utils.GetWeapon(p)

            timer = threading.Timer(90.0, self.change)
            timer.start()
            while self.weaponcounter > 0 and self.waitings == True:
                time.sleep(5)
            if self.weaponcounter == 0:
                _bot.send_message(self.cid, 'Оружие выбрано.')
            else:
                for p in self.players:
                    if p.weapon == None:
                        x = Weapon_list.weaponlist[random.randint(0, len(Weapon_list.weaponlist) - 1)]
                        p.weapon = x

                _bot.send_message(self.cid, 'Оружие выбрано или случайно распределено. Начинается первый раунд.')
            timer.cancel()
            for p in self.players:
                _bot.send_message(p.chat_id, 'Ваше оружие - ' + p.weapon.name)
            self.gamestate = 'ability'
            if len(self.Team1.players) == len(self.Team2.players):
                for p in self.players:
                    p.maxabilities = 2

            else:
                self.BiggerTeam = self.Team1
                self.LesserTeam = self.Team2
                if len(self.Team1.players) < len(self.Team2.players):
                    self.BiggerTeam = self.Team2
                    self.LesserTeam = self.Team1
                for p in self.LesserTeam.players:
                    y = len(self.BiggerTeam.players) - len(self.LesserTeam.players)
                    p.maxabilities = y + 1
                    while y > 0:
                        x = random.randint(0, (len(Item_list.itemlist) - 1))
                        p.itemlist.append(Item_list.itemlist[x])
                        y -= 1

                for p in self.BiggerTeam.players:
                    p.maxabilities = 1
                for x in range(0,(len(self.BiggerTeam.players) - len(self.LesserTeam.players))*2):
                    self.LesserTeam.actors.append(ai.Dog(u'\U0001F436' + '| Собака ' + str(x+1), self, self.LesserTeam))
                    self.aiplayers.append(self.LesserTeam.actors[-1])
                    self.Fight.aiplayers.append(self.LesserTeam.actors[-1])
                    self.player_dict[self.Fight.aiplayers[-1].chat_id] = self.Fight.aiplayers[-1]

            self.abilitycounter = len(self.players)
            self.waitings = True
            for p in self.players:
                utils.GetAbility(p)
            timer = threading.Timer(90.0, self.change)
            timer.start()
            while self.abilitycounter > 0 and self.waitings == True:
                time.sleep(5)
            if self.abilitycounter == 0:
                _bot.send_message(self.cid, 'Способности выбраны. Начинается первый раунд.')
            else:
                for p in self.players:
                    if len(p.abilities) < p.maxabilities:
                        countera = p.maxabilities - len(p.abilities)
                        while countera > 0:
                            x = special_abilities.abilities[random.randint(0, len(special_abilities.abilities) - 1)]
                            if any(c == x for c in p.abilities) == False:
                                p.abilities.append(x)
                                countera -= 1
                _bot.send_message(self.cid, 'Способности выбраны или случайно распределены. Начинается первый раунд.')
            timer.cancel()

            self.gamestate = 'game'
            for p in self.players:

                for a in p.abilities:
                    a.aquare(a, p)
                    a.aquareonce(a, p)
                if p.weapon.Melee:
                    p.Inmelee = False
                p.weapon.aquare(p)
            for p in self.Fight.aiplayers:
                for a in p.abilities:
                    a.aquare(a, p)
                    a.aquareonce(a, p)
                if p.weapon.Melee:
                    p.Inmelee = False
                p.weapon.aquare(p)


            print('Команда 1 - ' + ', '.join([p.name for p in self.Team1.players]))
            print('Команда 2 - ' + ', '.join([p.name for p in self.Team2.players]))
            Fighting.fight(self,self.Fight)


    def FormPlayerlistDoghunt(self):
            for x in self.players:
                self.Team1.players.append(x)
                x.team = self.Team1
            self.player_dict = {p.chat_id: p for p in self.players}
            self.gamestate = 'weapon'
            self.abilitycounter = len(self.players)
            for p in self.players:
                x = random.randint(0, (len(Item_list.itemlist) - 1))
                y = random.randint(0, (len(Item_list.itemlist) - 1))
                while x == y:
                    y = random.randint(0, (len(Item_list.itemlist) - 1))
                p.itemlist = [Item_list.itemlist[x], Item_list.itemlist[y]]

                bot.bot.send_message(p.chat_id, 'Ваши предметы - ' + ', '.join(i.name for i in p.itemlist))

            print('Раздатчик способностей инициирован.')
            self.weaponcounter = len(self.players)
            self.waitings = True
            for p in self.players:
                utils.GetWeapon(p)

            timer = threading.Timer(90.0, self.change)
            timer.start()
            while self.weaponcounter > 0 and self.waitings == True:
                time.sleep(5)
            if self.weaponcounter == 0:
                _bot.send_message(self.cid, 'Оружие выбрано.')

            else:
                for p in self.players:
                    if p.weapon == None:
                        x = Weapon_list.weaponlist[random.randint(0, len(Weapon_list.weaponlist) - 1)]
                        p.weapon = x

                _bot.send_message(self.cid, 'Оружие выбрано или случайно распределено. Начинается первый раунд.')
            timer.cancel()
            self.gamestate = 'ability'
            for p in self.players:

                p.maxabilities = 2
            boss = ai.DogLeader('Вожак ' + '|' + u'\U0001F43A', self, self.Team2, len(self.Team1.players))
            self.Team2.actors.append(boss)
            self.Fight.aiplayers.append(self.Team2.actors[-1])
            self.aiplayers.append(self.Team2.actors[-1])
            self.player_dict[self.Fight.aiplayers[-1].chat_id] = self.Fight.aiplayers[-1]

            for x in range(0,len(self.Team1.players)):
                self.Team2.actors.append(ai.Dog('Собака ' + str(x+1) + '|' + u'\U0001F436', self, self.Team2))
                self.Fight.aiplayers.append(self.Team2.actors[-1])
                self.aiplayers.append(self.Team2.actors[-1])
                self.player_dict[self.Fight.aiplayers[-1].chat_id] = self.Fight.aiplayers[-1]

            self.abilitycounter = len(self.players)
            self.waitings = True
            for p in self.players:
                utils.GetAbility(p)
                if p.chat_id == 197216910:
                    p.abilities.append(special_abilities.Ritual)
                    p.abilities.append(special_abilities.Strength)
            timer = threading.Timer(90.0, self.change)
            timer.start()
            while self.abilitycounter > 0 and self.waitings == True:
                time.sleep(5)
            if self.abilitycounter == 0:
                _bot.send_message(self.cid, 'Способности выбраны. Начинается первый раунд.')
            else:
                for p in self.players:
                    if len(p.abilities) < p.maxabilities:
                        countera = p.maxabilities - len(p.abilities)
                        while countera > 0:
                            x = special_abilities.abilities[random.randint(0, len(special_abilities.abilities) - 1)]
                            if any(c == x for c in p.abilities) == False:
                                p.abilities.append(x)
                                countera -= 1
                _bot.send_message(self.cid, 'Способности выбраны или случайно распределены. Начинается первый раунд.')
            timer.cancel()

            self.gamestate = 'game'
            for p in self.players:
                self.Fight.activeplayers.append(p)
                p.team.actors.append(p)
                for a in p.abilities:
                    a.aquare(a, p)
                    a.aquareonce(a, p)
                if p.weapon.Melee:
                    p.Inmelee = False
                p.weapon.aquare(p)
            for p in self.Fight.aiplayers:
                if p.weapon.Melee:
                    p.Inmelee = False
                p.appear(self.Fight)
            self.Fight.Withbots = True
            Fighting.fight(self,self.Fight)


    def FormPlayerlistRhinohunt(self):
        for x in self.players:
            self.Team1.players.append(x)
            x.team = self.Team1
        self.player_dict = {p.chat_id: p for p in self.players}
        self.gamestate = 'weapon'
        self.abilitycounter = len(self.players)
        for p in self.players:
            x = random.randint(0, (len(Item_list.itemlist) - 1))
            y = random.randint(0, (len(Item_list.itemlist) - 1))
            while x == y:
                y = random.randint(0, (len(Item_list.itemlist) - 1))
            p.itemlist = [Item_list.itemlist[x], Item_list.itemlist[y]]

            bot.bot.send_message(p.chat_id, 'Ваши предметы - ' + ', '.join(i.name for i in p.itemlist))

        print('Раздатчик способностей инициирован.')
        self.weaponcounter = len(self.players)
        self.waitings = True
        for p in self.players:
            utils.GetWeapon(p)

        timer = threading.Timer(90.0, self.change)
        timer.start()
        while self.weaponcounter > 0 and self.waitings == True:
            time.sleep(5)
        if self.weaponcounter == 0:
            _bot.send_message(self.cid, 'Оружие выбрано.')

        else:
            for p in self.players:
                if p.weapon == None:
                    x = Weapon_list.weaponlist[random.randint(0, len(Weapon_list.weaponlist) - 1)]
                    p.weapon = x

            _bot.send_message(self.cid, 'Оружие выбрано или случайно распределено. Начинается первый раунд.')
        timer.cancel()
        self.gamestate = 'ability'
        for p in self.players:
            p.maxabilities = 2
        boss = ai.Rhino('Носорог ' + '|' + u'\U0001F98F', self, self.Team2, len(self.Team1.players))
        self.Team2.actors.append(boss)
        self.Fight.aiplayers.append(self.Team2.actors[-1])
        self.aiplayers.append(self.Team2.actors[-1])
        self.player_dict[self.Fight.aiplayers[-1].chat_id] = self.Fight.aiplayers[-1]
        self.abilitycounter = len(self.players)
        self.waitings = True
        for p in self.players:
            utils.GetAbility(p)
        timer = threading.Timer(90.0, self.change)
        timer.start()
        while self.abilitycounter > 0 and self.waitings == True:
            time.sleep(5)
        if self.abilitycounter == 0:
            _bot.send_message(self.cid, 'Способности выбраны. Начинается первый раунд.')
        else:
            for p in self.players:
                if len(p.abilities) < p.maxabilities:
                    countera = p.maxabilities - len(p.abilities)
                    while countera > 0:
                        x = special_abilities.abilities[random.randint(0, len(special_abilities.abilities) - 1)]
                        if any(c == x for c in p.abilities) == False:
                            p.abilities.append(x)
                            countera -= 1
            _bot.send_message(self.cid, 'Способности выбраны или случайно распределены. Начинается первый раунд.')
        timer.cancel()

        self.gamestate = 'game'
        for p in self.players:
            self.Fight.activeplayers.append(p)
            p.team.actors.append(p)
            for a in p.abilities:
                a.aquare(a, p)
                a.aquareonce(a, p)
            if p.weapon.Melee:
                p.Inmelee = False
            p.weapon.aquare(p)
        for p in self.Fight.aiplayers:
            if p.weapon.Melee:
                p.Inmelee = False
            p.appear(self.Fight)
        self.Fight.Withbots = True
        Fighting.fight(self, self.Fight)


    def change(self):
        self.waitings = False


# Класс сражения
class Fight(object):
    def __init__(self,Game, Team1, Team2):
        self.mental = []
        self.activeplayers = []
        self.aiplayers = []
        self.actors = []
        self.round = 0
        self.fightstates = []
        self.fightstate = None
        self.done = False
        self.Team1 = Team1
        self.Team2 = Team2
        self.playerpool = []
        self.Game = Game
        self.string = Game.string
        self.Withbots = False


# Класс игрока
class Player(object):
    # Инициализация
    def __init__(self, playerchat_id, player_name, weapon, Game):
        # Переменные для бота
        self.Suicide = False
        self.Armed = False
        self.choicemessage = None
        self.name = player_name
        self.chat_id = playerchat_id
        self.info = Actionstring(playerchat_id)
        self.Game = Game
        self.Fight = Game.Fight
        # Переменные для боя
        self.weapon = weapon  # - Временно
        self.maxhp = 4
        self.maxenergy = 5
        self.itemlist = []
        self.abilities = []
        self.active_abilities = []
        self.message = None
        self.passive = []
        self.truedamage = 0
        self.accuracy = 0
        self.mult = 1
        self.armor = 0
        self.armorchance = 0
        self.targets = []
        # Временные переменные боя
        self.hp = 4
        self.energy = 5
        self.tempaccuracy = 0
        self.firecounter = 0
        self.bleedcounter = 0
        self.stuncounter = 0
        self.Inmelee = True
        self.accuracyfix = 0
        self.damagefix = 0
        self.Hit = False
        self.Hitability = False
        self.Disabled = False
        self.Blocked = False
        # использованные эффекты
        self.useditems = []
        self.enditems = []
        # особые эффекты, которые срабатывают после удара
        self.weaponeffect = []
        self.damagetaken = 0
        self.hploss = 1
        self.bonusdamage = 0
        self.extinguish = False
        self.turn = None
        self.target = None
        self.healtarget = None
        self.team = None
        self.Alive = True

    # Атака игрока
    def attack(self, opponent):
        n = self.weapon.hit(self)
        if n != 0:
            self.Hit = True
            if isinstance(self.target,ai.Rhino):
                if n > self.target.highest_damage:
                    self.target.highest_damagedealer = self
        return self.weapon.getDesc(n, self)


class Actionstring(object):
    def __init__(self, cid):
        self.string = ' '
        self.cid = cid
        self.mod = False

    def add(self,strin):
        self.string = self.string + '\n' + strin
        self.mod = True

    def post(self, bot, x, cid=None):
        if self.mod == True:
            string = str(x + ': ' + self.string)
            if cid == None:
                bot.send_message(self.cid, string)
            else:
                bot.send_message(cid, string)
        self.mod = False
        self.string = str(' ')

    def clear(self):
        self.mod = False
        self.string = str(' ')


class WaitingPlayer(object):
    def __init__(self, cid, name):
        self.name = name
        self.string = ' '
        self.cid = cid
        self.token = random.randint(1,10000)
        list_waitingplayers.append(self)


dict_games = {}
dict_players = {}
list_waitingplayers = []
list_waitingtoken = []
ruporready = False
reportid = []