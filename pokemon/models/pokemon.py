from math import floor
import random

from django.db import models

from .nature import Nature
from .ability import Ability
from .species import Species
from .move import Move
from pokemon.ai import select_move


class Pokemon(models.Model):
    species = models.ForeignKey(Species, models.PROTECT)
    level = models.IntegerField(default=50)
    nature = models.ForeignKey(Nature, models.PROTECT)
    ability = models.ForeignKey(Ability, models.PROTECT)
    moves = models.ManyToManyField(Move)
    cache = models.JSONField(default=dict, blank=True)

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

    def first(self, move, opponent, opponent_move):
        """Returns the Pokemon that moves first or None if it is random."""
        if move.priority > opponent_move.priority:
            return self
        elif opponent_move.priority > move.priority:
            return opponent
        else:
            if self.speed > opponent.speed:
                return self
            elif opponent.speed > self.speed:
                return opponent
            else:
                return None

    def use_move(self, move, opponent):
        """Use a move against another Pokemon."""
        damage = move.damage(self, opponent)
        damage_dealt = min(opponent.current_hp, damage)
        opponent.current_hp -= damage_dealt
        self.current_hp -= min(move.recoil_damage(damage_dealt), self.current_hp)
        self.current_hp += min(move.drain_recovery(damage_dealt), self.hp - self.current_hp)
        return (f'{self} uses {move} with {damage} {move.damage_class} damage.\n'
            f'HP left: {self} ({self.current_hp}) and {opponent} ({opponent.current_hp}).\n')

    def _finish_battle(self, winner, loser, battle_report):
        hp_left = (winner.current_hp / winner.hp) * 100.0
        battle_report += f'{winner} wins with {hp_left:.2f}% HP left.\n'
        return winner, battle_report

    def battle(self, opponent):
        """Battle with another Pokemon. The winner is returned."""
        battle_report = f'{self} vs {opponent}\n'
        for pokemon in [self, opponent]:
            pokemon.current_hp = pokemon.hp     # Initialize with full HP
        while True:
            # Select moves:
            move = select_move(self, opponent)
            opponent_move = select_move(opponent, self)
            # Determine move order:
            first = self.first(move, opponent, opponent_move)
            first = first if (first is not None) else random.choice((self, opponent))
            move_order = ((self, move, opponent), (opponent, opponent_move, self))
            move_order = move_order if (first is self) else reversed(move_order)
            # Execute the moves:
            for attacker, move, defender in move_order:
                battle_report += attacker.use_move(move, defender)
                if defender.current_hp == 0:
                    return self._finish_battle(attacker, defender, battle_report)
                elif attacker.current_hp == 0:
                    return self._finish_battle(defender, attacker, battle_report)
