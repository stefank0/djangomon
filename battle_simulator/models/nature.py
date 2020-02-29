from django.db import models


class Nature(models.Model):
    name = models.CharField(max_length=16)
