from __future__ import annotations

import json
import re
from typing import Any


class JSONExtractionError(ValueError):
    pass


def strip_code_fence(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()
    return cleaned


def extract_json(text: str) -> Any:
    cleaned = strip_code_fence(text)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    candidates = re.findall(r"(\{.*\}|\[.*\])", cleaned, flags=re.DOTALL)
    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue

    raise JSONExtractionError(f"No valid JSON found in AI output:\n{text[:2000]}")


def safe_json_dumps(data: Any, indent: int = 2) -> str:
    return json.dumps(data, ensure_ascii=False, indent=indent, default=str)
