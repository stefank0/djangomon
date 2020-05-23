from django.db import models

from .pokemon import Pokemon


class BattleLog(models.Model):
    winner = models.ForeignKey(Pokemon, models.CASCADE, related_name='wins')
    loser = models.ForeignKey(Pokemon, models.CASCADE, related_name='losses')
    report = models.TextField()
