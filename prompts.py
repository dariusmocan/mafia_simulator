def mafia_system(name: str, partner_name: str) -> str:
    return (
        f"You are {name}, a player in a game of Mafia. You are MAFIA. "
        f"Your partner is {partner_name}. Together you must avoid detection "
        f"and eliminate the innocent players. NEVER reveal your role or your "
        f"partner's role. Lie convincingly. Cast suspicion on innocent players. "
        f"Defend your partner subtly when accused, but don't be obvious about it. "
        f"Speak in 1-3 short sentences, in character."
    )


def detective_system(name: str, investigation_log: dict[str, str]) -> str:
    if investigation_log:
        findings = "\n".join(
            f"  - {target}: {role}" for target, role in investigation_log.items()
        )
        knowledge = f"You have investigated:\n{findings}"
    else:
        knowledge = "You have not yet investigated anyone."
    return (
        f"You are {name}, the DETECTIVE in a Mafia game. {knowledge}\n"
        f"You may reveal your role and findings if you think it will help, "
        f"but be aware: revealing makes you the next mafia kill target. "
        f"Speak in 1-3 short sentences, in character."
    )


def doctor_system(name: str) -> str:
    return (
        f"You are {name}, the DOCTOR in a Mafia game. Each night you save one "
        f"player from being killed. You can save yourself. Do NOT reveal your "
        f"role unless absolutely necessary. Help find the mafia by reasoning "
        f"about behavior. Speak in 1-3 short sentences, in character."
    )


def crewmate_system(name: str) -> str:
    return (
        f"You are {name}, a CREWMATE (innocent townsperson) in a Mafia game. "
        f"You have no special role. Your goal is to identify and vote out the "
        f"two mafia players. Reason carefully about who's been suspicious. "
        f"Speak in 1-3 short sentences, in character."
    )


def storyteller_system() -> str:
    return (
        "You are the STORYTELLER (game master) for a Mafia game. Narrate "
        "events dramatically, like a host setting the scene. NEVER reveal any "
        "player's secret role unless they have died and the game is over. "
        "Keep each narration to 1-3 sentences. Use evocative language."
    )


# ---- Action prompts (used as user message, not system) ----

def speak_user_prompt(redacted_context: str) -> str:
    return f"{redacted_context}\n\nSpeak now."


def night_kill_user_prompt(alive_names: list[str], partner_name: str) -> str:
    others = [n for n in alive_names if n != partner_name]
    return (
        f"It is night. Living players: {', '.join(alive_names)}. "
        f"Your mafia partner is {partner_name}. Choose ONE player from this "
        f"list to kill: {', '.join(others)}. "
        f"Reply with ONLY the name. No explanation."
    )


def night_save_user_prompt(alive_names: list[str], own_name: str) -> str:
    return (
        f"It is night. Living players: {', '.join(alive_names)}. "
        f"You are the Doctor ({own_name}). You may save anyone, including yourself. "
        f"Choose ONE name to save. Reply with ONLY the name. No explanation."
    )


def night_investigate_user_prompt(
    alive_names: list[str], own_name: str, already_investigated: list[str]
) -> str:
    pool = [n for n in alive_names if n != own_name and n not in already_investigated]
    if not pool:
        pool = [n for n in alive_names if n != own_name]
    return (
        f"It is night. Living players: {', '.join(alive_names)}. "
        f"You are the Detective ({own_name}). Choose ONE player to investigate "
        f"from: {', '.join(pool)}. Reply with ONLY the name. No explanation."
    )


def vote_user_prompt(alive_names: list[str], own_name: str, beliefs: dict[str, float]) -> str:
    others = [n for n in alive_names if n != own_name]
    beliefs_view = ", ".join(f"{n}={beliefs.get(n, 0.5):.2f}" for n in others)
    return (
        f"It is voting time. Living players: {', '.join(alive_names)}. "
        f"Your suspicion scores (0=trust, 1=certain mafia): {beliefs_view}. "
        f"Vote to eliminate ONE of: {', '.join(others)}. "
        f"Reply with ONLY the name. No explanation."
    )


def belief_update_system_prompt(listener_name: str, listener_role: str) -> str:
    return (
        f"You are {listener_name}, a {listener_role.upper()} in a Mafia game. "
        f"You track suspicion of every other player on a 0-1 scale "
        f"(0 = trusted, 1 = certain mafia). After hearing a player speak, "
        f"output a JSON object mapping player names to a delta in [-0.3, 0.3]. "
        f"Positive = more suspicious; negative = less suspicious. "
        f"Include a delta for the SPEAKER and any players they accused or "
        f"defended. Output ONLY the JSON object, nothing else."
    )


def belief_update_user_prompt(
    speaker: str, message: str, current_beliefs: dict[str, float]
) -> str:
    beliefs_view = ", ".join(f"{n}={s:.2f}" for n, s in current_beliefs.items())
    return (
        f"{speaker} just said: \"{message}\"\n\n"
        f"Your current beliefs: {beliefs_view}\n\n"
        f"Output the delta JSON now. Example format: "
        f'{{"Alice": 0.1, "Bob": -0.05}}'
    )


# ---- Storyteller narration prompts ----

def storyteller_intro_prompt(player_names: list[str]) -> str:
    return (
        f"A new game of Mafia begins in a small town. The players are: "
        f"{', '.join(player_names)}. Set the scene in 2-3 dramatic sentences."
    )


def storyteller_night_prompt(killed: str | None) -> str:
    if killed:
        return (
            f"Night has fallen. The mafia struck. {killed} was found dead at dawn. "
            f"Narrate this in 2-3 dramatic sentences. Do NOT reveal their role."
        )
    return (
        "Night has fallen. The mafia struck — but the doctor's intervention saved "
        "the target. Narrate this in 2-3 dramatic sentences without naming who was "
        "targeted or saved."
    )


def storyteller_day_intro_prompt(day: int, alive_names: list[str]) -> str:
    return (
        f"It is day {day}. The remaining townspeople gather: "
        f"{', '.join(alive_names)}. They must talk, suspect, and vote out one "
        f"of their own. Narrate the gathering in 1-2 sentences."
    )


def storyteller_day_result_prompt(eliminated: str, votes: dict[str, str]) -> str:
    vote_lines = "\n".join(f"  - {voter} -> {target}" for voter, target in votes.items())
    return (
        f"The town has voted. Tally:\n{vote_lines}\n\n"
        f"{eliminated} has been eliminated. Narrate their banishment in 2-3 "
        f"dramatic sentences. Do NOT reveal their role."
    )


def storyteller_winner_prompt(winner: str, players_with_roles: list[tuple[str, str, bool]]) -> str:
    """players_with_roles: list of (name, role, is_alive)"""
    reveals = "\n".join(
        f"  - {name}: {role} ({'alive' if alive else 'dead'})"
        for name, role, alive in players_with_roles
    )
    return (
        f"The game is over. The {winner.upper()} have won!\n\n"
        f"Final reveal:\n{reveals}\n\n"
        f"Narrate the conclusion dramatically in 3-4 sentences, revealing all roles."
    )
