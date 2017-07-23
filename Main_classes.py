import random
import ai
import Fighting


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
    gamestates = ['players', 'weapon', 'abilities', 'fight']
    gametypes = ['game', 'rhino', 'wolfs']

    def __init__(self, cid):
        self.gamestate = None
        self.gametype = None
        self.player_ids = []
        self.player_dict = {}
        self.players = []
        self.aiplayers = []
        self.team1 = Team()
        self.team2 = Team()
        self.cid = cid
        self.waitings = None
        self.string = Actionstring(self.cid)
        self.fight = Fight(self, self.team1, self.team2)

    def startfight(self):
        Fighting.fight_loop(self, self.fight)

    def change(self):
        self.waitings = False


# Класс сражения
class Fight(object):
    def __init__(self, game, team1, team2):
        self.mental = []
        self.activeplayers = []
        self.aiplayers = []
        self.actors = []
        self.round = 0
        self.fightstates = []
        self.fightstate = None
        self.done = False
        self.team1 = team1
        self.team2 = team2
        self.playerpool = []
        self.game = game
        self.string = game.string
        self.Withbots = False


# Класс игрока
class Player(object):
    # Инициализация
    def __init__(self, playerchat_id, player_name, weapon, game):
        # Переменные для бота
        self.Suicide = False
        self.Armed = False
        self.choicemessage = None
        self.name = player_name
        self.chat_id = playerchat_id
        self.info = Actionstring(playerchat_id)
        self.game = game
        self.fight = game.fight
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
        self.lostweapon = None
        self.toughness = 6
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
        self.Losthp = False
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
        self.hypnosysresist = 0
        self.bot = False

    # Атака игрока
    def attack(self):
        n = self.weapon.hit(self)
        if n != 0:
            self.Hit = True
            if isinstance(self.target, ai.Rhino):
                if n > self.target.highest_damage:
                    self.target.highest_damagedealer = self
        return self.weapon.getDesc(n, self)


class Actionstring(object):
    def __init__(self, cid):
        self.string = ' '
        self.cid = cid
        self.mod = False

    def add(self, strin):
        self.string = self.string + '\n' + strin
        self.mod = True

    def post(self, bot, x, cid=None):
        if self.mod:
            string = str(x + ': ' + self.string)
            if cid is None:
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
        self.token = random.randint(1, 10000)
        list_waitingplayers.append(self)


existing_games = {}
dict_players = {}
list_waitingplayers = []
list_waitingtoken = []
ruporready = False
reportid = []
