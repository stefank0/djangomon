from pokemon.models import BattleLog
from pokemon.models import Pokemon


def battle():
    """Run the Pokemon battle simulator."""
    pokemons = Pokemon.objects.filter(species__id__lte=386)  # up to 3rd gen only
    for pokemon1 in pokemons:
        for pokemon2 in pokemons:
            if pokemon1 != pokemon2:
                winner, report = pokemon1.battle(pokemon2)
                loser = pokemon1 if winner is pokemon2 else pokemon2
                BattleLog.objects.create(winner=winner, loser=loser, report=report)
