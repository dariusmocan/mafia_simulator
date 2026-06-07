from __future__ import annotations

from .. import prompts
from .base_agent import BaseAgent


class Crewmate(BaseAgent):
    role = "crewmate"

    def system_prompt(self) -> str:
        return prompts.crewmate_system(self.name)
