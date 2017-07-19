import Weapon_list
import utils
import random
import Main_classes
import special_abilities


class AI_player(object):
    def __init__(self, name, Game, team):
        # Переменные для бота
        self.weapon = None
        self.name = name
        self.Game = Game
        self.Fight = Game.Fight
        self.chat_id = random.randint(1,1000)
        self.info = Main_classes.Actionstring(self.chat_id)
        self.turn = None
        # Переменные для боя
        self.maxhp = 3
        self.maxenergy = 4
        self.truedamage = 0
        self.accuracy = 0
        self.mult = 1
        self.armor = 0
        self.armorchance = 0
        self.itemlist = []
        self.passive = []
        self.abilities = []
        self.targets = []
        self.Blocked = False
        self.hypnosysresist = 40
        # Временные переменные боя
        self.hp = 3
        self.energy = 4
        self.tempaccuracy = 0
        self.firecounter = 0
        self.bleedcounter = 0
        self.stuncounter = 0
        self.Hit = False
        self.Hitability = False
        self.accuracyfix = 0
        self.damagefix = 0
        self.Inmelee = False
        self.Disabled = False
        # особые эффекты, которые срабатывают после удара
        self.weaponeffect = []
        self.damagetaken = 0
        self.hploss = 1
        self.bonusdamage = 0
        self.extinguish = False
        self.turn = None
        self.target = None
        self.healtarget = None
        self.team = team
        self.Alive = True
        self.useditems = []
        self.enditems = []

    def attack(self, opponent):
            n = self.weapon.hit(self)
            if n != 0: self.Hit = True
            return self.weapon.getDesc(n, self)

    def aiaction1q(self, Fight):
            pass
    def aiaction2q(self, Fight):
        pass
    def aiactionlastq(self, Fight):
        pass
    def aiactionend(self, Fight):
        pass
    def appear(self, Fight):
        pass


class Dog(AI_player):

    def __init__(self, name, Game, team):
        AI_player.__init__(self, name, Game, team)
        self.abilities = [Bloodthurst]
        self.weapon = fangs
        self.servant = False
        self.leader = None
        self.offfire = None

    def rest(self):
        self.energy = self.maxenergy
        return u'\U0001F624' + "|" + self.name + ' тяжело дышит. Энергия полностью восстановлена.'

    def get_turn(self, Fight):
        if self.Disabled:
            self.turn = 'disabled'
        elif self.firecounter > 1 and self.offfire != Fight.round:
                Fight.string.add(self.name + ' катается по земле и гасит пламя.')
                self.extinguish = True
                self.turn = 'skip' + str(Fight.round)

        elif self.Inmelee:
                minhp = 10
                for player in utils.GetOtherTeam(self).actors:
                    if player.hp < minhp:
                        minhp = player.hp
                        self.target = player


                if random.randint(1,3) == 1 and self.energy > 1:
                    self.target = utils.GetOtherTeam(self).actors[random.randint(0,len(utils.GetOtherTeam(self).actors) - 1)]
                    self.turn = 'attack' + str(Fight.round)
                elif self.target.hp == 1 and self.energy > 0:
                    self.tempaccuracy += 3
                    self.turn = 'attack' + str(Fight.round)
                elif self.energy > 2:
                    self.turn = 'attack' + str(Fight.round)
                elif self.firecounter > 0:
                    Fight.string.add(self.name + ' катается по земле и гасит пламя.')
                    self.extinguish = True
                    self.turn = 'skip' + str(Fight.round)
                else:
                    self.turn = 'dog_rest' + str(Fight.round)
                    print('sobaka otdih')

        else:
            self.turn = 'move' + str(Fight.round)

    def aiaction2q(self, Fight):
        if self.turn == 'dog_rest' + str(Fight.round):
            Fight.string.add(self.rest())

    def appear(self, Fight):
        for actor in self.team.actors:
            print(actor.name + ' leader?')
            if isinstance(actor, DogLeader):
                print(actor.name + ' yes')
                self.servant = True
                self.leader = actor

    def aiactionend(self, Fight):
        print('run?')
        x = random.randint(1,5)
        print(str(x))
        if self.leader != None:
            if self.leader.hp <= 0 and x > 3 and len(utils.GetOtherTeam(self).actors) > 0\
                    and len(utils.GetOtherTeam(self).actors) >= len(self.team.actors) and self.hp > 0 and self.hp < 3:
                self.Alive = False
                Fight.string.add(u'\U00002620' + ' |' + self.name + ' трусливо сбегает с поля боя.')
                self.team.actors.remove(self)
                Fight.aiplayers.remove(self)
                Fight.actors.remove(self)

