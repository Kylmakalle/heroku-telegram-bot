import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# import ../db.py
import special_abilities


class Sturdy(special_abilities.Ability):
    name ="Двужильность"
    info = 'Увеличивает максимум жизней на 1. Вы получаете устойчивость к кровотечению.'
    RangeOnly = False
    MeleeOnly = False
    TeamOnly = False
    def aquare(self, user):
        user.maxhp += 1
        user.hp += 1

special_abilities.abilities.append(Sturdy)