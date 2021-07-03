from collections import Counter

from django.contrib import admin
from django.db.models import Count, Q

from .models import Ability, Move, Nature, Pokemon, Species, Type, BattleLog

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
    list_display = ['species', 'win_percentage', 'noteworthy', 'evolutions', 'used_moves']

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

    def noteworthy(self, pokemon):
        return ', '.join(str(m) for m in pokemon.moves.filter(is_noteworthy=True))

    def evolutions(self, pokemon):
        evolutions = Species.objects.filter(evolves_from=pokemon.species)
        return ', '.join(str(s) for s in evolutions)

    def used_moves(self, pokemon):
        moves = []
        for log in BattleLog.objects.filter(Q(winner=pokemon) | Q(loser=pokemon)):
            moves += [s.split(' ')[0] for s in log.report.split(f'{pokemon} uses ')[1:]]
        return ', '.join(f'{move}: {count}' for move, count in Counter(moves).most_common())
