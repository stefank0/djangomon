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

    def damage_expected(self, attacker, defender):
        """Expectation value of the damage."""
        return self.damage_value(attacker, defender) * self.accuracy

    def damage_value(self, attacker, defender):
        """Damage when the attacker hits the defender."""
        if self.damage_class == 'Physical':
            stat_factor = attacker.attack / defender.defense
        else:
            stat_factor = attacker.special_attack / defender.special_defense
        level_factor = 2.0 * attacker.level / 5.0 + 2.0
        base_damage = (self.power * level_factor * stat_factor) / 50.0 + 2.0
        stab = self.stab(attacker)
        effectiveness = defender.species.effectiveness(self.type)
        return base_damage * stab * effectiveness

    def damage(self, attacker, defender):
        """Actual damage when used by an attacker against a defender."""
        return self.damage_value(attacker, defender)                            # TODO: Use accuracy and randomness.
