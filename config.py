# Groq model name
MODEL = "llama-3.3-70b-versatile"

# Six players with stable names. Roles are shuffled at game start.
PLAYER_NAMES = ["Alice", "Bob", "Carol", "Dave", "Eve", "Frank"]

# Must be the same length as PLAYER_NAMES.
ROLES = ["mafia", "mafia", "detective", "doctor", "crewmate", "crewmate"]

# Each living agent speaks this many times per day.
MAX_DAY_ROUNDS = 1

# LLM generation caps.
MAX_TOKENS_SPEECH = 200
MAX_TOKENS_NARRATION = 200
MAX_TOKENS_BELIEF_JSON = 300
MAX_TOKENS_DECISION = 50  # for night actions / votes

# Retry behavior for llm.py
LLM_RETRIES = 3
LLM_RETRY_SLEEP_SECONDS = 5

# Belief update clamping
SUSPICION_MIN = 0.0
SUSPICION_MAX = 1.0
BELIEF_DELTA_MIN = -0.3
BELIEF_DELTA_MAX = 0.3
