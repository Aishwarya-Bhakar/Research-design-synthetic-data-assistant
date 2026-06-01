from __future__ import annotations

from json_utils import safe_json_dumps
from ai_client import call_ai_json
from heuristics import fallback_designs
import config


SYSTEM = """
You are an expert research methodology advisor.
Suggest research designs based on the topic, literature brief, population, and intended objective.
Do not overclaim. Return valid JSON only.
"""


def suggest_research_designs(topic: str, literature_summary: dict, population: str = "") -> dict:
    prompt = f"""
Topic:
{topic}

Population/setting:
{population or "not specified"}

Literature summary:
{safe_json_dumps(literature_summary)}

Return ONLY valid JSON:
{{
  "suggested_designs": [
    {{
      "design": "cross-sectional/cohort/case-control/RCT/quasi-experimental/diagnostic accuracy/qualitative/mixed-methods",
      "fit_score": 0.0,
      "reason": "...",
      "typical_outputs": ["..."],
      "minimum_data_needed": ["..."],
      "limitations": ["..."]
    }}
  ],
  "recommended_design": "...",
  "reason_for_recommendation": "...",
  "sampling_strategy_suggestions": ["..."],
  "bias_and_confounding_warnings": ["..."]
}}
"""
    try:
        return call_ai_json(prompt=prompt, system=SYSTEM, max_tokens=3000)
    except Exception as exc:
        if not config.ALLOW_HEURISTIC_FALLBACK:
            raise
        data = fallback_designs(topic)
        data["warnings"].append(str(exc))
        return data
