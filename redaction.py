from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .agents.base_agent import BaseAgent
    from .game_state import GameState


def redact_for(agent: "BaseAgent", state: "GameState") -> str:
    """Return the user message body to feed to this agent's LLM call.
    Includes: alive players, recent transcript, the agent's own private
    knowledge (role, partner if mafia, investigation log if detective),
    and the agent's current suspicion scores."""

    alive = ", ".join(state.alive_names())

    # Recent day discussion
    day_speeches = state.recent_day_transcript(state.day)
    if day_speeches:
        discussion = "\n".join(
            f"  {e['speaker']}: \"{e['text']}\"" for e in day_speeches
        )
        discussion_block = f"\n\nDiscussion so far on day {state.day}:\n{discussion}"
    else:
        discussion_block = ""

    # Recent narration (last 4 narration entries)
    narrations = [e for e in state.transcript if e["kind"] == "narration"]
    recent_narr = narrations[-4:]
    if recent_narr:
        narr_lines = "\n".join(f"  {e['text']}" for e in recent_narr)
        narration_block = f"\n\nRecent events:\n{narr_lines}"
    else:
        narration_block = ""

    # Private knowledge - role-specific
    private_lines = [f"You are {agent.name}, a {agent.role.upper()}."]
    if agent.role == "mafia":
        partner = getattr(agent, "partner_name", None)
        if partner:
            private_lines.append(f"Your mafia partner is {partner}.")
    elif agent.role == "detective":
        log = getattr(agent, "investigation_log", {})
        if log:
            findings = ", ".join(f"{k} is {v}" for k, v in log.items())
            private_lines.append(f"Investigations: {findings}.")
        else:
            private_lines.append("You have not investigated anyone yet.")

    others = [(n, s) for n, s in agent.belief_state.items() if n != agent.name]
    beliefs_view = ", ".join(f"{n}={s:.2f}" for n, s in others)
    private_lines.append(f"Your suspicion scores (0=trust, 1=certain mafia): {beliefs_view}.")

    private_block = "\n  - " + "\n  - ".join(private_lines)

    return (
        f"Day {state.day}. Alive players: {alive}."
        f"{narration_block}"
        f"{discussion_block}"
        f"\n\nYour private knowledge:{private_block}"
    )
