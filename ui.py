from __future__ import annotations

import random

from rich.console import Console
from rich.rule import Rule

console = Console()

_PLAYER_COLORS_PALETTE = [
    "bright_blue",
    "bright_magenta",
    "bright_green",
    "bright_yellow",
    "bright_cyan",
    "orange1",
    "purple",
    "deep_pink2",
]

_player_colors: dict[str, str] = {}


def assign_player_colors(names: list[str]) -> None:
    """Call once at game start. Assigns each name a stable color."""
    palette = list(_PLAYER_COLORS_PALETTE)
    random.shuffle(palette)
    for i, name in enumerate(names):
        _player_colors[name] = palette[i % len(palette)]


def _color_for(name: str) -> str:
    return _player_colors.get(name, "white")


def print_storyteller(text: str) -> None:
    console.print(f"[italic yellow]>> {text}[/]")


def print_speech(name: str, text: str, role: str | None = None) -> None:
    color = _color_for(name)
    label = f"{name}({role})" if role else name
    console.print(f"[bold {color}]{label}[/]: {text}")


def print_death(name: str) -> None:
    console.print(f"[bold red]X {name} has been killed.[/]")


def print_elimination(name: str) -> None:
    console.print(f"[bold red]== {name} has been voted out.[/]")


def print_vote(voter: str, target: str) -> None:
    voter_color = _color_for(voter)
    target_color = _color_for(target)
    console.print(
        f"  [bold {voter_color}]{voter}[/] votes -> [bold {target_color}]{target}[/]"
    )


def print_phase_header(day: int, phase: str) -> None:
    console.print()
    console.print(Rule(f"[bold]Day {day} -- {phase.upper()}[/]"))


def print_warning(text: str) -> None:
    console.print(f"[dim red]! {text}[/]")


def print_winner(winner: str) -> None:
    console.print()
    console.print(Rule(f"[bold green]*** {winner.upper()} WIN ***[/]"))


def print_intro(text: str) -> None:
    console.print()
    console.print(Rule("[bold]MAFIA[/]"))
    console.print(f"[italic yellow]{text}[/]")

def print_night_action(text: str) -> None:
    """Surface a private night action (doctor / detective) to the viewer"""
    console.print(f"[dim italic]   . {text}[/]")