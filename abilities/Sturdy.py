import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# import ../db.py
import special_abilities


class Sturdy(special_abilities.Ability):
    name ="Двужильность"
    info = 'Увеличивает максимум жизней на 2.'
    RangeOnly = False
    MeleeOnly = False
    TeamOnly = False
    def aquare(self, user):
        user.maxhp += 2
        user.hp += 2

special_abilities.abilities.append(Sturdy)