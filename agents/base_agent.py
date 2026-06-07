from __future__ import annotations

import random
from typing import TYPE_CHECKING

from .. import belief_model, config, prompts
from ..llm import call_llm
from ..redaction import redact_for

if TYPE_CHECKING:
    from ..game_state import GameState


class BaseAgent:
    role: str = "base"  

    def __init__(self, name: str, all_player_names: list[str]):
        self.name = name
        self.is_alive = True
        self.belief_state: dict[str, float] = belief_model.initial_beliefs(
            name, all_player_names
        )

    def system_prompt(self) -> str:
        raise NotImplementedError

    # ---- Day phase ----

    def speak(self, state: "GameState") -> str:
        sys = self.system_prompt()
        msg = prompts.speak_user_prompt(redact_for(self, state))
        try:
            return call_llm(sys, msg, max_tokens=config.MAX_TOKENS_SPEECH)
        except RuntimeError:
            return f"({self.name} stays silent.)"

    def update_beliefs(self, speaker_name: str, message: str, state: "GameState") -> None:
        if speaker_name == self.name:
            return
        self.belief_state = belief_model.update_beliefs_via_llm(
            listener_name=self.name,
            listener_role=self.role,
            speaker_name=speaker_name,
            message=message,
            current_beliefs=self.belief_state,
        )

    def vote(self, state: "GameState") -> str:
        """Return the name of the living player with highest suspicion.
        Ties broken randomly. Never votes for self."""
        alive_others = [p.name for p in state.alive() if p.name != self.name]
        if not alive_others:
            return self.name  # degenerate; engine should have ended already
        scores = [(name, self.belief_state.get(name, 0.5)) for name in alive_others]
        max_score = max(s for _, s in scores)
        top = [name for name, s in scores if s == max_score]
        return random.choice(top)
