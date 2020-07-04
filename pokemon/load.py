import pokebase as pb
from pokemon.models import Nature, Type, Species, Ability, Move, Pokemon


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
        id = pokemon.id
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
        Species.objects.create(
            id=id,
            name=name,
            type1=type1,
            type2=type2,
            hp=hp,
            attack=attack,
            defense=defense,
            special_attack=special_attack,
            special_defense=special_defense,
            speed=speed
        )


def load_abilities():
    """Load all abilities from Pokemon API into our own DB."""
    for ability in get_all('ability'):
        name = ability.name
        Ability.objects.create(name=name)


def load_moves():
    """Load all moves from Pokemoon API into our own DB."""
    for move in get_all('move'):
        name = move.name
        power = move.power
        if power is None:
            power = 0
        priority = move.priority
        """Accuracy needs to be modified but for now okay because it Null is different from 100. Can be influenced"""
        accuracy = move.accuracy
        if accuracy is None:
            accuracy = 100
        pp = move.pp
        type_ = Type.objects.get(name=move.type.name)
        damage_classes = {'physical': 'PH', 'special': 'SP', 'status': 'ST'}
        damage_class = damage_classes[move.damage_class.name]
        Move.objects.create(name=name, power=power, priority=priority,
                            accuracy=accuracy, pp=pp, type=type_, damage_class=damage_class)

def is_selected(move):
    """Load Pokemon moves based on its learnset"""
    for details in move.version_group_details:
        if details['version_group']['name'] == 'ultra-sun-ultra-moon':
            if details['move_learn_method']['name'] == 'level-up':
                if details['level_learned_at'] < 60:
                    return True
    return False

def load_pokemon():
    """Load unique Pokemon creatures for the battle simulator """
    ability = Ability.objects.first()
    nature = Nature.objects.get(name='quirky')
    for species in Species.objects.all():
        pokemon = Pokemon.objects.create(species=species, ability=ability, nature=nature)
        for move in pb.pokemon(species.name).moves:
            if is_selected(move):
                move_name = move.move.name
                pokemon.moves.add(Move.objects.get(name=move_name))
