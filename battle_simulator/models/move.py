from django.db import models

from .type import Type


class Move(models.Model):
    name = models.CharField(max_length=16)
    power = models.IntegerField()
    accuracy = models.FloatField()
    type = models.ForeignKey(Type, models.PROTECT)

    def __str__(self):
        return self.name
