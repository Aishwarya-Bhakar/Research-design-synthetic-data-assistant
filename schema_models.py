from __future__ import annotations

from typing import Literal, Any
from pydantic import BaseModel, Field, field_validator


VariableRole = Literal[
    "independent",
    "dependent",
    "control",
    "covariate",
    "mediator",
    "moderator",
    "exposure",
    "outcome",
    "grouping",
    "identifier",
]

VariableType = Literal["continuous", "integer", "binary", "categorical", "ordinal", "date", "text"]

DistributionType = Literal["normal", "lognormal", "uniform", "poisson", "bernoulli", "categorical", "ordinal", "date", "text"]


class VariableDefinition(BaseModel):
    name: str
    label: str = ""
    role: VariableRole = "covariate"
    variable_type: VariableType = "continuous"
    definition: str = ""
    unit: str = ""
    min_value: float | None = None
    max_value: float | None = None
    categories: list[str] = Field(default_factory=list)
    distribution: DistributionType = "normal"
    mean: float | None = None
    sd: float | None = None
    missing_rate: float = 0.0
    coding: str = ""
    notes: str = ""

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        cleaned = value.strip().lower().replace(" ", "_").replace("-", "_")
        if not cleaned:
            raise ValueError("variable name cannot be empty")
        return cleaned

    @field_validator("missing_rate")
    @classmethod
    def valid_missing_rate(cls, value: float) -> float:
        if value < 0 or value > 0.8:
            raise ValueError("missing_rate must be between 0 and 0.8")
        return value


class Relationship(BaseModel):
    source_variable: str
    target_variable: str
    relationship_type: Literal[
        "positive_correlation",
        "negative_correlation",
        "group_difference",
        "risk_increase",
        "risk_decrease",
        "no_expected_relationship",
    ] = "positive_correlation"
    strength: Literal["weak", "moderate", "strong"] = "moderate"
    suggested_r: float | None = None
    rationale: str = ""


class Hypothesis(BaseModel):
    code: str
    text: str
    null_hypothesis: str = ""
    variables_involved: list[str] = Field(default_factory=list)
    expected_direction: str = ""
    suggested_test: str = ""


class GenerationSchema(BaseModel):
    study_title: str
    sample_size: int = Field(ge=1, le=1_000_000)
    study_design: str
    population: str = ""
    variables: list[VariableDefinition]
    relationships: list[Relationship] = Field(default_factory=list)

    @field_validator("variables")
    @classmethod
    def unique_variables(cls, variables: list[VariableDefinition]) -> list[VariableDefinition]:
        names = [v.name for v in variables]
        if len(names) != len(set(names)):
            raise ValueError("variable names must be unique")
        return variables


class ValidationIssue(BaseModel):
    severity: Literal["info", "warning", "error"]
    location: str
    message: str


class ValidationReport(BaseModel):
    ok: bool
    issues: list[ValidationIssue] = Field(default_factory=list)
    ai_plausibility: dict[str, Any] = Field(default_factory=dict)
