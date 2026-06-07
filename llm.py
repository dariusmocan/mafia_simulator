from __future__ import annotations

import json
import os
import re
import time
from typing import Any

from dotenv import load_dotenv
from groq import Groq, RateLimitError, APIError

from . import config
from pathlib import Path

_ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

_API_KEY = os.environ.get("GROQ_API_KEY")
if not _API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is not set. Copy .env.example to .env and paste your key. "
        "Get one free at https://console.groq.com/keys"
    )

_client = Groq(api_key=_API_KEY)


def call_llm(system_prompt: str, message: str, max_tokens: int = 300) -> str:
    """Plain text LLM call with retry on rate-limit / transient errors."""
    last_err: Exception | None = None
    for attempt in range(config.LLM_RETRIES):
        try:
            resp = _client.chat.completions.create(
                model=config.MODEL,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message},
                ],
            )
            return resp.choices[0].message.content.strip()
        except RateLimitError as e:
            last_err = e
            time.sleep(config.LLM_RETRY_SLEEP_SECONDS)
        except APIError as e:
            last_err = e
            time.sleep(config.LLM_RETRY_SLEEP_SECONDS)
    # Final fallback: re-raise as RuntimeError so the engine can decide what to do.
    raise RuntimeError(f"LLM call failed after {config.LLM_RETRIES} attempts: {last_err}")


def call_llm_json(
    system_prompt: str,
    message: str,
    max_tokens: int = 300,
) -> dict[str, Any]:
    """LLM call expecting a JSON object. Retries on parse failures
    with a stricter reminder. Returns {} if all attempts fail."""
    strict_suffix = (
        "\n\nIMPORTANT: Output ONLY a valid JSON object. "
        "No prose, no markdown, no backticks. Just the JSON."
    )
    sys = system_prompt
    for _attempt in range(config.LLM_RETRIES):
        try:
            raw = call_llm(sys, message, max_tokens=max_tokens)
            return _extract_json(raw)
        except (json.JSONDecodeError, ValueError):
            sys = system_prompt + strict_suffix
        except RuntimeError:
            break
    return {}


def _extract_json(text: str) -> dict[str, Any]:
    """Best-effort: strip code fences, find the first {...} block, parse."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)
    parsed = json.loads(cleaned)
    if not isinstance(parsed, dict):
        raise ValueError("Expected a JSON object, got something else.")
    return parsed
