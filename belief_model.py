from __future__ import annotations

from . import config, prompts
from .llm import call_llm_json


def initial_beliefs(own_name: str, all_names: list[str]) -> dict[str, float]:
    """Self gets 0.0 (no self-suspicion); everyone else gets 0.5 (neutral)."""
    return {
        name: (0.0 if name == own_name else 0.5)
        for name in all_names
    }


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def apply_delta(
    current: dict[str, float],
    delta: dict[str, float],
    own_name: str,
) -> dict[str, float]:
    """Return a new dict with delta applied. Self-suspicion stays at 0.
    Each delta is clamped to BELIEF_DELTA_MIN..BELIEF_DELTA_MAX before
    application; each result is clamped to SUSPICION_MIN..SUSPICION_MAX."""
    result = dict(current)
    for name, raw_d in delta.items():
        if name == own_name:
            continue
        if name not in result:
            continue
        try:
            d = float(raw_d)
        except (TypeError, ValueError):
            continue
        d = _clamp(d, config.BELIEF_DELTA_MIN, config.BELIEF_DELTA_MAX)
        result[name] = _clamp(
            result[name] + d, config.SUSPICION_MIN, config.SUSPICION_MAX
        )
    # Defensive: self-suspicion always 0.
    result[own_name] = 0.0
    return result


def update_beliefs_via_llm(
    listener_name: str,
    listener_role: str,
    speaker_name: str,
    message: str,
    current_beliefs: dict[str, float],
) -> dict[str, float]:
    """Call the LLM for a delta JSON and return the updated belief dict.
    On any failure (parse errors, network, etc.) returns current_beliefs unchanged."""
    sys = prompts.belief_update_system_prompt(listener_name, listener_role)
    msg = prompts.belief_update_user_prompt(speaker_name, message, current_beliefs)
    delta = call_llm_json(sys, msg, max_tokens=config.MAX_TOKENS_BELIEF_JSON)
    if not delta:
        return current_beliefs
    return apply_delta(current_beliefs, delta, listener_name)
