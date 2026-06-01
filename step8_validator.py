from __future__ import annotations

import pandas as pd

from ai_client import call_ai_json
from json_utils import safe_json_dumps
from schema_models import GenerationSchema, ValidationIssue, ValidationReport
import config


SYSTEM = """
You are a research data plausibility reviewer.
You are reviewing a synthetic dataset profile, not real patient data.
Flag design, coding, and plausibility issues. Return valid JSON only.
"""


def mathematical_validation(df: pd.DataFrame, schema: dict) -> list[ValidationIssue]:
    parsed = GenerationSchema(**schema)
    issues: list[ValidationIssue] = []

    if len(df) != parsed.sample_size:
        issues.append(ValidationIssue(
            severity="error",
            location="dataset",
            message=f"Expected {parsed.sample_size} rows, found {len(df)}.",
        ))

    for v in parsed.variables:
        if v.name not in df.columns:
            issues.append(ValidationIssue(severity="error", location=v.name, message="Missing column."))
            continue

        s = df[v.name]

        if v.variable_type in {"continuous", "integer"}:
            numeric = pd.to_numeric(s, errors="coerce")
            if v.min_value is not None and (numeric.dropna() < v.min_value).any():
                issues.append(ValidationIssue(severity="error", location=v.name, message="Values below minimum."))
            if v.max_value is not None and (numeric.dropna() > v.max_value).any():
                issues.append(ValidationIssue(severity="error", location=v.name, message="Values above maximum."))

        if v.variable_type in {"binary", "categorical", "ordinal"} and v.categories:
            invalid = sorted(set(s.dropna().astype(str)) - set(map(str, v.categories)))
            if invalid:
                issues.append(ValidationIssue(
                    severity="error",
                    location=v.name,
                    message=f"Invalid categories found: {invalid}",
                ))

        missing_rate = float(s.isna().mean())
        if missing_rate > max(v.missing_rate + 0.10, 0.20):
            issues.append(ValidationIssue(
                severity="warning",
                location=v.name,
                message=f"Observed missingness {missing_rate:.2%} is higher than expected.",
            ))

    for rel in parsed.relationships:
        if rel.source_variable in df.columns and rel.target_variable in df.columns:
            xs = pd.to_numeric(df[rel.source_variable], errors="coerce")
            ys = pd.to_numeric(df[rel.target_variable], errors="coerce")
            if xs.notna().sum() > 3 and ys.notna().sum() > 3:
                corr = xs.corr(ys)
                if rel.suggested_r is not None and pd.notna(corr):
                    if abs(corr - rel.suggested_r) > 0.35:
                        issues.append(ValidationIssue(
                            severity="warning",
                            location=f"{rel.source_variable}->{rel.target_variable}",
                            message=f"Observed r={corr:.2f}, expected around {rel.suggested_r:.2f}.",
                        ))

    return issues


def ai_plausibility_review(df: pd.DataFrame, schema: dict) -> dict:
    profile = {
        "shape": df.shape,
        "columns": list(df.columns),
        "describe": df.describe(include="all").fillna("").astype(str).to_dict(),
        "sample_rows": df.head(8).fillna("").astype(str).to_dict(orient="records"),
    }
    prompt = f"""
Generation schema:
{safe_json_dumps(schema)}

Synthetic dataset profile:
{safe_json_dumps(profile)}

Return ONLY valid JSON:
{{
  "overall_plausibility": "pass/pass_with_warnings/fail",
  "major_issues": ["..."],
  "minor_issues": ["..."],
  "variable_specific_comments": [
    {{"variable": "...", "comment": "...", "severity": "info/warning/error"}}
  ],
  "recommended_fixes": ["..."]
}}
"""
    try:
        return call_ai_json(prompt=prompt, system=SYSTEM, max_tokens=3500)
    except Exception as exc:
        if not config.ALLOW_HEURISTIC_FALLBACK:
            raise
        return {
            "overall_plausibility": "not_reviewed",
            "major_issues": [],
            "minor_issues": [f"AI plausibility review unavailable: {exc}"],
            "variable_specific_comments": [],
            "recommended_fixes": ["Add GROQ_API_KEY or disable AI plausibility review."],
        }


def validate_dataset(df: pd.DataFrame, schema: dict, run_ai_review: bool = True) -> dict:
    issues = mathematical_validation(df, schema)
    ai_review = ai_plausibility_review(df, schema) if run_ai_review else {}

    ok = not any(issue.severity == "error" for issue in issues)
    report = ValidationReport(
        ok=ok,
        issues=issues,
        ai_plausibility=ai_review,
    )
    return report.model_dump()
