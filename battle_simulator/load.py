import pokebase as pb
from battle_simulator.models import Nature, Type, Species


def get_all(attr):
    """Generator: retrieve all objects of Pokemon API."""
    i = 1
    while True:
        try:
            print(i)
            yield getattr(pb, attr)(i)
        except:
            return
        i += 1


def get_increased_stat(nature):
    """Get increased_stat from Pokemon API for nature."""
    if nature.increased_stat:
        return nature.increased_stat.name.replace('-', '_')
    else:
        return ''


def get_decreased_stat(nature):
    """Get decreased_stat from Pokemon API for nature."""
    if nature.decreased_stat:
        return nature.decreased_stat.name.replace('-', '_')
    else:
        return ''


def load_natures():
    """Load all natures from Pokemon API into the our own DB."""
    for nature in get_all('nature'):
        name = nature.name
        increased_stat = get_increased_stat(nature)
        decreased_stat = get_decreased_stat(nature)
        Nature.objects.create(name=name, increased_stat=increased_stat, decreased_stat=decreased_stat)


def load_types():
    """Load all types from Pokemon API into the our own DB."""
    for type_ in get_all('type_'):
        name = type_.name
        instance, _created = Type.objects.get_or_create(name=name)
        for other_type in type_.damage_relations.double_damage_from:
            other_name = other_type['name']
            other_instance, _created = Type.objects.get_or_create(name=other_name)
            instance.weaknesses.add(other_instance)
        for other_type in type_.damage_relations.half_damage_from:
            other_name = other_type['name']
            other_instance, _created = Type.objects.get_or_create(name=other_name)
            instance.resistances.add(other_instance)
        for other_type in type_.damage_relations.no_damage_from:
            other_name = other_type['name']
            other_instance, _created = Type.objects.get_or_create(name=other_name)
            instance.immunities.add(other_instance)


def load_species():
    """Load all species from Pokemon API into the our own DB."""
    for pokemon in get_all('pokemon'):
        name = pokemon.name
        hp = pokemon.stats[5].base_stat
        attack = pokemon.stats[4].base_stat
        defense = pokemon.stats[3].base_stat
        special_attack = pokemon.stats[2].base_stat
        special_defense = pokemon.stats[1].base_stat
        speed = pokemon.stats[0].base_stat
        assert [stat.stat.name for stat in pokemon.stats] == ['speed', 'special-defense', 'special-attack', 'defense', 'attack', 'hp']
        type1 = Type.objects.get(name=pokemon.types[0].type.name)
        if len(pokemon.types) > 1:
            type2 = Type.objects.get(name=pokemon.types[1].type.name)
        else:
            type2 = None
        Species.objects.create(name=name, type1=type1, type2=type2, hp=hp, attack=attack, defense=defense, special_attack=special_attack, special_defense=special_defense, speed=speed)
