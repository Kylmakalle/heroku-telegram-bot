import special_abilities
import utils
import telebot
import config
import random
import Item_list

types = telebot.types
bot = telebot.TeleBot(config.token)

secret_abilities = []
def check_ability(player):
    for ability in secret_abilities:
        if ability.condition_1 in player.abilities and ability.condition_2 in player.abilities:
            player.abilities.append(ability)
            ability.aquare(ability, player)
            bot.send_message(player.chat_id, 'Вы активируете секретную способность - ' + ability.name)


class Warlock(special_abilities.Ability):

    condition_1 = special_abilities.Necromancer
    condition_2 = special_abilities.Ritual
    name = 'Чернокнижник'
    info = 'Вы получаете 1 хп за каждого умершего.'
    MeleeOnly = False
    RangeOnly = False
    TeamOnly = True

    def aquare(self, user):
        user.deadplayers = []

    def special_first(self, user):
        if user.deadteammates != user.team.deadplayers:
            print('Обнаружены трупы! ')
            deadbodies = len(user.team.deadplayers) + len(utils.get_other_team(user).deadplayers) - len(user.deadplayers)
            user.deadplayers = list(user.team.deadplayers) + list(utils.get_other_team(user).deadplayers)

            while deadbodies != 0:
                user.fight.string.add(u'\U0001F47F' + "|" + 'Чернокнижник ' + user.name + ' получает 1 жизнь.')
                deadbodies -= 1
                user.hp += 1

class Regeneration(special_abilities.Ability):
    condition_1 = special_abilities.Sturdy.Sturdy
    condition_2 = special_abilities.Armorer
    name = 'Регенерация.'
    info = 'У вас есть шанс 33% восстановить 1 жизнь после получения урона.'
    MeleeOnly = False
    RangeOnly = False
    TeamOnly = True

    def special_end(self, user):
        if user.Losthp and random.randint(1,3) == 3:
            user.hp += 1
            user.fight.string.add(u'\U00002757' + "|" + user.name + ' восстанавливает 1 жизнь.')


class Bloodlust(special_abilities.Ability):
    condition_1 = special_abilities.Berserk
    condition_2 = special_abilities.Sadist
    name = 'Кровожадность.'
    info = 'Вы чаще попадаете по противникам, у которых меньше половины жизней.'
    MeleeOnly = False
    RangeOnly = False
    TeamOnly = False

    def special_first(self, user):
        if user.target is not None:
            if user.target.maxhp//user.hp >= 2:
                user.tempaccuracy += 1

secret_abilities.append(Warlock)
secret_abilities.append(Regeneration)
secret_abilities.append(Bloodlust)