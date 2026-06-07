from __future__ import annotations

from typing import TYPE_CHECKING

from .. import config, prompts, ui
from ..llm import call_llm

if TYPE_CHECKING:
    from ..game_state import GameState


class Storyteller:
    def _say(self, user_msg: str, max_tokens: int = config.MAX_TOKENS_NARRATION) -> str:
        try:
            return call_llm(prompts.storyteller_system(), user_msg, max_tokens=max_tokens)
        except RuntimeError:
            return "(The narrator is silent.)"

    def narrate_intro(self, state: "GameState") -> None:
        text = self._say(prompts.storyteller_intro_prompt([p.name for p in state.players]))
        ui.print_intro(text)
        state.add_to_transcript(
            day=state.day, phase=state.phase, speaker="Storyteller",
            text=text, kind="narration",
        )

    def narrate_night(self, state: "GameState", killed: str | None) -> None:
        text = self._say(prompts.storyteller_night_prompt(killed))
        ui.print_storyteller(text)
        if killed:
            ui.print_death(killed)
        state.add_to_transcript(
            day=state.day, phase=state.phase, speaker="Storyteller",
            text=text, kind="narration",
        )

    def narrate_day_intro(self, state: "GameState") -> None:
        text = self._say(prompts.storyteller_day_intro_prompt(
            state.day, state.alive_names()
        ))
        ui.print_storyteller(text)
        state.add_to_transcript(
            day=state.day, phase=state.phase, speaker="Storyteller",
            text=text, kind="narration",
        )

    def narrate_day_result(
        self, state: "GameState", eliminated: str, votes: dict[str, str]
    ) -> None:
        # Show each vote first
        for voter, target in votes.items():
            ui.print_vote(voter, target)
        text = self._say(prompts.storyteller_day_result_prompt(eliminated, votes))
        ui.print_storyteller(text)
        ui.print_elimination(eliminated)
        state.add_to_transcript(
            day=state.day, phase=state.phase, speaker="Storyteller",
            text=text, kind="narration",
        )

    def narrate_winner(self, state: "GameState", winner: str) -> None:
        roster = [(p.name, p.role, p.is_alive) for p in state.players]
        text = self._say(
            prompts.storyteller_winner_prompt(winner, roster),
            max_tokens=400,
        )
        ui.print_winner(winner)
        ui.print_storyteller(text)
