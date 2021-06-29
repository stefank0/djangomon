import math
import random

from django.db import models

from .type import Type


class Move(models.Model):
    name = models.CharField(max_length=16)
    power = models.IntegerField()
    priority = models.IntegerField()
    pp = models.IntegerField()
    accuracy = models.IntegerField()
    type = models.ForeignKey(Type, models.PROTECT)
    drain = models.IntegerField()
    recoil = models.IntegerField()
    nerf_factor = models.FloatField(default=1.0)
    is_noteworthy = models.BooleanField(default=False)

    class DamageClass(models.TextChoices):
        PHYSICAL = 'PH', 'Physical'
        SPECIAL = 'SP', 'Special'
        STATUS = 'ST', 'Status'

    damage_class = models.CharField(max_length=2, choices=DamageClass.choices)

    def __str__(self):
        return self.name

    def _stab(self, attacker, damage):
        """Apply same type attack bonus (STAB) to the damage."""
        types = [attacker.species.type1, attacker.species.type2]
        return (3 * damage) // 2 if (self.type in types) else damage

    def _effectiveness(self, defender, damage):
        """Apply type effectiveness to the damage."""
        effectiveness = defender.species.effectiveness(self.type)
        return math.floor(effectiveness * damage)

    def _apply_type(self, attacker, defender, damage):
        """Apply type bonusses to the damage."""
        return self._effectiveness(defender, self._stab(attacker, damage))

    def _damage_value(self, attacker, defender):
        """Damage when the attacker hits the defender."""
        if self.damage_class == 'PH':
            attack_stat = attacker.attack
            defense_stat = defender.defense
        else:
            attack_stat = attacker.special_attack
            defense_stat = defender.special_defense
        level_factor = (2 * attacker.level) // 5 + 2
        power = round(self.nerf_factor * self.power)
        if power == 0:
            return 0
        damage = (level_factor * power * attack_stat // defense_stat) // 50 + 2
        return damage if damage > 0 else 1

    def max_damage(self, attacker, defender):
        """Maximum value of the damage."""
        damage = self._damage_value(attacker, defender)
        return self._apply_type(attacker, defender, damage)

    def true_damage(self, attacker, defender, random_number):
        """Damage when incorporating the random number from [85, 100]."""
        damage = self._damage_value(attacker, defender)
        damage = damage * random_number // 100
        return self._apply_type(attacker, defender, damage)

    def expected_damage(self, attacker, defender):
        """Expectation value of the damage."""
        return 0.000625 * self.accuracy * sum(
            self.true_damage(attacker, defender, i) for i in range(85, 101)
        )

    def recoil_damage(self, damage):
        """Recoil damage to the attacker when damage is done."""
        return damage * self.recoil // 100

    def drain_recovery(self, damage):
        """HP healed by draining HP of the defender."""
        return damage * self.drain // 100

    def damage(self, attacker, defender):
        """Actual damage when used by an attacker against a defender."""
        if random.random() * 100 < self.accuracy:
            random_number = random.randrange(85, 101)
            return self.true_damage(attacker, defender, random_number)
        else:
            return 0
