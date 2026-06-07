from __future__ import annotations

import random
from typing import TYPE_CHECKING

from .. import config, prompts
from ..llm import call_llm
from .base_agent import BaseAgent

if TYPE_CHECKING:
    from ..game_state import GameState


class Mafia(BaseAgent):
    role = "mafia"

    def __init__(self, name: str, all_player_names: list[str]):
        super().__init__(name, all_player_names)
        self.partner_name: str | None = None  # set after instantiation

    def system_prompt(self) -> str:
        partner = self.partner_name or "(unknown)"
        return prompts.mafia_system(self.name, partner)

    def night_kill_choice(self, state: "GameState") -> str:
        """Pick a non-mafia living player to kill. Falls back to random
        valid target if the LLM picks something invalid twice."""
        alive_names = state.alive_names()
        valid = [
            p.name for p in state.alive()
            if p.role != "mafia"
        ]
        if not valid:
            # Should never happen — game would already be over.
            return random.choice([n for n in alive_names if n != self.name])

        msg = prompts.night_kill_user_prompt(alive_names, self.partner_name or self.name)
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


def _extract_name(text: str, valid_names: list[str]) -> str | None:
    """Find the first valid name appearing as a whole word in text."""
    lowered = text.lower()
    # Prefer exact match on a stripped line
    stripped = text.strip().strip(".,!?\"'").strip()
    for name in valid_names:
        if stripped.lower() == name.lower():
            return name
    # Fallback: substring match
    for name in valid_names:
        if name.lower() in lowered:
            return name
    return None


# Re-export the helper so detective/doctor can use it
__all__ = ["Mafia", "_extract_name"]
