from django.contrib import admin
from .models import Ability, Move, Nature, Pokemon, Species, Type

# Register your models here.
admin.site.register((Nature, Type))


@admin.register(Move)
class MoveAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Ability)
class PokemonAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Species)
class PokemonAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Pokemon)
class PokemonAdmin(admin.ModelAdmin):
    search_fields = ['species__name']
    autocomplete_fields = ['moves', 'ability', 'species']
