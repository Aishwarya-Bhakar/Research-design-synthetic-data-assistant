from __future__ import annotations

import math
from typing import Iterable

import numpy as np
import pandas as pd

from schema_models import GenerationSchema, Relationship, VariableDefinition


STRENGTH_TO_R = {
    "weak": 0.20,
    "moderate": 0.45,
    "strong": 0.70,
}

NEGATIVE_RELATIONSHIP_TYPES = {"negative_correlation", "risk_decrease"}
POSITIVE_RELATIONSHIP_TYPES = {"positive_correlation", "risk_increase", "group_difference"}


# -----------------------------------------------------------------------------
# Numeric generation helpers
# -----------------------------------------------------------------------------


def _finite_number(value: object) -> float | None:
    try:
        x = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    if not math.isfinite(x):
        return None
    return x


def _bounds(v: VariableDefinition) -> tuple[float | None, float | None]:
    low = _finite_number(v.min_value)
    high = _finite_number(v.max_value)
    if low is not None and high is not None and high <= low:
        high = low + 1.0
    return low, high


def _range_width(v: VariableDefinition) -> float | None:
    low, high = _bounds(v)
    if low is None or high is None:
        return None
    return high - low


def _default_mean_for_variable(v: VariableDefinition) -> float:
    """Choose a sane default mean when AI gives no mean or an impossible mean.

    The old generator accepted AI means blindly. If AI suggested mean=50 for a
    variable bounded 0-6, clipping turned every value into 6. This function keeps
    the center inside the defined range.
    """

    low, high = _bounds(v)
    width = _range_width(v)
    name = v.name.lower()

    if low is not None and high is not None:
        midpoint = low + (high - low) / 2

        # Hour variables are usually right-skewed, not centered at maximum.
        if "hour" in name or "screen_time" in name:
            return low + (high - low) * 0.40

        # Scores often occupy mid-range in synthetic examples unless user gives a mean.
        if "score" in name or "scale" in name or "index" in name:
            return midpoint

        return midpoint

    if low is not None and high is None:
        return low + 10

    if low is None and high is not None:
        return high - 10

    if "age" in name:
        return 35
    if "hour" in name:
        return 3
    if "score" in name:
        return 50
    return 50


def _default_sd_for_variable(v: VariableDefinition) -> float:
    width = _range_width(v)
    name = v.name.lower()

    if width is not None:
        # Approx. 99.7% of a normal variable lies inside +/- 3 SD.
        # This prevents heavy clipping at the boundaries.
        if "age" in name:
            return max(width / 5, 0.5)
        if "score" in name or "scale" in name or "index" in name:
            return max(width / 5, 0.5)
        return max(width / 6, 0.5)

    if "age" in name:
        return 8
    if "hour" in name:
        return 2
    if "score" in name:
        return 10
    return 10


def _safe_mean_sd(v: VariableDefinition) -> tuple[float, float]:
    low, high = _bounds(v)
    width = _range_width(v)

    mean = _finite_number(v.mean)
    sd = _finite_number(v.sd)

    if mean is None:
        mean = _default_mean_for_variable(v)

    if low is not None and mean < low:
        mean = _default_mean_for_variable(v)
    if high is not None and mean > high:
        mean = _default_mean_for_variable(v)

    if low is not None and high is not None:
        mean = min(max(mean, low), high)

    if sd is None or sd <= 0:
        sd = _default_sd_for_variable(v)

    if width is not None:
        # Keep SD small enough that values are not collapsed by clipping.
        sd = min(sd, max(width / 3, 0.1))
        sd = max(sd, max(width / 20, 0.05))

    return float(mean), float(sd)


def _clip_array(values: np.ndarray, v: VariableDefinition) -> np.ndarray:
    low, high = _bounds(v)
    if low is not None:
        values = np.maximum(values, low)
    if high is not None:
        values = np.minimum(values, high)
    return values


def _truncated_normal(
    mean: float,
    sd: float,
    n: int,
    rng: np.random.Generator,
    low: float | None = None,
    high: float | None = None,
) -> np.ndarray:
    """Generate bounded normal data by resampling, not by immediate clipping."""

    if n <= 0:
        return np.array([], dtype=float)

    values = rng.normal(mean, sd, n)

    if low is None and high is None:
        return values

    invalid = np.zeros(n, dtype=bool)
    if low is not None:
        invalid |= values < low
    if high is not None:
        invalid |= values > high

    # Resample invalid values several times before final clipping.
    # This maintains variation near bounds and avoids all-max/all-min columns.
    attempts = 0
    while invalid.any() and attempts < 50:
        values[invalid] = rng.normal(mean, sd, int(invalid.sum()))
        invalid = np.zeros(n, dtype=bool)
        if low is not None:
            invalid |= values < low
        if high is not None:
            invalid |= values > high
        attempts += 1

    return _clip_array(values, _dummy_variable_for_bounds(low, high))