fangs = Weapon_list.Bleeding(3, 1, 2, 1, 1, True, True, True, 'Клыки', '1-3' + u'\U0001F4A5' + "|" + '2' + u'\U000026A1', 4, standart = False)
fangs.desc1 = 'Игрок набрасывается на Противник.'
fangs.desc2 = 'Игрок набрасывается на Противник.'
fangs.desc3 = 'Игрок набрасывается на Противник.'
fangs.desc4 = 'Игрок пытается укусить Противник, но не попадает.'
fangs.desc5 = 'Игрок пытается укусить Противник, но не попадает.'
fangs.desc6 = 'Игрок пытается укусить Противник, но не попадает.'


class Bloodthurst(special_abilities.Ability):
    name = 'Кровожадность'


class DogLeader(AI_player):
    def __init__(self, name, Game, team, teambonus):
        AI_player.__init__(self, name, Game, team)
        self.abilities = [special_abilities.Gasmask, Bloodthurst, Howl, special_abilities.Armorer, Leader]
        self.teambonus = teambonus
        self.maxhp = 3 + teambonus
        self.hp = 3 + teambonus
        self.maxenergy = 3 + teambonus
        self.energy = 3 + teambonus
        self.bonusdamage += teambonus
        self.howlcounter = 0
        self.weapon = leaderfangs
        self.final = False
        self.wonpic = 'BQADAgADMAEAAsR9WEvmg8J4vxV91wI'
    def rest(self):
        self.energy = self.maxenergy
        return u'\U0001F624' + "|" + self.name + ' тяжело дышит. Энергия полностью восстановлена.'

    def get_turn(self, Fight):
        if float(self.hp)<=self.maxhp/2 and self.final is False:
            self.Fight.string.add(u'\U00002757' + "|"+self.name + ' злобно рычит!')
            self.bonusdamage += self.teambonus - 1
            self.armor += 2
            self.armorchance += 20
            self.accuracy += 2
            self.maxenergy += self.teambonus
            self.final = True
        if self.Disabled:
            self.turn = 'disabled'
        elif self.howlcounter is 0 and self.energy > 0 and random.randint(1,3) == 1 and Fight.round != 1 and len(self.team.actors) != 1 \
                and not any(x.energy==0 for x in self.team.actors) and self.hp != 1:
            self.turn = 'howl' + str(Fight.round)
            self.energy -= 1

        elif self.Inmelee:
                minhp = 10
                for player in utils.GetOtherTeam(self).actors:
                    if player.hp < minhp:
                        minhp = player.hp
                        self.target = player
                if random.randint(1,3) == 1 and self.energy > 1:
                    self.target = utils.GetOtherTeam(self).actors[random.randint(0,len(utils.GetOtherTeam(self).actors) - 1)]
                    self.turn = 'attack' + str(Fight.round)
                elif self.target.hp == 1 and self.energy > 0:
                    self.tempaccuracy += 3
                    self.turn = 'attack' + str(Fight.round)
                elif self.energy > 2:
                    self.turn = 'attack' + str(Fight.round)

                else:
                    self.turn = 'dog_rest' + str(Fight.round)

        else:
            self.turn = 'move' + str(Fight.round)
    def aiaction1q(self, Fight):
        if self.howlcounter > 0:
            self.howlcounter -= 1
    def aiaction2q(self, Fight):
        if self.turn == 'dog_rest' + str(Fight.round):
            Fight.string.add(self.rest())
        if self.turn == 'howl' + str(Fight.round):
            Fight.string.add(u'\U00002757' + "|"+self.name + ' издает пронзительный вой! Характеристики собак временно увеличены!')
            self.howlcounter = 3

    def aiactionend(self, Fight):
        if self.turn == 'howl' + str(Fight.round):
            for actor in self.team.actors:
                print(actor.name + ' howl?')
                if isinstance(actor, Dog):
                    print(actor.name + ' yes?')
                    actor.energy += 2
                    actor.accuracy += 2
                    actor.accuracyfix += 2
                    actor.bonusdamage += 1
                    actor.damagefix += 1

