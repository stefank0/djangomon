import pokebase as pb
from pokemon.models import Nature, Type, Species, Ability, Move, Pokemon


def get_all(attr, max_id=None):
    """Generator: retrieve all objects of Pokemon API."""
    i = 1
    while True:
        try:
            print(i)
            yield getattr(pb, attr)(i)
        except:
            return
        if max_id and i >= max_id:
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
            other_name = other_type.name
            other_instance, _created = Type.objects.get_or_create(name=other_name)
            instance.weaknesses.add(other_instance)
        for other_type in type_.damage_relations.half_damage_from:
            other_name = other_type.name
            other_instance, _created = Type.objects.get_or_create(name=other_name)
            instance.resistances.add(other_instance)
        for other_type in type_.damage_relations.no_damage_from:
            other_name = other_type.name
            other_instance, _created = Type.objects.get_or_create(name=other_name)
            instance.immunities.add(other_instance)


def _get_base_stat(stats, name):
    """Get the correct base stat from the Pokemon API stats list."""
    return next(stat.base_stat for stat in stats if stat.stat.name == name)


def load_species():
    """Load all species from Pokemon API into the our own DB."""
    max_id = 386    # up to 3rd gen only
    for pokemon in get_all('pokemon', max_id=max_id):
        id_ = pokemon.id
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
            id=id_,
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
    for pokemon in get_all('pokemon', max_id=max_id):
        evolves_from = pokemon.species.evolves_from_species
        if evolves_from:
            try:
                species = Species.objects.get(name=pokemon.name)
                species.evolves_from = Species.objects.get(name=evolves_from.name)
                species.save()
            except Species.DoesNotExist:
                print(f'DoesNotExist: {pokemon.name}, {evolves_from.name}')


def load_abilities():
    """Load all abilities from Pokemon API into our own DB."""
    for ability in get_all('ability'):
        name = ability.name
        Ability.objects.create(name=name)


def _is_noteworthy(move):
    if move.name in [
        'toxic-spikes',
        'spikes',
        'stealth-rock',
        'sunny-day',
        'rain-dance',
        'rest',
        'healing-wish',
        'wish',
        'heal-bell',
        'aromatherapy',
        'mirror-coat',
        'counter',
        'rapid-spin',
        'defog',
        'substitute',
        'u-turn',
        'volt-switch',
        'baton-pass',
        'shell-smash',
        'hidden-power',
        'protect',
        'detect'
    ]:
        return True
    accuracy = move.accuracy if move.accuracy else 100
    power = move.power if move.power else 0
    if move.stat_changes:
        scores = {
            'attack': 2,
            'special-attack': 2,
            'speed': 1,
            'defense': 1,
            'special-defense': 1,
            'hp': 1,
            'accuracy': 1,
            'evasion': 1
        }
        score = sum(
            stat_change.change * scores[stat_change.stat.name]
            for stat_change in move.stat_changes
        )
        score += power / 40
        effect_chance = move.effect_chance if move.effect_chance else 100
        chance = effect_chance * accuracy / 100
        if (score * chance / 100 >= 3) and (move.name != 'swagger'):
            return True
    meta = move.meta
    if meta is None:
        return False
    if meta.healing and meta.healing >= 50:
        return True
    if meta.flinch_chance and meta.flinch_chance >= 75:
        return True
    ailments = [
        'paralysis',
        'freeze',
        'sleep',
        'burn',
        'poison',
        'leech-seed',
        'ingrain'
    ]
    if meta.ailment.name in ailments:
        ailment_chance = meta.ailment_chance if meta.ailment_chance else 100
        chance = ailment_chance * accuracy / 100
        if (chance >= 75) or (chance >= 30 and power >= 80):
            return True
        if (chance >= 60) and meta.ailment.name in ['freeze', 'sleep']:
            return True
    return False


def load_moves():
    """Load all moves from Pokemon API into our own DB."""
    for move in get_all('move'):
        power = move.power if move.power else 0
        accuracy = move.accuracy if move.accuracy else 100
        pp = move.pp if move.pp else 5
        type_ = Type.objects.get(name=move.type.name)
        damage_classes = {
            'physical': Move.DamageClass.PHYSICAL,
            'special': Move.DamageClass.SPECIAL,
            'status': Move.DamageClass.STATUS
        }
        if move.damage_class:
            damage_class = damage_classes[move.damage_class.name]
        else:
            damage_class = Move.DamageClass.STATUS
        drain = max(move.meta.drain, 0) if move.meta else 0
        recoil = max(-move.meta.drain, 0) if move.meta else 0
        is_noteworthy = _is_noteworthy(move)
        Move.objects.create(
            name=move.name,
            power=power,
            priority=move.priority,
            accuracy=accuracy,
            pp=pp,
            type=type_,
            damage_class=damage_class,
            drain=drain,
            recoil=recoil,
            is_noteworthy=is_noteworthy
        )


def is_selected(move):
    """Load Pokemon moves based on its learn set"""
    for details in move.version_group_details:
        if details.version_group.name == 'black-white':
            if details.move_learn_method.name == 'level-up':
                # if details.level_learned_at < 60:
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


def _pre_evolution_moves(pokemon):
    evolves_from = pokemon.species.evolves_from
    if evolves_from:
        pokemon = Pokemon.objects.get(species=evolves_from)
        pre_evolution_moves = _pre_evolution_moves(pokemon)
        return list(pokemon.moves.all()) + pre_evolution_moves
    else:
        return []


def apply_corrections():
    struggle = Move.objects.get(name='struggle')
    for pokemon in Pokemon.objects.all():
        pokemon.moves.add(struggle)  # Avoids problems with 0 damage moves.
    for move in Move.objects.filter(name__in=['explosion', 'self-destruct']):
        move.recoil = 10000  # Probably kills the Pokemon using the move.
        move.save()
    nerf_factors = {
        'dream-eater': 0.0,
        'fake-out': 0.0,
        'synchronoise': 0.0,
        'focus-punch': 0.0,
        'struggle': 0.2,
        'last-resort': 0.33,
        'future-sight': 0.5,
        'skull-bash': 0.5,
        'sky-attack': 0.5,
        'solar-beam': 0.5,
        'razor-wind': 0.5,
        'blast-burn': 0.66,
        'frenzy-plant': 0.66,
        'hydro-cannon': 0.66,
        'rock-wrecker': 0.66,
        'roar-of-time': 0.66,
        'giga-impact': 0.66,
        'hyper-beam': 0.66,
        'water-spout': 0.75,
        'eruption': 0.75,
        'overheat': 0.75,
        'draco-meteor': 0.75,
        'leaf-storm': 0.75,
        'superpower': 0.875,
        'close-combat': 0.875
    }
    for move in Move.objects.filter(name__in=nerf_factors.keys()):
        move.nerf_factor = nerf_factors[move.name]
        move.save()
    for pokemon in Pokemon.objects.all():
        moves = pokemon.moves.all()
        for move in _pre_evolution_moves(pokemon):
            if move not in moves:
                pokemon.moves.add(move)


def load_all():
    """Load all the data at once."""
    load_natures()
    load_types()
    load_abilities()
    load_moves()
    load_species()
    load_pokemon()
    apply_corrections()
