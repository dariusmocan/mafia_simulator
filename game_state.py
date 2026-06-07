from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from .agents.base_agent import BaseAgent


Phase = Literal["night", "day"]
TranscriptKind = Literal["speech", "narration", "vote", "death"]


@dataclass
class GameState:
    players: list["BaseAgent"]
    day: int = 1
    phase: Phase = "night"
    transcript: list[dict] = field(default_factory=list)

    def alive(self) -> list["BaseAgent"]:
        return [p for p in self.players if p.is_alive]

    def alive_names(self) -> list[str]:
        return [p.name for p in self.alive()]

    def alive_innocents(self) -> list["BaseAgent"]:
        return [p for p in self.alive() if p.role != "mafia"]

    def alive_mafia(self) -> list["BaseAgent"]:
        return [p for p in self.alive() if p.role == "mafia"]

    def by_name(self, name: str) -> "BaseAgent":
        for p in self.players:
            if p.name == name:
                return p
        raise KeyError(f"No player named {name!r}")

    def add_to_transcript(
        self, *, day: int, phase: Phase, speaker: str, text: str, kind: TranscriptKind
    ) -> None:
        self.transcript.append(
            {"day": day, "phase": phase, "speaker": speaker, "text": text, "kind": kind}
        )

    def recent_day_transcript(self, day: int) -> list[dict]:
        return [
            e for e in self.transcript
            if e["day"] == day and e["phase"] == "day" and e["kind"] == "speech"
        ]
