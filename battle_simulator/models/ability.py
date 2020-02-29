from django.db import models


class Ability(models.Model):
    name = models.CharField(max_length=16)
