from __future__ import annotations

from typing import Any

import config
from json_utils import extract_json


class AIClientError(RuntimeError):
    pass


def groq_available() -> bool:
    return bool(config.GROQ_API_KEY)


def call_ai_text(
    prompt: str,
    system: str = "",
    temperature: float = 0.1,
    max_tokens: int = 4096,
    model: str | None = None,
) -> str:
    if not config.GROQ_API_KEY:
        raise AIClientError(
            "GROQ_API_KEY is missing. Add it to .env or enable heuristic fallback."
        )

    try:
        from groq import Groq
    except ImportError as exc:
        raise AIClientError(
            "The groq package is not installed. Run: pip install -r requirements.txt"
        ) from exc

    client = Groq(api_key=config.GROQ_API_KEY)
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=model or config.GROQ_MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content or ""


def call_ai_json(
    prompt: str,
    system: str = "",
    temperature: float = 0.1,
    max_tokens: int = 4096,
    model: str | None = None,
) -> Any:
    text = call_ai_text(
        prompt=prompt,
        system=system,
        temperature=temperature,
        max_tokens=max_tokens,
        model=model,
    )
    return extract_json(text)
