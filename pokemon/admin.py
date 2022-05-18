from collections import Counter

from django.contrib import admin
from django.db.models import Q
from django.utils.html import format_html

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


class TypeFilter(admin.SimpleListFilter):
    title = 'type'
    parameter_name = 'type'

    def lookups(self, request, model_admin):
        return [(t.name, t.name) for t in Type.objects.order_by('name')]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(
                Q(species__type1__name=value) | Q(species__type2__name=value)
            )


@admin.register(Pokemon)
class PokemonAdmin(admin.ModelAdmin):
    search_fields = ['species__name']
    autocomplete_fields = ['moves', 'ability', 'species']
    exclude = ['cache']
    list_display = ['species', 'serebii', 'win_percentage', 'noteworthy', 'evolutions', 'used_moves', 'attacker', 'defender']
    list_select_related = ['species']
    list_filter = [TypeFilter]

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

    def attacker(self, pokemon):
        attack = pokemon.species.attack
        special_attack = pokemon.species.special_attack
        if attack > 1.5 * special_attack:
            return 'physical'
        elif special_attack > 1.5 * attack:
            return 'special'
        else:
            return ''

    def defender(self, pokemon):
        defense = pokemon.species.defense
        special_defense = pokemon.species.special_defense
        if defense > 1.5 * special_defense:
            return 'physical'
        elif special_defense > 1.5 * defense:
            return 'special'
        else:
            return ''

    def serebii(self, pokemon):
        url = f'https://www.serebii.net/pokedex-bw/{pokemon.species.id}.shtml'
        return format_html('<a href="{}">&raquo;&raquo;</a>', url)
