from __future__ import annotations

import numpy as np
import pandas as pd

from schema_models import GenerationSchema, VariableDefinition, Relationship


def _clip(series: np.ndarray, v: VariableDefinition) -> np.ndarray:
    if v.min_value is not None:
        series = np.maximum(series, v.min_value)
    if v.max_value is not None:
        series = np.minimum(series, v.max_value)
    return series


def _generate_variable(v: VariableDefinition, n: int, rng: np.random.Generator) -> pd.Series:
    if v.variable_type == "integer":
        mean = v.mean if v.mean is not None else 50
        sd = v.sd if v.sd is not None else 10
        data = rng.normal(mean, sd, n)
        data = np.rint(_clip(data, v)).astype(int)
        return pd.Series(data, name=v.name)

    if v.variable_type == "continuous":
        mean = v.mean if v.mean is not None else 50
        sd = v.sd if v.sd is not None else 10

        if v.distribution == "lognormal":
            sigma = 0.5
            mu = np.log(max(mean, 1)) - sigma**2 / 2
            data = rng.lognormal(mu, sigma, n)
        elif v.distribution == "uniform":
            low = v.min_value if v.min_value is not None else 0
            high = v.max_value if v.max_value is not None else 100
            data = rng.uniform(low, high, n)
        else:
            data = rng.normal(mean, sd, n)

        return pd.Series(_clip(data, v).round(3), name=v.name)

    if v.variable_type == "binary":
        categories = v.categories or ["No", "Yes"]
        p_yes = 0.5
        raw = rng.binomial(1, p_yes, n)
        return pd.Series([categories[int(x)] for x in raw], name=v.name)

    if v.variable_type in {"categorical", "ordinal"}:
        categories = v.categories or ["Group A", "Group B", "Group C"]
        raw = rng.choice(categories, size=n)
        return pd.Series(raw, name=v.name)

    if v.variable_type == "date":
        start = np.datetime64("2020-01-01")
        offsets = rng.integers(0, 365 * 5, size=n)
        return pd.Series(start + offsets.astype("timedelta64[D]"), name=v.name)

    return pd.Series([f"text_{i+1}" for i in range(n)], name=v.name)


def _numeric_standardize(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    sd = numeric.std()
    if sd == 0 or pd.isna(sd):
        return pd.Series(np.zeros(len(series)), index=series.index)
    return (numeric - numeric.mean()) / sd


def _apply_relationships(
    df: pd.DataFrame,
    variables: dict[str, VariableDefinition],
    relationships: list[Relationship],
    rng: np.random.Generator,
) -> pd.DataFrame:
    for rel in relationships:
        src = rel.source_variable
        tgt = rel.target_variable
        if src not in df.columns or tgt not in df.columns:
            continue
        if tgt not in variables or src not in variables:
            continue
        target_def = variables[tgt]
        if target_def.variable_type not in {"continuous", "integer"}:
            continue
        if variables[src].variable_type not in {"continuous", "integer"}:
            continue

        r = rel.suggested_r
        if r is None:
            r = {"weak": 0.2, "moderate": 0.45, "strong": 0.7}.get(rel.strength, 0.35)
            if rel.relationship_type in {"negative_correlation", "risk_decrease"}:
                r = -abs(r)
        r = max(min(r, 0.95), -0.95)

        z_src = _numeric_standardize(df[src])
        noise = pd.Series(rng.normal(0, 1, len(df)), index=df.index)
        z_target = r * z_src + np.sqrt(max(0.0, 1 - r**2)) * noise

        mean = target_def.mean if target_def.mean is not None else pd.to_numeric(df[tgt], errors="coerce").mean()
        sd = target_def.sd if target_def.sd is not None else pd.to_numeric(df[tgt], errors="coerce").std()
        if pd.isna(sd) or sd == 0:
            sd = 1

        values = (z_target * sd + mean).to_numpy()
        values = _clip(values, target_def)
        if target_def.variable_type == "integer":
            values = np.rint(values).astype(int)
        df[tgt] = values
    return df


def _apply_missingness(df: pd.DataFrame, variables: list[VariableDefinition], rng: np.random.Generator) -> pd.DataFrame:
    for v in variables:
        if v.missing_rate and v.name in df.columns:
            mask = rng.random(len(df)) < v.missing_rate
            df.loc[mask, v.name] = np.nan
    return df


def generate_dataset(schema: dict, seed: int | None = 42) -> pd.DataFrame:
    parsed = GenerationSchema(**schema)
    rng = np.random.default_rng(seed)

    columns = {}
    variables_by_name = {v.name: v for v in parsed.variables}
    for v in parsed.variables:
        columns[v.name] = _generate_variable(v, parsed.sample_size, rng)

    df = pd.DataFrame(columns)
    df = _apply_relationships(df, variables_by_name, parsed.relationships, rng)
    df = _apply_missingness(df, parsed.variables, rng)
    return df
