from django.db import models

from .type import Type


class Move(models.Model):
    name = models.CharField(max_length=16)
    power = models.IntegerField()
    priority = models.IntegerField()
    pp = models.IntegerField()
    accuracy = models.FloatField()
    type = models.ForeignKey(Type, models.PROTECT)
    # stat_changes

    class DamageClass(models.TextChoices):
        PHYSICAL = 'PH', 'Physical'
        SPECIAL = 'SP', 'Special'
        STATUS = 'ST', 'Status'

    damage_class = models.CharField(max_length=2, choices=DamageClass.choices)

    def __str__(self):
        return self.name

    def stab(self, attacker):
        """Same type attack bonus (STAB)."""
        types = [attacker.species.type1, attacker.species.type2]
        return 1.5 if (self.type in types) else 1.0

    def damage(self, attacker, defender):
        stab = self.stab(attacker)
        effectiveness = defender.species.effectiveness(self.type)
