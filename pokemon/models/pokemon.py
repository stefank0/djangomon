from math import floor
import random

from django.db import models

from .nature import Nature
from .ability import Ability
from .species import Species
from .move import Move


class Pokemon(models.Model):
    species = models.ForeignKey(Species, models.PROTECT)
    level = models.IntegerField(default=50)
    nature = models.ForeignKey(Nature, models.PROTECT)
    ability = models.ForeignKey(Ability, models.PROTECT)
    moves = models.ManyToManyField(Move)

    # IV's
    iv_hp = models.IntegerField(default=15)
    iv_attack = models.IntegerField(default=15)
    iv_special_attack = models.IntegerField(default=15)
    iv_defense = models.IntegerField(default=15)
    iv_special_defense = models.IntegerField(default=15)
    iv_speed = models.IntegerField(default=15)

    # EV's
    ev_hp = models.IntegerField(default=20)
    ev_attack = models.IntegerField(default=20)
    ev_special_attack = models.IntegerField(default=20)
    ev_defense = models.IntegerField(default=20)
    ev_special_defense = models.IntegerField(default=20)
    ev_speed = models.IntegerField(default=20)

    class Meta:
        verbose_name_plural = 'pokemon'

    def __str__(self):
        return self.species.name

    def _stat(self, stat_name):
        iv = getattr(self, 'iv_' + stat_name)
        ev = getattr(self, 'ev_' + stat_name)
        base_stat = getattr(self.species, stat_name)
        stat = (((2*base_stat + iv + ev//4) * self.level) // 100) + 5
        return floor(stat * self.nature.modifier(stat_name))

    @property
    def hp(self):
        return self._stat('hp') + 5 + self.level

    @property
    def attack(self):
        return self._stat('attack')

    @property
    def special_attack(self):
        return self._stat('special_attack')

    @property
    def defense(self):
        return self._stat('defense')

    @property
    def special_defense(self):
        return self._stat('special_defense')

    @property
    def speed(self):
        return self._stat('speed')

    def pick_move(self, other):
        """Pick the best move against another Pokemon."""
        return max(
            self.moves.all(),
            key=lambda move: move.damage_expected(self, other)
        )

    @staticmethod
    def _move_order(pokemon1, move1, pokemon2, move2):
        """The order in which the moves are performed."""
        order1 = ((pokemon1, move1, pokemon2), (pokemon2, move2, pokemon1))
        order2 = reversed(order1)
        if move1.priority > move2.priority:
            return order1
        elif move2.priority > move1.priority:
            return order2
        else:
            if pokemon1.speed > pokemon2.speed:
                return order1
            elif pokemon2.speed > pokemon1.speed:
                return order2
            else:
                return random.choice((order1, order2))

    def use_move(self, move, other, battle_report):
        """Use a move against another Pokemon."""
        damage = move.damage(self, other)
        other.current_hp = max(other.current_hp - damage, 0)
        battle_report += f'{self} uses {move} with {damage} {move.damage_class} damage.\n'
        battle_report += f'HP left: {self} ({self.current_hp}) and {other} ({other.current_hp}).\n'

    def battle(self, other):
        """Battle with another Pokemon. The winner is returned."""
        self.current_hp = self.hp
        other.current_hp = other.hp
        battle_report = f'{self} vs {other}\n'
        while True:
            move_self = self.pick_move(other)
            move_other = other.pick_move(self)
            for attacker, move, defender in self._move_order(self, move_self, other, move_other):
                attacker.use_move(move, defender, battle_report)
                if defender.current_hp == 0:
                    hp_left = (attacker.current_hp / attacker.hp) * 100.0
                    battle_report += f'{attacker} wins with {hp_left:.2f}% HP left.\n'
                    return attacker, battle_report
