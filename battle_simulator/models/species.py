from django.db import models

from .type import Type


class Species(models.Model):
    name = models.CharField(max_length=16)
    type1 = models.ForeignKey(Type, models.PROTECT, related_name='species1')
    type2 = models.ForeignKey(Type, models.PROTECT, related_name='species2', blank=True, null=True)

    # Base stats
    hp = models.IntegerField()
    attack = models.IntegerField()
    special_attack = models.IntegerField()
    defense = models.IntegerField()
    special_defense = models.IntegerField()
    speed = models.IntegerField()

    class Meta:
        verbose_name_plural = 'species'

    def __str__(self):
        return self.name

    def effectiveness(self, type):
        """Effectiveness of a Type against this PokemonSpecies."""
        effectiveness = type.effectiveness(self.type1)
        if self.type2:
            effectiveness *= type.effectiveness(self.type2)
        return effectiveness
