from django.contrib import admin
from .models import Ability, Move, Nature, Pokemon, PokemonSpecies, Type

# Register your models here.
admin.site.register((Ability, Move, Nature, Pokemon, PokemonSpecies, Type))
