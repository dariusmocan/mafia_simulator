from __future__ import annotations

import random
import sys

from . import config, ui
from .agents.crewmate import Crewmate
from .agents.detective import Detective
from .agents.doctor import Doctor
from .agents.mafia import Mafia
from .agents.storyteller import Storyteller
from .game_engine import run_game
from .game_state import GameState


ROLE_TO_CLASS = {
    "mafia": Mafia,
    "detective": Detective,
    "doctor": Doctor,
    "crewmate": Crewmate,
}


def build_players() -> list:
    """Assign shuffled roles to fixed names; return agent instances."""
    roles = list(config.ROLES)
    random.shuffle(roles)
    assignments = list(zip(config.PLAYER_NAMES, roles))
    all_names = list(config.PLAYER_NAMES)

    players = []
    for name, role in assignments:
        cls = ROLE_TO_CLASS[role]
        players.append(cls(name=name, all_player_names=all_names))

    # Wire up mafia partners
    mafia_players = [p for p in players if p.role == "mafia"]
    if len(mafia_players) == 2:
        mafia_players[0].partner_name = mafia_players[1].name
        mafia_players[1].partner_name = mafia_players[0].name
    elif len(mafia_players) == 1:
        mafia_players[0].partner_name = mafia_players[0].name
    return players


def main() -> int:
    try:
        ui.assign_player_colors(list(config.PLAYER_NAMES))
        players = build_players()
        assignments_line = "Role assignments: " + ", ".join(
            f"{p.name} = {p.role}" for p in players
        )
        ui.print_intro(assignments_line)
        state = GameState(players=players, day=1, phase="night")
        storyteller = Storyteller()
        winner = run_game(state, storyteller)
        ui.print_storyteller(f"Game over. Winner: {winner}.")
        return 0
    except KeyboardInterrupt:
        ui.print_warning("Game interrupted by user.")
        return 130
    except Exception as e:
        ui.print_warning(f"Unhandled error: {e!r}")
        raise


if __name__ == "__main__":
    sys.exit(main())
