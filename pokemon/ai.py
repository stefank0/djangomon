from math import isclose


def select_move_naive(pokemon, opponent):
    """Select a move for a Pokemon when facing a certain opponent."""
    return max(
        pokemon.moves.all(),
        key=lambda move: move.expected_damage(pokemon, opponent)
    )


def _moves(pokemon, opponent):
    """Moves that are considered by the AI.

    Notes:
        Only the strongest move within a set of moves with the same accuracy
        and priority needs to be considered.
    """
    partitions = {}
    for move in pokemon.moves.all():
        key = (move.priority, move.accuracy, move.drain, move.recoil)
        partitions.setdefault(key, []).append(move)
    return [
        max(partition, key=lambda move: move.max_damage(pokemon, opponent))
        for partition in partitions.values()
    ]


def _score(pokemon, move, opponent, opponent_moves):
    """Score a move by the minimum win probability."""
    return min(
        win_probability(pokemon, move, opponent, opponent_move)
        for opponent_move in opponent_moves
    )


def select_move(pokemon, opponent):
    """Select a move for a Pokemon when facing a certain opponent (minimax)."""
    moves = _moves(pokemon, opponent)
    opponent_moves = _moves(opponent, pokemon)
    scores = [_score(pokemon, move, opponent, opponent_moves) for move in moves]
    return max(
        [move for move, score in zip(moves, scores) if score == max(scores)],
        key=lambda move: move.expected_damage(pokemon, opponent)
    )


def _add_probability(distr, damage, probability):
    """Add probability to the distribution for a certain damage value."""
    distr[damage] = distr.get(damage, 0.0) + probability


def _damage_distribution(pokemon, move, opponent):
    """Probability distribution of the damage of a move."""
    accuracy = 0.01 * move.accuracy   # convert to decimal probability
    distr = {}
    if not isclose(accuracy, 1.0):
        _add_probability(distr, 0, 1.0 - accuracy)
    for random_number in range(85, 101):
        damage = move.true_damage(pokemon, opponent, random_number)
        _add_probability(distr, damage, accuracy / 16.0)
    return distr


def _opponent_recovery(pokemon, move, opponent, opponent_move, turns):
    """Expected recovery for the opponent."""
    expected_damage = round(opponent_move.expected_damage(opponent, pokemon))
    expected_recovery = opponent_move.drain_recovery(expected_damage)
    max_recovery = opponent_move.drain_recovery(pokemon.current_hp)
    if pokemon.first(move, opponent, opponent_move) == opponent:
        turns += 1  # One more turn of recovery before the attack of the pokemon.
    return min(turns * expected_recovery, max_recovery)


def _opponent_hp(pokemon, move, opponent, opponent_move, turns, is_selecting):
    """HP used to calculate the faint probability."""
    hp = opponent.current_hp
    if not is_selecting:  # When selecting a move, do not assume the opponent hurts itself.
        # When considering a move with recoil damage, subtract the full recoil
        # damage, because you need to take this damage in order to win without
        # dying. The case where both pokemon die is ignored, but it is good to
        # discourage recoil damage moves a bit extra.
        if opponent_move.recoil > 0:
            hp -= opponent_move.recoil_damage(pokemon.current_hp)
    if opponent_move.drain > 0:
        hp += _opponent_recovery(pokemon, move, opponent, opponent_move, turns)
    return hp


def _faint_probability(distr, opponent_hp):
    """Probability that the opponent faints given a damage distribution."""
    return sum(
        probability
        for damage, probability in distr.items()
        if damage >= opponent_hp
    )


def _sum_distribution(distr1, distr2):
    """Distribution of the sum of two random variables (convolution)."""
    distr = {}
    for damage1, probability1 in distr1.items():
        for damage2, probability2 in distr2.items():
            damage = damage1 + damage2
            _add_probability(distr, damage, probability1 * probability2)
    return distr


MAX_TURNS = 10
SURVIVAL = 999


def _cumulative_damage_distributions(pokemon, move, opponent):
    """Probability distribution of the cumulative damage for multiple turns."""
    distr = _damage_distribution(pokemon, move, opponent)
    distributions = [distr]
    for i in range(MAX_TURNS - 1):
        distributions.append(_sum_distribution(distr, distributions[-1]))
    return distributions


def _faint_distribution(pokemon, move, opponent, opponent_move, is_selecting):
    """Probability distribution of the turn the opponent faints."""
    distributions = _cumulative_damage_distributions(pokemon, move, opponent)
    cdf = [
        _faint_probability(
            distr,
            _opponent_hp(pokemon, move, opponent, opponent_move, turns, is_selecting)
        )
        for turns, distr in enumerate(distributions)
    ]
    pdf = [
        probability - probability_previous
        for probability, probability_previous in zip(cdf, [0.0] + cdf[:-1])
    ]
    faint_distr = {turn: probability for turn, probability in enumerate(pdf)}
    faint_distr[SURVIVAL] = 1.0 - sum(pdf)   # probability of survival
    return faint_distr


def win_probability(pokemon, move, opponent, opponent_move):
    """Probability that the pokemon wins within the next couple of turns."""
    first = pokemon.first(move, opponent, opponent_move)
    p_win = 0.0
    p_lose = 0.0
    p_undecided = 0.0
    for turn_opponent_faints, p1 in _faint_distribution(pokemon, move, opponent, opponent_move, True).items():
        for turn_pokemon_faints, p2 in _faint_distribution(opponent, opponent_move, pokemon, move, False).items():
            probability = p1 * p2
            if turn_pokemon_faints > turn_opponent_faints:
                p_win += probability
            elif turn_opponent_faints > turn_pokemon_faints:
                p_lose += probability
            elif (turn_opponent_faints == SURVIVAL) and (turn_pokemon_faints == SURVIVAL):
                p_undecided += probability
            else:
                if first is pokemon:
                    p_win += probability
                elif first is opponent:
                    p_lose += probability
                else:
                    p_win += 0.5 * probability
                    p_lose += 0.5 * probability
    return p_win
