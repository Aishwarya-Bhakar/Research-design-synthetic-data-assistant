from __future__ import annotations

from json_utils import safe_json_dumps
from ai_client import call_ai_json
from heuristics import fallback_framework
import config


SYSTEM = """
You are a research design assistant.
Build conceptual frameworks, hypotheses, and statistical relationship constraints.
Return valid JSON only.
"""


def build_framework_and_hypotheses(
    topic: str,
    study_design: str,
    variables: list[dict],
    expected_results_text: str,
    literature_summary: dict | None = None,
) -> dict:
    prompt = f"""
Research topic:
{topic}

Study design:
{study_design}

Variables:
{safe_json_dumps(variables)}

Expected results / hypotheses described by user:
{expected_results_text or "not specified"}

Literature summary:
{safe_json_dumps(literature_summary or {})}

Return ONLY valid JSON:
{{
  "conceptual_framework": {{
    "summary": "...",
    "independent_variables": ["..."],
    "dependent_variables": ["..."],
    "control_variables": ["..."],
    "mediators": ["..."],
    "moderators": ["..."],
    "mermaid": "flowchart LR\\n  A[Exposure] --> B[Outcome]"
  }},
  "hypotheses": [
    {{
      "code": "H1",
      "text": "...",
      "null_hypothesis": "...",
      "variables_involved": ["..."],
      "expected_direction": "positive/negative/difference/no difference",
      "suggested_test": "..."
    }}
  ],
  "relationships": [
    {{
      "source_variable": "...",
      "target_variable": "...",
      "relationship_type": "positive_correlation/negative_correlation/group_difference/risk_increase/risk_decrease/no_expected_relationship",
      "strength": "weak/moderate/strong",
      "suggested_r": 0.3,
      "rationale": "..."
    }}
  ],
  "analysis_plan": ["..."],
  "warnings": ["..."]
}}
"""
    try:
        return call_ai_json(prompt=prompt, system=SYSTEM, max_tokens=4000)
    except Exception as exc:
        if not config.ALLOW_HEURISTIC_FALLBACK:
            raise
        data = fallback_framework(topic, variables, expected_results_text)
        data["warnings"].append(str(exc))
        return data
