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
