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


def _get_base_stat(stats, name):
    """Get the correct base stat from the Pokemon API stats list."""
    return next(stat.base_stat for stat in stats if stat.stat.name == name)


def load_species():
    """Load all species from Pokemon API into the our own DB."""
    for pokemon in get_all('pokemon'):
        id = pokemon.id
        if id > 386:
            break  # up to 3rd gen only
        name = pokemon.name
        hp = _get_base_stat(pokemon.stats, 'hp')
        attack = _get_base_stat(pokemon.stats, 'attack')
        defense = _get_base_stat(pokemon.stats, 'defense')
        special_attack = _get_base_stat(pokemon.stats, 'special-attack')
        special_defense = _get_base_stat(pokemon.stats, 'special-defense')
        speed = _get_base_stat(pokemon.stats, 'speed')
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
    """Load all moves from Pokemon API into our own DB."""
    for move in get_all('move'):
        power = move.power
        if power is None:
            power = 0
        accuracy = move.accuracy
        if accuracy is None:
            accuracy = 100  # Quick Fix. Moves without accuracy cannot miss at all.
        type_ = Type.objects.get(name=move.type.name)
        damage_classes = {
            'physical': Move.DamageClass.PHYSICAL,
            'special': Move.DamageClass.SPECIAL,
            'status': Move.DamageClass.STATUS
        }
        damage_class = damage_classes[move.damage_class.name]
        drain = max(move.meta.drain, 0)
        recoil = max(-move.meta.drain, 0)
        Move.objects.create(
            name=move.name,
            power=power,
            priority=move.priority,
            accuracy=accuracy,
            pp=move.pp,
            type=type_,
            damage_class=damage_class,
            drain=drain,
            recoil=recoil
        )


def is_selected(move):
    """Load Pokemon moves based on its learnset"""
    for details in move.version_group_details:
        if details['version_group']['name'] == 'black-white':
            if details['move_learn_method']['name'] == 'level-up':
                # if details['level_learned_at'] < 60:
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


def load_all():
    """Load all the data at once."""
    load_natures()
    load_types()
    load_abilities()
    load_moves()
    load_species()
    load_pokemon()
