def select_move(pokemon, opponent):
    """Select a move for a Pokemon when facing a certain opponent."""
    return max(
        pokemon.moves.all(),
        key=lambda move: move.expected_damage(pokemon, opponent)
    )
