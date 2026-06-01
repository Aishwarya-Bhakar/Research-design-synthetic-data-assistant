from __future__ import annotations

from typing import Any


def infer_variable_type(name: str) -> dict[str, Any]:
    n = name.lower()
    if any(x in n for x in ["sex", "gender", "group", "type", "category", "status"]):
        return {
            "variable_type": "categorical",
            "distribution": "categorical",
            "categories": ["Group A", "Group B"],
            "role": "control",
        }
    if any(x in n for x in ["yes", "no", "present", "absent", "smoker", "diabetes", "hypertension"]):
        return {
            "variable_type": "binary",
            "distribution": "bernoulli",
            "categories": ["No", "Yes"],
            "role": "covariate",
        }
    if "age" in n:
        return {
            "variable_type": "integer",
            "distribution": "normal",
            "min_value": 18,
            "max_value": 80,
            "mean": 40,
            "sd": 12,
            "role": "control",
        }
    if any(x in n for x in ["score", "scale", "index"]):
        return {
            "variable_type": "continuous",
            "distribution": "normal",
            "min_value": 0,
            "max_value": 100,
            "mean": 50,
            "sd": 15,
            "role": "dependent",
        }
    return {
        "variable_type": "continuous",
        "distribution": "normal",
        "min_value": 0,
        "max_value": 100,
        "mean": 50,
        "sd": 10,
        "role": "covariate",
    }


def fallback_literature_summary(topic: str, papers: list[dict]) -> dict:
    titles = [p.get("title", "") for p in papers if p.get("title") and p.get("source") != "system"]
    return {
        "topic": topic,
        "paper_count": len(titles),
        "evidence_summary": (
            "AI summary was not available. Retrieved literature metadata is shown; "
            "review abstracts manually or add GROQ_API_KEY for AI synthesis."
        ),
        "papers": [
            {
                "source": p.get("source"),
                "id": p.get("id"),
                "title": p.get("title"),
                "year": p.get("year"),
                "journal": p.get("journal"),
                "url": p.get("url"),
                "summary": p.get("abstract", "")[:500] if p.get("abstract") else "",
                "key_findings": [],
                "variables_found": [],
                "relationships_found": [],
            }
            for p in papers
        ],
        "candidate_independent_variables": [],
        "candidate_dependent_variables": [],
        "candidate_control_variables": [],
        "candidate_mediators": [],
        "candidate_moderators": [],
        "candidate_relationships": [],
        "warnings": ["Heuristic fallback used because Groq was unavailable or failed."],
    }


def fallback_designs(topic: str) -> dict:
    return {
        "suggested_designs": [
            {
                "design": "cross-sectional",
                "fit_score": 0.8,
                "reason": "Useful for estimating prevalence and associations at one time point.",
                "typical_outputs": ["prevalence", "mean differences", "correlations", "regression models"],
                "minimum_data_needed": ["outcome variable", "predictor variables", "covariates"],
                "limitations": ["Temporal direction is usually weak."],
            },
            {
                "design": "cohort",
                "fit_score": 0.7,
                "reason": "Useful when exposure precedes outcome and incidence/risk is important.",
                "typical_outputs": ["risk ratio", "hazard ratio", "incidence"],
                "minimum_data_needed": ["baseline exposure", "follow-up outcome", "time variable"],
                "limitations": ["Requires temporal assumptions."],
            },
            {
                "design": "case-control",
                "fit_score": 0.65,
                "reason": "Useful for rare outcomes and retrospective exposure comparison.",
                "typical_outputs": ["odds ratio"],
                "minimum_data_needed": ["case status", "exposure history", "confounders"],
                "limitations": ["Selection and recall bias are possible."],
            },
        ],
        "recommended_design": "cross-sectional",
        "reason_for_recommendation": "Safe default for general synthetic data exploration.",
        "sampling_strategy_suggestions": ["Define inclusion/exclusion criteria", "Use stratified sampling if groups matter"],
        "bias_and_confounding_warnings": ["Specify confounders explicitly"],
        "warnings": ["Heuristic design suggestions used."],
    }


def fallback_framework(topic: str, variables: list[dict], hypotheses_text: str) -> dict:
    indep = [v["name"] for v in variables if v.get("role") in {"independent", "exposure"}]
    dep = [v["name"] for v in variables if v.get("role") in {"dependent", "outcome"}]
    controls = [v["name"] for v in variables if v.get("role") in {"control", "covariate"}]
    relationships = []
    if indep and dep:
        relationships.append({
            "source_variable": indep[0],
            "target_variable": dep[0],
            "relationship_type": "positive_correlation",
            "strength": "moderate",
            "suggested_r": 0.35,
            "rationale": "Fallback relationship based on selected independent and dependent variables."
        })
    return {
        "conceptual_framework": {
            "summary": f"The study examines how selected predictors relate to selected outcomes in {topic}.",
            "independent_variables": indep,
            "dependent_variables": dep,
            "control_variables": controls,
            "mediators": [v["name"] for v in variables if v.get("role") == "mediator"],
            "moderators": [v["name"] for v in variables if v.get("role") == "moderator"],
            "mermaid": "flowchart LR\n  IV[Independent variables] --> DV[Dependent variables]\n  C[Control variables] -. adjust .-> DV",
        },
        "hypotheses": [
            {
                "code": "H1",
                "text": hypotheses_text or "There is an association between the main independent and dependent variables.",
                "null_hypothesis": "There is no association between the main independent and dependent variables.",
                "variables_involved": (indep[:1] + dep[:1]),
                "expected_direction": "positive",
                "suggested_test": "correlation/regression depending on variable types",
            }
        ],
        "relationships": relationships,
        "analysis_plan": ["Descriptive statistics", "Bivariate analysis", "Multivariable model if covariates are present"],
        "warnings": ["Heuristic framework used."],
    }