def _dummy_variable_for_bounds(low: float | None, high: float | None) -> VariableDefinition:
    return VariableDefinition(name="_dummy", min_value=low, max_value=high)


def _ensure_variation(values: np.ndarray, v: VariableDefinition, rng: np.random.Generator) -> np.ndarray:
    """Repair accidental constant numeric columns."""

    if len(values) <= 1:
        return values

    numeric = pd.Series(values).dropna()
    if numeric.nunique() > 1:
        return values

    low, high = _bounds(v)
    if low is not None and high is not None and high > low:
        if v.variable_type == "integer":
            repaired = rng.integers(math.floor(low), math.ceil(high) + 1, len(values))
            return repaired.astype(float)
        return rng.uniform(low, high, len(values))

    mean, sd = _safe_mean_sd(v)
    return rng.normal(mean, sd, len(values))


# -----------------------------------------------------------------------------
# Variable generation
# -----------------------------------------------------------------------------


def _generate_integer(v: VariableDefinition, n: int, rng: np.random.Generator) -> pd.Series:
    low, high = _bounds(v)
    mean, sd = _safe_mean_sd(v)

    if v.distribution == "poisson":
        lam = max(mean, 0.1)
        data = rng.poisson(lam, n).astype(float)
    elif v.distribution == "uniform" and low is not None and high is not None:
        data = rng.integers(math.floor(low), math.ceil(high) + 1, n).astype(float)
    else:
        data = _truncated_normal(mean, sd, n, rng, low, high)

    data = _clip_array(data, v)
    data = _ensure_variation(data, v, rng)
    data = _clip_array(data, v)
    return pd.Series(np.rint(data).astype(int), name=v.name)


def _generate_continuous(v: VariableDefinition, n: int, rng: np.random.Generator) -> pd.Series:
    low, high = _bounds(v)
    mean, sd = _safe_mean_sd(v)

    if v.distribution == "uniform" and low is not None and high is not None:
        data = rng.uniform(low, high, n)
    elif v.distribution == "lognormal":
        # Use lognormal shape but rescale into the allowed range when bounded.
        sigma = 0.55
        mu = np.log(max(mean, 0.1)) - sigma**2 / 2
        data = rng.lognormal(mu, sigma, n)
        if low is not None and high is not None and high > low:
            p_low, p_high = np.percentile(data, [2, 98])
            if p_high > p_low:
                data = (data - p_low) / (p_high - p_low)
                data = low + np.clip(data, 0, 1) * (high - low)
            else:
                data = rng.uniform(low, high, n)
        else:
            data = _clip_array(data, v)
    else:
        data = _truncated_normal(mean, sd, n, rng, low, high)

    data = _clip_array(data, v)
    data = _ensure_variation(data, v, rng)
    data = _clip_array(data, v)
    return pd.Series(np.round(data, 3), name=v.name)


def _generate_binary(v: VariableDefinition, n: int, rng: np.random.Generator) -> pd.Series:
    categories = v.categories or ["No", "Yes"]
    if len(categories) == 1:
        categories = [categories[0], f"Not {categories[0]}"]
    categories = categories[:2]

    # Keep binary variables varied by avoiding extreme base probabilities.
    p_yes = 0.50
    raw = rng.binomial(1, p_yes, n)
    return pd.Series([categories[int(x)] for x in raw], name=v.name)


def _category_probabilities(categories: list[str], rng: np.random.Generator) -> np.ndarray:
    if not categories:
        return np.array([], dtype=float)
    if len(categories) == 1:
        return np.array([1.0], dtype=float)

    # Mildly uneven probabilities look more realistic than perfectly uniform,
    # but every category remains possible.
    weights = rng.uniform(0.8, 1.2, len(categories))
    return weights / weights.sum()


def _generate_categorical(v: VariableDefinition, n: int, rng: np.random.Generator) -> pd.Series:
    categories = v.categories or ["Group A", "Group B", "Group C"]
    probabilities = _category_probabilities(categories, rng)
    data = rng.choice(categories, size=n, p=probabilities)
    return pd.Series(data, name=v.name)


