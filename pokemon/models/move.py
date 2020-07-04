import math
import random

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

    def stab(self, attacker, damage):
        """Same type attack bonus (STAB)."""
        types = [attacker.species.type1, attacker.species.type2]
        return (3 * damage) // 2 if (self.type in types) else damage

    def damage_expected(self, attacker, defender):
        """Expectation value of the damage."""
        damage = self.stab(attacker, self.damage_value(attacker, defender))
        effectiveness = defender.species.effectiveness(self.type)
        return math.floor(effectiveness * damage * 0.925 * self.accuracy)

    def damage_value(self, attacker, defender):
        """Damage when the attacker hits the defender."""
        if self.damage_class == 'PH':
            attack_stat = attacker.attack
            defense_stat = defender.defense
        else:
            attack_stat = attacker.special_attack
            defense_stat = defender.special_defense
        level_factor = (2 * attacker.level) // 5 + 2
        return (level_factor * self.power * attack_stat // defense_stat) // 50 + 2

    def damage(self, attacker, defender):
        """Actual damage when used by an attacker against a defender."""
        if random.random() * 100 < self.accuracy:
            damage = self.damage_value(attacker, defender)
            damage = damage * random.randrange(85, 101) // 100
            damage = self.stab(attacker, damage)
            effectiveness = defender.species.effectiveness(self.type)
            return math.floor(effectiveness * damage)
        else:
            return 0
