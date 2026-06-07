from __future__ import annotations

import random
from collections import Counter
from typing import TYPE_CHECKING

from . import ui

if TYPE_CHECKING:
    from .agents.storyteller import Storyteller
    from .game_state import GameState


def check_winner(state: "GameState") -> str | None:
    """Returns 'mafia', 'innocents', or None."""
    mafia = state.alive_mafia()
    innocents = state.alive_innocents()
    if not mafia:
        return "innocents"
    if len(mafia) > len(innocents):
        return "mafia"
    return None


def tally_votes(votes: dict[str, str]) -> str:
    """Plurality vote. Ties broken randomly among the tied names."""
    counts = Counter(votes.values())
    if not counts:
        raise ValueError("No votes to tally.")
    top_count = max(counts.values())
    tied = [name for name, c in counts.items() if c == top_count]
    return random.choice(tied)


def _mafia_team_choose_kill(state: "GameState") -> str:
    """The first living mafia decides for the team."""
    living_mafia = state.alive_mafia()
    if not living_mafia:
        return ""  # caller should not invoke when no mafia alive
    return living_mafia[0].night_kill_choice(state) 


def run_game(state: "GameState", storyteller: "Storyteller") -> str:
    """Run the game to completion. Returns the winner ('mafia' or 'innocents')."""
    storyteller.narrate_intro(state)

    while True:
        # ---------------- NIGHT ----------------
        state.phase = "night"
        ui.print_phase_header(state.day, "night")

        kill_target = _mafia_team_choose_kill(state)

        # Doctor
        doctor = next(
            (p for p in state.alive() if p.role == "doctor"),
            None,
        )
        save_target = doctor.night_save_choice(state) if doctor else None  # type: ignore[attr-defined]

        # Detective
        detective = next(
            (p for p in state.alive() if p.role == "detective"),
            None,
        )
        detective_target: str | None = None
        detective_target_role: str | None = None
        if detective:
            detective_target = detective.night_investigate(state)  
            detective_target_role = state.by_name(detective_target).role
            detective.investigation_log[detective_target] = detective_target_role 

        # Resolve
        if kill_target and kill_target != save_target:
            state.by_name(kill_target).is_alive = False
            killed_for_narration: str | None = kill_target
        else:
            killed_for_narration = None

        # mafia insights
        if kill_target:
            ui.print_night_action(f"Mafia targeted {kill_target} for elimination.")    

        # doctor insights
        if doctor and save_target:
            if save_target == kill_target:
                outcome = "succeeded -- the mafia targeted them!"
            else:
                outcome = "failed -- mafia targeted someone else."
            ui.print_night_action(f"Doctor {doctor.name} chose to save {save_target} and {outcome}") 

        # detective insights
        if detective and detective_target:
            ui.print_night_action(
                f"Detective {detective.name} investigated {detective_target}." 
                f" -- learned role: {detective_target_role}",
            )

        storyteller.narrate_night(state, killed_for_narration)

        winner = check_winner(state)
        if winner:
            storyteller.narrate_winner(state, winner)
            return winner

        # ---------------- DAY ----------------
        state.phase = "day"
        ui.print_phase_header(state.day, "day")
        storyteller.narrate_day_intro(state)

        speakers = list(state.alive())
        random.shuffle(speakers)
        for speaker in speakers:
            text = speaker.speak(state)
            state.add_to_transcript(
                day=state.day, phase="day", speaker=speaker.name,
                text=text, kind="speech",
            )
            ui.print_speech(speaker.name, text, role=speaker.role)
            for listener in state.alive():
                if listener is speaker:
                    continue
                listener.update_beliefs(speaker.name, text, state)

        # Vote
        votes = {a.name: a.vote(state) for a in state.alive()}
        eliminated = tally_votes(votes)
        state.by_name(eliminated).is_alive = False
        storyteller.narrate_day_result(state, eliminated, votes)

        winner = check_winner(state)
        if winner:
            storyteller.narrate_winner(state, winner)
            return winner

        state.day += 1