leaderfangs = Weapon_list.Bleeding(3, 1, 2, 1, 1, True, True, True, 'Клыки', '1-5' + u'\U0001F4A5' + "|" + '2' + u'\U000026A1', 4, standart = False)
leaderfangs.desc1 = 'Игрок набрасывается на Противник.'
leaderfangs.desc2 = 'Игрок набрасывается на Противник.'
leaderfangs.desc3 = 'Игрок набрасывается на Противник.'
leaderfangs.desc4 = 'Игрок пытается укусить Противник, но не попадает.'
leaderfangs.desc5 = 'Игрок пытается укусить Противник, но не попадает.'
leaderfangs.desc6 = 'Игрок пытается укусить Противник, но не попадает.'


class Rhino(AI_player):

    # Основные параметра Носорога

    def __init__(self, name, Game, team, teambonus):
        AI_player.__init__(self, name, Game, team)
        self.abilities = [special_abilities.Impaler, Stun, Leader]
        self.teambonus = teambonus
        self.maxhp = 4 + teambonus
        self.hp = 4 + teambonus
        self.maxenergy = 2 + int(teambonus/2)
        self.energy = 2 + int(teambonus/2)
        self.bonusdamage += teambonus
        self.weapon = horn
        self.armor = teambonus + 1
        self.armorchance = 60
        self.final = False
        self.highest_damagedealer = None
        self.highest_damage = 0
        self.lasthploss = None
        self.circlecd = 0
        self.trumpcd = 0

        self.hypnosysresist = 70

    # Определение хода Носорога

    def get_target(self):
        if self.highest_damagedealer != None and self.highest_damagedealer.Alive:
            target = self.highest_damagedealer
        else:
            target = utils.GetOtherTeam(self).actors[random.randint(0, len(utils.GetOtherTeam(self).actors) - 1)]
        return target

    def get_turn(self, Fight):
        if float(self.hp)<=self.maxhp/2 and self.final is False:
            self.Fight.string.add(u'\U00002757' + "| Кровь заливает глаза "+self.name + '! Он разъярен!')
            self.bonusdamage += self.teambonus - 1
            self.armorchance += 40
            self.accuracy += 2
            self.maxenergy += self.teambonus
            self.final = True
        meleecounter = 0
        for x in utils.GetOtherTeam(self).actors:
            if x.weapon.Melee and x.Inmelee:
                meleecounter += 1
        # Застанен
        if self.Disabled:
            self.turn = 'disabled'
        # Влететь в мили
        elif not self.Inmelee:
            self.target = self.get_target()
            self.turn = 'rhino_tramp' + str(Fight.round)
            self.Inmelee = True
        elif self.energy < 1:
            self.turn = 'rhino_rest' + str(Fight.round)
        # Раскидать милишников
        elif float(meleecounter) >= len(utils.GetOtherTeam(self).actors)/2 and random.randint(1,2) == 1 and self.circlecd < 1:
            self.turn = 'rhino_circle' + str(Fight.round)
        # Отомстить за удар
        else:
            self.target = self.get_target()
            if not self.target.weapon.Melee and self.trumpcd < 1 or not self.target.Inmelee and self.trumpcd < 1:
                self.turn = 'rhino_tramp' + str(Fight.round)
            elif self.target.Disabled:
                self.turn = 'rhino_stomp' + str(Fight.round)
            else: self.turn = 'attack' + str(Fight.round)

    # Навыки Носорога

    def rest(self):
        self.energy = self.maxenergy
        return u'\U0001F624' + "|" + self.name \
               + ' шумно раздувает ноздри, готовясь атаковать. Энергия полностью восстановлена.'

    def tramp(self):
        damage = self.bonusdamage*random.randint(2,3)
        self.target.damagetaken += damage
        self.energy -= 1
        if random.randint(1,3)!=3:
            self.target.stuncounter += 2
            self.trumpcd = 4
            return u'\U0001F300' + "|" + self.name + ' атакует ' + self.target.name + ' с разбега, сбивая с ног. ' \
                + self.target.name + ' оглушен(а). Нанесено ' + str(damage) + ' урона!'
        else:
            self.trumpcd = 4
            return u'\U0001F4A2' + "|" + self.name + ' атакует ' + self.target.name + ' с разбега, сбивая с ног. ' \
                    ' Нанесено ' + str(damage) + ' урона!'

    def stomp(self):
        damage = self.bonusdamage * random.randint(2, 3) + 3
        self.target.damagetaken += damage
        self.energy -= 1
        return u'\U0001F4A2' + "|" + self.name + ' топчет лежащего на земле ' + self.target.name + ' !' \
               + ' Нанесено ' + str(damage) + ' урона!'

    def poisoned(self):
        return u'\U0001F300' + "|" + self.name + ' вдыхает ядовитый газ. Энергия обнулена!'

    def circle(self):
        damage = self.bonusdamage*random.randint(1,2)
        self.energy -= 1
        self.circlecd = 3
        for x in utils.GetOtherTeam(self).actors:
            if x.weapon.Melee and x.Inmelee:
                x.damagetaken += damage
                x.Inmelee = False
        self.Inmelee = False
        return u'\U0001F4A5' + "|" + self.name + ' отбрасывает всех противников, подошедших к нему вплотную, и наносит им ' \
               + str(damage) + ' урона!'


    # Определение хода Носорога

    def aiaction1q(self, Fight):
        if self.turn == 'rhino_rest' + str(Fight.round) or self.turn == 'rhino_poisoned' + str(Fight.round):
            self.armor = 0
        else:
            self.armor = self.teambonus+1

    def aiaction2q(self, Fight):
        if self.turn == 'rhino_poisoned' + str(Fight.round):
            Fight.string.add(self.poisoned())
        elif self.turn == 'rhino_tramp' + str(Fight.round):
            Fight.string.add(self.tramp())
        elif self.turn == 'rhino_stomp' + str(Fight.round):
            if self.target.Disabled:
                Fight.string.add(self.stomp())
            else:
                self.attack(self.target)
        elif self.turn == 'rhino_circle' + str(Fight.round):
            Fight.string.add(self.circle())

        elif self.turn == 'rhino_rest' + str(Fight.round):
            Fight.string.add(self.rest())

    def aiactionend(self, Fight):
        if self.circlecd > 0:
            self.circlecd -= 1
        if self.trumpcd > 0:
            self.trumpcd -= 1

horn = Weapon_list.Weapon(2, 1, 1, 5, 1, True, True, True, 'Рог', '?' + u'\U0001F4A5' + "|" + '1' + u'\U000026A1', standart = False)
horn.desc1 = 'Игрок бьет Противник Рогом.'
horn.desc2 = 'Игрок бьет Противник Рогом.'
horn.desc3 = 'Игрок бьет Противник Рогом.'
horn.desc4 = 'Игрок бьет Противник Рогом, но не попадает.'
horn.desc5 = 'Игрок бьет Противник Рогом, но не попадает.'
horn.desc6 = 'Игрок бьет Противник Рогом, но не попадает.'


class Howl(special_abilities.Ability):
    name = 'Вой'

class Stun(special_abilities.Ability):
    name = 'Откидывание'

class Leader(special_abilities.Ability):
    name = 'Вожак'


