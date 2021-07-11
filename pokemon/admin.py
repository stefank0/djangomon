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
class AbilityAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Pokemon)
class PokemonAdmin(admin.ModelAdmin):
    search_fields = ['species__name']
    autocomplete_fields = ['moves', 'ability', 'species']
    exclude = ['cache']
    list_display = ['species', 'win_percentage', 'noteworthy', 'evolutions', 'used_moves']
    list_select_related = ['species']

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-cache__win_percentage')

    def _get_cached(self, pokemon, attribute):
        if attribute not in pokemon.cache:
            method = getattr(self, f'_get_{attribute}')
            pokemon.cache[attribute] = method(pokemon)
            pokemon.save()
        return pokemon.cache[attribute]

    def _get_win_percentage(self, pokemon):
        wins = pokemon.wins.count()
        losses = pokemon.losses.count()
        if wins == 0 and losses == 0:
            return 0
        else:
            return round(wins / (wins+losses) * 100, 2)

    def win_percentage(self, pokemon):
        return self._get_cached(pokemon, 'win_percentage')

    def _get_noteworthy(self, pokemon):
        return ', '.join(str(m) for m in pokemon.moves.filter(is_noteworthy=True))

    def noteworthy(self, pokemon):
        return self._get_cached(pokemon, 'noteworthy')

    def _get_evolutions(self, pokemon):
        evolutions = Species.objects.filter(evolves_from=pokemon.species)
        return ', '.join(str(s) for s in evolutions)

    def evolutions(self, pokemon):
        return self._get_cached(pokemon, 'evolutions')

    def _get_used_moves(self, pokemon):
        moves = []
        for log in BattleLog.objects.filter(Q(winner=pokemon) | Q(loser=pokemon)):
            moves += [s.split(' ')[0] for s in log.report.split(f'\n{pokemon} uses ')[1:]]
        return ', '.join(f'{move}: {count}' for move, count in Counter(moves).most_common())

    def used_moves(self, pokemon):
        return self._get_cached(pokemon, 'used_moves')
