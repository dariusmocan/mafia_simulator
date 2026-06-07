from __future__ import annotations

import random
from typing import TYPE_CHECKING

from .. import config, prompts
from ..llm import call_llm
from .base_agent import BaseAgent
from .mafia import _extract_name

if TYPE_CHECKING:
    from ..game_state import GameState


class Doctor(BaseAgent):
    role = "doctor"

    def system_prompt(self) -> str:
        return prompts.doctor_system(self.name)

    def night_save_choice(self, state: "GameState") -> str:
        alive_names = state.alive_names()  # doctor may save self
        if not alive_names:
            return self.name
        msg = prompts.night_save_user_prompt(alive_names, self.name)
        for _attempt in range(2):
            try:
                raw = call_llm(self.system_prompt(), msg, max_tokens=config.MAX_TOKENS_DECISION)
            except RuntimeError:
                break
            chosen = _extract_name(raw, alive_names)
            if chosen:
                return chosen
            msg = (
                f"Your previous answer was not one of: {', '.join(alive_names)}. "
                f"Reply with ONLY one of those names."
            )
        return random.choice(alive_names)