def _generate_ordinal(v: VariableDefinition, n: int, rng: np.random.Generator) -> pd.Series:
    categories = v.categories or ["Low", "Moderate", "High"]
    if len(categories) <= 2:
        return _generate_categorical(v, n, rng)

    # Center-weighted ordinal distribution.
    center = (len(categories) - 1) / 2
    weights = np.array([1 / (1 + abs(i - center)) for i in range(len(categories))], dtype=float)
    weights = weights / weights.sum()
    data = rng.choice(categories, size=n, p=weights)
    return pd.Series(data, name=v.name)


def _generate_date(v: VariableDefinition, n: int, rng: np.random.Generator) -> pd.Series:
    start = np.datetime64("2020-01-01")
    offsets = rng.integers(0, 365 * 5, size=n)
    return pd.Series(start + offsets.astype("timedelta64[D]"), name=v.name)


def _generate_variable(v: VariableDefinition, n: int, rng: np.random.Generator) -> pd.Series:
    if v.variable_type == "integer":
        return _generate_integer(v, n, rng)
    if v.variable_type == "continuous":
        return _generate_continuous(v, n, rng)
    if v.variable_type == "binary":
        return _generate_binary(v, n, rng)
    if v.variable_type == "categorical":
        return _generate_categorical(v, n, rng)
    if v.variable_type == "ordinal":
        return _generate_ordinal(v, n, rng)
    if v.variable_type == "date":
        return _generate_date(v, n, rng)
    return pd.Series([f"text_{i + 1}" for i in range(n)], name=v.name)


# -----------------------------------------------------------------------------
# Relationship handling
# -----------------------------------------------------------------------------


