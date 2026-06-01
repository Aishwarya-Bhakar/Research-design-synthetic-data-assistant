from __future__ import annotations

import pandas as pd

from ai_client import call_ai_json
from json_utils import safe_json_dumps
from schema_models import GenerationSchema, ValidationIssue, ValidationReport
import config


SYSTEM = """
You are a research data plausibility reviewer.
You are reviewing a synthetic dataset profile, not real patient data.
Flag design, coding, distribution, relationship, and plausibility issues.
Return valid JSON only.
"""


STRENGTH_TO_R = {"weak": 0.20, "moderate": 0.45, "strong": 0.70}
NEGATIVE_RELATIONSHIP_TYPES = {"negative_correlation", "risk_decrease"}
POSITIVE_RELATIONSHIP_TYPES = {"positive_correlation", "risk_increase", "group_difference"}


def _relationship_expected_r(rel) -> float:
    r = rel.suggested_r
    if r is None:
        r = STRENGTH_TO_R.get(rel.strength, 0.35)

    if rel.relationship_type in NEGATIVE_RELATIONSHIP_TYPES:
        r = -abs(r)
    elif rel.relationship_type in POSITIVE_RELATIONSHIP_TYPES:
        r = abs(r)

    return float(max(min(r, 0.90), -0.90))


def _as_numeric_codes(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().sum() >= max(3, len(series) // 4):
        return numeric
    codes, _ = pd.factorize(series.astype(str), sort=True)
    return pd.Series(codes.astype(float), index=series.index)


def build_data_profile(df: pd.DataFrame, schema: dict) -> dict:
    parsed = GenerationSchema(**schema)
    profile: dict = {
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "variables": [],
        "relationships": [],
    }

    for v in parsed.variables:
        if v.name not in df.columns:
            continue

        s = df[v.name]
        item = {
            "name": v.name,
            "type": v.variable_type,
            "missing_rate": round(float(s.isna().mean()), 4),
            "unique_values": int(s.nunique(dropna=True)),
        }

        if v.variable_type in {"continuous", "integer"}:
            numeric = pd.to_numeric(s, errors="coerce")
            item.update({
                "min": None if numeric.dropna().empty else round(float(numeric.min()), 4),
                "max": None if numeric.dropna().empty else round(float(numeric.max()), 4),
                "mean": None if numeric.dropna().empty else round(float(numeric.mean()), 4),
                "sd": None if numeric.dropna().empty else round(float(numeric.std()), 4),
            })
        else:
            item["top_values"] = s.astype(str).value_counts(dropna=False).head(5).to_dict()

        profile["variables"].append(item)

    for rel in parsed.relationships:
        if rel.source_variable in df.columns and rel.target_variable in df.columns:
            xs = _as_numeric_codes(df[rel.source_variable])
            ys = _as_numeric_codes(df[rel.target_variable])
            corr = xs.corr(ys)
            profile["relationships"].append({
                "source": rel.source_variable,
                "target": rel.target_variable,
                "relationship_type": rel.relationship_type,
                "expected_r": round(_relationship_expected_r(rel), 3),
                "observed_r": None if pd.isna(corr) else round(float(corr), 3),
            })

    return profile


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
        unique_count = int(s.nunique(dropna=True))

        if unique_count <= 1 and len(s.dropna()) > 1:
            severity = "error" if v.variable_type in {"continuous", "integer"} else "warning"
            issues.append(ValidationIssue(
                severity=severity,
                location=v.name,
                message="Variable has no variation. Synthetic data should not be constant unless it is an identifier or fixed design field.",
            ))

        if v.variable_type in {"continuous", "integer"}:
            numeric = pd.to_numeric(s, errors="coerce")
            observed = numeric.dropna()

            if observed.empty:
                issues.append(ValidationIssue(severity="error", location=v.name, message="Numeric variable contains no numeric values."))
                continue

            if v.min_value is not None and (observed < v.min_value).any():
                issues.append(ValidationIssue(severity="error", location=v.name, message="Values below minimum."))
            if v.max_value is not None and (observed > v.max_value).any():
                issues.append(ValidationIssue(severity="error", location=v.name, message="Values above maximum."))

            sd = observed.std()
            if pd.notna(sd) and sd == 0:
                issues.append(ValidationIssue(
                    severity="error",
                    location=v.name,
                    message="Numeric variable standard deviation is zero.",
                ))

            if v.min_value is not None:
                at_min = float((observed == v.min_value).mean())
                if at_min > 0.35:
                    issues.append(ValidationIssue(
                        severity="warning",
                        location=v.name,
                        message=f"{at_min:.0%} of values are exactly at the minimum. This suggests clipping or poor distribution settings.",
                    ))
            if v.max_value is not None:
                at_max = float((observed == v.max_value).mean())
                if at_max > 0.35:
                    issues.append(ValidationIssue(
                        severity="warning",
                        location=v.name,
                        message=f"{at_max:.0%} of values are exactly at the maximum. This suggests clipping or poor distribution settings.",
                    ))

        if v.variable_type in {"binary", "categorical", "ordinal"} and v.categories:
            invalid = sorted(set(s.dropna().astype(str)) - set(map(str, v.categories)))
            if invalid:
                issues.append(ValidationIssue(
                    severity="error",
                    location=v.name,
                    message=f"Invalid categories found: {invalid}",
                ))

            if unique_count < min(2, len(v.categories)) and len(s.dropna()) > 1:
                issues.append(ValidationIssue(
                    severity="warning",
                    location=v.name,
                    message="Categorical variable uses too few categories.",
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
            xs = _as_numeric_codes(df[rel.source_variable])
            ys = _as_numeric_codes(df[rel.target_variable])
            if xs.notna().sum() > 3 and ys.notna().sum() > 3:
                corr = xs.corr(ys)
                if pd.isna(corr):
                    issues.append(ValidationIssue(
                        severity="warning",
                        location=f"{rel.source_variable}->{rel.target_variable}",
                        message="Observed relationship could not be calculated.",
                    ))
                    continue

                expected = _relationship_expected_r(rel)
                if expected > 0 and corr < -0.05:
                    issues.append(ValidationIssue(
                        severity="warning",
                        location=f"{rel.source_variable}->{rel.target_variable}",
                        message=f"Observed r={corr:.2f}; expected positive relationship.",
                    ))
                elif expected < 0 and corr > 0.05:
                    issues.append(ValidationIssue(
                        severity="warning",
                        location=f"{rel.source_variable}->{rel.target_variable}",
                        message=f"Observed r={corr:.2f}; expected negative relationship.",
                    ))
                elif abs(corr - expected) > 0.30:
                    issues.append(ValidationIssue(
                        severity="warning",
                        location=f"{rel.source_variable}->{rel.target_variable}",
                        message=f"Observed r={corr:.2f}, expected around {expected:.2f}.",
                    ))

    return issues


def ai_plausibility_review(df: pd.DataFrame, schema: dict) -> dict:
    profile = {
        "shape": df.shape,
        "columns": list(df.columns),
        "data_quality_profile": build_data_profile(df, schema),
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
    ).model_dump()
    report["data_quality_profile"] = build_data_profile(df, schema)
    return report

