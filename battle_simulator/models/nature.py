from django.db import models


class Nature(models.Model):
    name = models.CharField(max_length=16)
    CHOICES = (
        ('attack', 'attack'),
        ('defense', 'defense'),
        ('special_attack', 'special attack'),
        ('special_defense', 'special defense'),
        ('speed', 'speed')
    )
    increased_stat = models.CharField(max_length=16, choices=CHOICES, blank=True)
    decreased_stat = models.CharField(max_length=16, choices=CHOICES, blank=True)

    def __str__(self):
        return self.name

    def modifier(self, stat):
        modifiers = {
            self.increased_stat: 1.1,
            self.decreased_stat: 0.9
        }
        return modifiers.get(stat, 1)
