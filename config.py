from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def env_str(name: str, default: str = "") -> str:
    value = os.getenv(name, default)
    return value.strip() if isinstance(value, str) else default


def env_bool(name: str, default: bool = False) -> bool:
    value = env_str(name, str(default)).lower()
    return value in {"1", "true", "yes", "y", "on"}


def env_int(name: str, default: int) -> int:
    try:
        return int(env_str(name, str(default)))
    except ValueError:
        return default


GROQ_API_KEY = env_str("GROQ_API_KEY")
GROQ_MODEL = env_str("GROQ_MODEL", "llama-3.3-70b-versatile")

NCBI_EMAIL = env_str("NCBI_EMAIL")
NCBI_API_KEY = env_str("NCBI_API_KEY")

CROSSREF_MAILTO = env_str("CROSSREF_MAILTO") or NCBI_EMAIL
LITERATURE_MAX_RESULTS = env_int("LITERATURE_MAX_RESULTS", 8)
ALLOW_HEURISTIC_FALLBACK = env_bool("ALLOW_HEURISTIC_FALLBACK", True)
