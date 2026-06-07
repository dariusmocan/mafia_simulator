from __future__ import annotations

import random
from typing import TYPE_CHECKING

from .. import config, prompts
from ..llm import call_llm
from .base_agent import BaseAgent
from .mafia import _extract_name

if TYPE_CHECKING:
    from ..game_state import GameState


class Detective(BaseAgent):
    role = "detective"

    def __init__(self, name: str, all_player_names: list[str]):
        super().__init__(name, all_player_names)
        self.investigation_log: dict[str, str] = {}  # name -> "mafia"|"crewmate"|"doctor"|"detective"

    def system_prompt(self) -> str:
        return prompts.detective_system(self.name, self.investigation_log)

    def night_investigate(self, state: "GameState") -> str:
        alive_names = state.alive_names()
        valid = [n for n in alive_names if n != self.name]
        if not valid:
            return self.name
        msg = prompts.night_investigate_user_prompt(
            alive_names, self.name, list(self.investigation_log.keys())
        )
        for _attempt in range(2):
            try:
                raw = call_llm(self.system_prompt(), msg, max_tokens=config.MAX_TOKENS_DECISION)
            except RuntimeError:
                break
            chosen = _extract_name(raw, valid)
            if chosen:
                return chosen
            msg = (
                f"Your previous answer was not one of: {', '.join(valid)}. "
                f"Reply with ONLY one of those names."
            )
        return random.choice(valid)
