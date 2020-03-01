from django.db import models
from django.utils.functional import cached_property


class Type(models.Model):
    name = models.CharField(max_length=16)
    weaknesses = models.ManyToManyField('self', symmetrical=False, related_name='strong_against', blank=True)
    resistances = models.ManyToManyField('self', symmetrical=False, related_name='weak_against', blank=True)
    immunities = models.ManyToManyField('self', symmetrical=False, related_name='no_effect_against', blank=True)

    def __str__(self):
        return self.name

    @cached_property
    def _effectiveness_dict(self):
        """Cache to avoid many database queries."""
        factors = {'strong_against': 2.0, 'weak_against': 0.5, 'no_effect_against': 0.0}
        return {
            type: factor
            for attribute, factor in factors.items()
            for type in getattr(self, attribute).all()
        }

    def effectiveness(self, other):
        """Effectiveness when attacking another Type."""
        return self._effectiveness_dict.get(other, 1.0)
