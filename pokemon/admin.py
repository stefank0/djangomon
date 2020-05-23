from django.contrib import admin
from django.db.models import Count

from .models import Ability, Move, Nature, Pokemon, Species, Type, BattleLog

# Register your models here.
admin.site.register((Nature, Type))


@admin.register(BattleLog)
class BattleLogAdmin(admin.ModelAdmin):
    search_fields = ['winner__species__name', 'loser__species__name']
    list_filter = ['winner', 'loser']
    list_display = ['id', 'winner', 'loser']


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
    list_display = ['species', 'win_percentage']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(wins_count=Count('wins')).order_by('-wins_count')

    def win_percentage(self, pokemon):
        wins = pokemon.wins.count()
        losses = pokemon.losses.count()
        if wins == 0 and losses == 0:
            return 0
        else:
            return round(wins / (wins+losses) * 100, 2)
