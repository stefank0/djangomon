from math import floor

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

    def battle(self, other):
        """Battle with another Pokemon. The winner is returned."""
        report = 'Generation = Ultra Sun / Ultra Moon \n'
        self.current_hp = self.hp
        other.current_hp = other.hp
        first = max([self, other], key=lambda pokemon: pokemon.speed)
        second = self if (first is other) else other
        report += '{} at {} vs {} at {} \n'.format(first.species.name, first.level, second.species.name, second.level)
        while True:
            move = first.pick_move(second)
            damage = move.damage(first, second)
            report += '{}:{} vs {}:{}, \n'.format(first.species.name, first.current_hp, second.species.name, second.current_hp)
            report += '{} does {}({}) with {} damage \n'.format(first.species.name, move.name, move.damage_class, damage)
            second.current_hp -= damage
            if second.current_hp <= 0:
                report += '{} is a winner with {}% HP left.'.format(first.species.name, round((first.current_hp / first.hp)*100), 2)
                return first, report
            move = second.pick_move(first)
            damage = move.damage(second, first)
            report += '{}:{} vs {}:{}, \n'.format(first.species.name, first.current_hp, second.species.name, second.current_hp)
            report += '{} does {}({}) with {} damage \n'.format(second.species.name, move.name, move.damage_class, damage)
            first.current_hp -= damage
            if first.current_hp <= 0:
                report += '{} is a winner with {}% HP left.'.format(second.species.name, round((second.current_hp / second.hp)*100), 2)
                return second, report
