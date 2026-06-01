from __future__ import annotations

from json_utils import safe_json_dumps
from ai_client import call_ai_json
from literature.search import search_literature
from heuristics import fallback_literature_summary
import config


SYSTEM = """
You are a research methodology assistant.
Use only the retrieved literature records supplied by the software.
Do not invent papers, authors, journals, years, PMIDs, DOIs, sample sizes, or effect sizes.
If evidence is weak or absent, state that explicitly.
Return valid JSON only.
"""


def research_literature(
    topic: str,
    domain: str = "",
    sources: list[str] | None = None,
    max_results: int | None = None,
) -> dict:
    papers = search_literature(topic, sources=sources, max_results=max_results)

    prompt = f"""
Research topic:
{topic}

Research domain/discipline:
{domain or "not specified"}

Retrieved literature records:
{safe_json_dumps(papers)}

Task:
Create a structured research evidence brief for a research design and synthetic data generator.

Return ONLY valid JSON in this structure:
{{
  "topic": "...",
  "paper_count": 0,
  "evidence_summary": "...",
  "papers": [
    {{
      "source": "PubMed/Crossref",
      "id": "...",
      "title": "...",
      "year": "...",
      "journal": "...",
      "url": "...",
      "summary": "...",
      "key_findings": ["..."],
      "variables_found": ["..."],
      "relationships_found": ["..."],
      "limitations": ["..."]
    }}
  ],
  "candidate_independent_variables": ["..."],
  "candidate_dependent_variables": ["..."],
  "candidate_control_variables": ["..."],
  "candidate_mediators": ["..."],
  "candidate_moderators": ["..."],
  "candidate_relationships": ["..."],
  "evidence_gaps": ["..."],
  "warnings": ["..."]
}}
"""
    try:
        return call_ai_json(prompt=prompt, system=SYSTEM, max_tokens=5000)
    except Exception as exc:
        if not config.ALLOW_HEURISTIC_FALLBACK:
            raise
        summary = fallback_literature_summary(topic, papers)
        summary["warnings"].append(str(exc))
        return summary
