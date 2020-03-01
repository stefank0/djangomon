from django.db import models


class Ability(models.Model):
    name = models.CharField(max_length=16)

    class Meta:
        verbose_name_plural = 'abilities'

    def __str__(self):
        return self.name
