from django.db import models


class Type(models.Model):
    name = models.CharField(max_length=16)

    def __str__(self):
        return self.name

    def effectiveness(self, other):
        """Effectiveness when attacking another Type."""
        return 1.0
