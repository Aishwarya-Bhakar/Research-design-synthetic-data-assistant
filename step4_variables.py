from __future__ import annotations

from json_utils import safe_json_dumps
from ai_client import call_ai_json
from schema_models import VariableDefinition
from heuristics import infer_variable_type
import config


SYSTEM = """
You are a research data dictionary and codebook assistant.
Suggest variable metadata that is plausible, transparent, and editable by the user.
Return valid JSON only.
"""


def suggest_variable(
    variable_name: str,
    topic: str,
    study_design: str,
    literature_summary: dict | None = None,
    existing_variables: list[dict] | None = None,
) -> dict:
    prompt = f"""
Research topic:
{topic}

Study design:
{study_design}

Variable name entered by user:
{variable_name}

Existing variables:
{safe_json_dumps(existing_variables or [])}

Literature summary:
{safe_json_dumps(literature_summary or {})}

Return ONLY valid JSON:
{{
  "name": "{variable_name}",
  "label": "...",
  "role": "independent/dependent/control/covariate/mediator/moderator/exposure/outcome/grouping/identifier",
  "variable_type": "continuous/integer/binary/categorical/ordinal/date/text",
  "definition": "...",
  "unit": "...",
  "min_value": null,
  "max_value": null,
  "categories": [],
  "distribution": "normal/lognormal/uniform/poisson/bernoulli/categorical/ordinal/date/text",
  "mean": null,
  "sd": null,
  "missing_rate": 0.0,
  "coding": "...",
  "notes": "..."
}}
"""
    try:
        data = call_ai_json(prompt=prompt, system=SYSTEM, max_tokens=2500)
    except Exception as exc:
        if not config.ALLOW_HEURISTIC_FALLBACK:
            raise
        data = {
            "name": variable_name,
            "label": variable_name.replace("_", " ").title(),
            "definition": f"User-defined variable: {variable_name}",
            "unit": "",
            "missing_rate": 0.0,
            "coding": "",
            "notes": f"Heuristic fallback used. AI error: {exc}",
            **infer_variable_type(variable_name),
        }

    return VariableDefinition(**data).model_dump()
