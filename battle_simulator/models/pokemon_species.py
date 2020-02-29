from django.db import models

from .type import Type


class PokemonSpecies(models.Model):
    name = models.CharField(max_length=16)
    type1 = models.ForeignKey(Type, models.PROTECT)
    type2 = models.ForeignKey(Type, models.PROTECT, blank=True, null=True)

    # Base stats
    hp = models.IntegerField()
    attack = models.IntegerField()
    special_attack = models.IntegerField()
    defense = models.IntegerField()
    special_defense = models.IntegerField()
    speed = models.IntegerField()
