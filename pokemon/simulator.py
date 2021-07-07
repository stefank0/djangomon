from pokemon.models import BattleLog
from pokemon.models import Pokemon


def battle(resume_pokemon1=None, resume_pokemon2=None):
    """Run the Pokemon battle simulator."""
    skip = resume_pokemon1 and resume_pokemon2
    pokemons = Pokemon.objects.order_by('id')
    for pokemon1 in pokemons:
        for pokemon2 in pokemons:
            if skip:
                if (pokemon1 == resume_pokemon1) and (pokemon2 == resume_pokemon2):
                    skip = False
                else:
                    continue
            if pokemon1 != pokemon2:
                winner, report = pokemon1.battle(pokemon2)
                loser = pokemon1 if winner is pokemon2 else pokemon2
                BattleLog.objects.create(winner=winner, loser=loser, report=report)
                print(report)


def test():
    bulbasaur = Pokemon.objects.get(species__name='bulbasaur')
    ekans = Pokemon.objects.get(species__name='ekans')
    print(bulbasaur.battle(ekans))