def _as_numeric_codes(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().sum() >= max(3, len(series) // 4):
        return numeric

    codes, _ = pd.factorize(series.astype(str), sort=True)
    return pd.Series(codes.astype(float), index=series.index)


def _standardize(series: pd.Series) -> pd.Series:
    numeric = _as_numeric_codes(series)
    sd = numeric.std()
    if pd.isna(sd) or sd == 0:
        return pd.Series(np.zeros(len(series)), index=series.index)
    return (numeric - numeric.mean()) / sd


def _relationship_r(rel: Relationship) -> float:
    r = rel.suggested_r
    if r is None:
        r = STRENGTH_TO_R.get(rel.strength, 0.35)

    if rel.relationship_type in NEGATIVE_RELATIONSHIP_TYPES:
        r = -abs(r)
    elif rel.relationship_type in POSITIVE_RELATIONSHIP_TYPES:
        r = abs(r)

    return float(max(min(r, 0.90), -0.90))


def _apply_numeric_target_relationship(
    df: pd.DataFrame,
    src: str,
    tgt: str,
    target_def: VariableDefinition,
    rel: Relationship,
    rng: np.random.Generator,
) -> None:
    r = _relationship_r(rel)
    z_src = _standardize(df[src])

    if z_src.std() == 0 or pd.isna(z_src.std()):
        return

    noise = pd.Series(rng.normal(0, 1, len(df)), index=df.index)
    z_target = r * z_src + np.sqrt(max(0.0, 1 - r**2)) * noise

    mean, sd = _safe_mean_sd(target_def)
    values = (z_target.to_numpy() * sd) + mean
    values = _clip_array(values, target_def)
    values = _ensure_variation(values, target_def, rng)
    values = _clip_array(values, target_def)

    if target_def.variable_type == "integer":
        df[tgt] = np.rint(values).astype(int)
    else:
        df[tgt] = np.round(values, 3)


def _apply_binary_target_relationship(
    df: pd.DataFrame,
    src: str,
    tgt: str,
    target_def: VariableDefinition,
    rel: Relationship,
    rng: np.random.Generator,
) -> None:
    categories = target_def.categories or ["No", "Yes"]
    if len(categories) == 1:
        categories = [categories[0], f"Not {categories[0]}"]
    categories = categories[:2]

    r = _relationship_r(rel)
    z_src = _standardize(df[src])
    if z_src.std() == 0 or pd.isna(z_src.std()):
        return

    # Strength controls slope of logistic probability.
    beta = abs(r) * 2.4
    if r < 0:
        beta = -beta
    logits = beta * z_src.to_numpy()
    probabilities = 1 / (1 + np.exp(-logits))
    probabilities = np.clip(probabilities, 0.05, 0.95)

    raw = rng.binomial(1, probabilities)
    df[tgt] = [categories[int(x)] for x in raw]


def _apply_numeric_relationship_group(
    df: pd.DataFrame,
    target: str,
    target_def: VariableDefinition,
    rels: list[Relationship],
    rng: np.random.Generator,
) -> None:
    usable: list[tuple[Relationship, pd.Series, float]] = []

    for rel in rels:
        src = rel.source_variable
        if src not in df.columns:
            continue
        r = _relationship_r(rel)
        z_src = _standardize(df[src])
        if z_src.std() == 0 or pd.isna(z_src.std()):
            continue
        usable.append((rel, z_src, r))

    if not usable:
        return

    # Combine all predictors for the same target instead of overwriting the
    # target repeatedly. The previous implementation applied relationships one
    # by one, so the last relationship could erase the earlier one.
    requested = np.array([r for _, _, r in usable], dtype=float)
    requested_sumsq = float(np.sum(requested**2))

    if requested_sumsq <= 0:
        return

    signal_strength = min(math.sqrt(requested_sumsq), 0.90)
    weights = requested / math.sqrt(requested_sumsq)

    combined = np.zeros(len(df), dtype=float)
    for weight, (_, z_src, _) in zip(weights, usable):
        combined += weight * z_src.to_numpy()

    combined_series = pd.Series(combined, index=df.index)
    combined_sd = combined_series.std()
    if pd.notna(combined_sd) and combined_sd > 0:
        combined = ((combined_series - combined_series.mean()) / combined_sd).to_numpy()

    noise = rng.normal(0, 1, len(df))
    z_target = signal_strength * combined + np.sqrt(max(0.0, 1 - signal_strength**2)) * noise

    mean, sd = _safe_mean_sd(target_def)
    values = (z_target * sd) + mean
    values = _clip_array(values, target_def)
    values = _ensure_variation(values, target_def, rng)
    values = _clip_array(values, target_def)

    if target_def.variable_type == "integer":
        df[target] = np.rint(values).astype(int)
    else:
        df[target] = np.round(values, 3)


def _apply_binary_relationship_group(
    df: pd.DataFrame,
    target: str,
    target_def: VariableDefinition,
    rels: list[Relationship],
    rng: np.random.Generator,
) -> None:
    categories = target_def.categories or ["No", "Yes"]
    if len(categories) == 1:
        categories = [categories[0], f"Not {categories[0]}"]
    categories = categories[:2]

    logits = np.zeros(len(df), dtype=float)
    usable = 0

    for rel in rels:
        src = rel.source_variable
        if src not in df.columns:
            continue
        z_src = _standardize(df[src])
        if z_src.std() == 0 or pd.isna(z_src.std()):
            continue
        r = _relationship_r(rel)
        logits += (abs(r) * 2.4) * np.sign(r) * z_src.to_numpy()
        usable += 1

    if usable == 0:
        return

    logits = logits / max(math.sqrt(usable), 1.0)
    probabilities = 1 / (1 + np.exp(-logits))
    probabilities = np.clip(probabilities, 0.05, 0.95)
    raw = rng.binomial(1, probabilities)
    df[target] = [categories[int(x)] for x in raw]


def _apply_relationships(
    df: pd.DataFrame,
    variables: dict[str, VariableDefinition],
    relationships: Iterable[Relationship],
    rng: np.random.Generator,
) -> pd.DataFrame:
    grouped: dict[str, list[Relationship]] = {}

    for rel in relationships:
        if rel.relationship_type == "no_expected_relationship":
            continue
        if rel.source_variable not in df.columns or rel.target_variable not in df.columns:
            continue
        if rel.source_variable not in variables or rel.target_variable not in variables:
            continue
        grouped.setdefault(rel.target_variable, []).append(rel)

    for target, rels in grouped.items():
        target_def = variables[target]
        if target_def.variable_type in {"continuous", "integer"}:
            _apply_numeric_relationship_group(df, target, target_def, rels, rng)
        elif target_def.variable_type == "binary":
            _apply_binary_relationship_group(df, target, target_def, rels, rng)

    return df

def _apply_missingness(
    df: pd.DataFrame,
    variables: list[VariableDefinition],
    rng: np.random.Generator,
) -> pd.DataFrame:
    for v in variables:
        if v.missing_rate and v.name in df.columns:
            mask = rng.random(len(df)) < v.missing_rate
            df.loc[mask, v.name] = np.nan
    return df


def generate_dataset(schema: dict, seed: int | None = 42) -> pd.DataFrame:
    parsed = GenerationSchema(**schema)
    rng = np.random.default_rng(seed)

    variables_by_name = {v.name: v for v in parsed.variables}
    columns = {
        v.name: _generate_variable(v, parsed.sample_size, rng)
        for v in parsed.variables
    }

    df = pd.DataFrame(columns).reset_index(drop=True)
    df = _apply_relationships(df, variables_by_name, parsed.relationships, rng)
    df = _apply_missingness(df, parsed.variables, rng)
    return df.reset_index(drop=True)

