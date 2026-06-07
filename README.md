# Mafia Multi-Agent Simulation

Six LLM-driven agents play a full game of Mafia in your terminal. Powered by Groq + Llama 3.3 70B.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Then edit .env and paste your Groq API key
# Get one for free at https://console.groq.com/keys
```

## Run

From the project root (the directory that *contains* `mafia_simulation/`):

```bash
python -m mafia_simulation.main
```

## Roles

- 2 Mafia (kill at night, lie during the day)
- 1 Detective (investigates one player per night)
- 1 Doctor (saves one player per night)
- 2 Crewmates (just vote)
- 1 Storyteller (narrates; not a player)

## Win conditions

- Innocents win when all Mafia are eliminated
- Mafia win when their count is >= remaining innocents
