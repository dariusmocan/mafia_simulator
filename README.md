# Mafia Multi-Agent Simulation

Six LLM-driven agents play a full game of Mafia in your terminal. Each agent
has its own role, private knowledge, and evolving beliefs about the others;
the engine moderates a strict night/day cycle until one side wins.

For setup and run steps, see `INSTRUCTIONS.txt`.

## Problem domain

Mafia is a hidden-information social-deduction game. It is
a useful test bed for multi-agent research because it forces agents to:

- **Reason under partial information.** No agent ever sees the full game
  state. Mafia know each other; the detective accumulates investigation
  results; everyone else only has public speech to go on.
- **Communicate strategically.** Crewmates must coordinate via natural
  language without a private channel. Mafia must lie convincingly and
  defend each other subtly.
- **Update beliefs over time.** Suspicion of each other player is a moving
  target shaped by speech, votes, and night outcomes.
- **Make adversarial decisions.** Night kills, investigations, saves, and
  day-time votes are all chosen against opponents whose roles are unknown.

The simulation produces a full transcript of speeches, votes, deaths, and
storyteller narration - a corpus that captures emergent deception,
accusation, and coordination among LLM agents.

### Roles and rules

| Role        | Count | Knows                               | Acts at night                 |
| ----------- | ----: | ----------------------------------- | ----------------------------- |
| Mafia       |     2 | The other mafia                     | Choose one player to kill     |
| Detective   |     1 | Own role; growing investigation log | Investigate one player's role |
| Doctor      |     1 | Own role                            | Choose one player to save     |
| Crewmate    |     2 | Own role                            | -                             |
| Storyteller |     1 | Everything (narrator, not a player) | -                             |

Each day, every living agent speaks once and then everyone votes. The player
with the plurality of votes is eliminated; ties are broken randomly.

### Win conditions

- **Innocents win** when no mafia remain alive.
- **Mafia win** when they *strictly outnumber* the innocents (e.g. 2 vs 1).
  When the counts are equal, the game continues - a 2 vs 2 standoff goes to
  the next night.

## Architecture

The codebase is small and intentionally layered. Each module has a single
responsibility, and agents only ever see a redacted view of the world.

```
main.py
  └── builds players, hands them to the engine
game_engine.py
  └── orchestrates night → day → vote → win-check loop
        ├── reads / mutates GameState
        └── calls each agent's role-specific methods
agents/
  ├── base_agent.py     shared LLM plumbing, belief updates, voting
  ├── mafia.py          night_kill_choice, deceptive speech
  ├── detective.py      night_investigate, log of past results
  ├── doctor.py         night_save_choice
  ├── crewmate.py       speech + vote only
  └── storyteller.py    narration; not a player
game_state.py            passive dataclass: players, day, phase, transcript
redaction.py             builds the per-agent view fed to its LLM call
belief_model.py          per-agent suspicion scores [0..1] + LLM updates
llm.py                   single entry point to Groq (call_llm, call_llm_json)
prompts.py               every system prompt, in one tuneable place
ui.py                    rich-terminal output (colors per player, headers)
config.py                model name, player names, role distribution, caps
```

### How a turn flows

1. **Engine** sets `state.phase = "night"`.
2. The engine asks the first living mafia for a kill target, the doctor for a
   save target, and the detective for an investigation target. Each agent's
   decision goes through `redact_for(...)` so the prompt only contains
   information that agent is allowed to know.
3. The engine resolves the night (kill unless saved), records the death, and
   asks the **storyteller** to narrate.
4. `check_winner` runs. If a side has won, the engine returns.
5. **Engine** sets `state.phase = "day"`. Living agents are shuffled and each
   one speaks once. Every other living agent updates its belief state from
   that speech via the **belief model**.
6. Every living agent votes. `tally_votes` picks the plurality target
   (random tie-break); the engine eliminates them and the storyteller
   narrates the result.
7. `check_winner` runs again. If still inconclusive, `state.day += 1` and the
   loop returns to step 1.

### Key invariants

- **Information hygiene.** `redaction.py` is the only place that builds an
  agent's user message. Non-mafia agents are never shown another player's
  role in their prompt.
- **One LLM seam.** Every model call goes through `llm.call_llm` /
  `call_llm_json`. Retries, JSON parsing, token caps, and the model name
  live there and nowhere else.
- **Engine owns state.** Agents read `GameState` (through the redaction
  layer) but never mutate it. Death, elimination, and phase transitions
  happen exclusively in `game_engine.py`.
- **Beliefs are per-agent.** Each agent keeps a `belief_state: dict[name, float]` of suspicion in [0, 1]. After hearing a speech, the listener
  asks the LLM for a clamped delta and updates locally - no global belief.

### Configuration

`config.py` is the single tuning surface: model name, player roster, role
distribution, max tokens per call type, retry behavior, and belief
clamping bounds. Changing the cast size means changing `PLAYER_NAMES` and
`ROLES` together  they must stay the same length.
