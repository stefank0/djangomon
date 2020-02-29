from math import floor

from django.db import models

from .nature import Nature
from .ability import Ability
from .pokemon_species import PokemonSpecies
from .move import Move


class Pokemon(models.Model):
    species = models.ForeignKey(PokemonSpecies, models.PROTECT)
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
