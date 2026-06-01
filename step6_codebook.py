from __future__ import annotations

from schema_models import GenerationSchema, VariableDefinition, Relationship


def build_codebook(variables: list[dict]) -> list[dict]:
    codebook = []
    for index, variable in enumerate(variables, start=1):
        v = VariableDefinition(**variable)
        codebook.append({
            "order": index,
            "name": v.name,
            "label": v.label or v.name.replace("_", " ").title(),
            "role": v.role,
            "type": v.variable_type,
            "definition": v.definition,
            "unit": v.unit,
            "range": (
                f"{v.min_value} to {v.max_value}"
                if v.min_value is not None or v.max_value is not None
                else ""
            ),
            "categories": v.categories,
            "coding": v.coding,
            "missing_rate": v.missing_rate,
            "notes": v.notes,
        })
    return codebook


def build_generation_schema(
    study_title: str,
    sample_size: int,
    study_design: str,
    population: str,
    variables: list[dict],
    relationships: list[dict] | None = None,
) -> dict:
    schema = GenerationSchema(
        study_title=study_title,
        sample_size=sample_size,
        study_design=study_design,
        population=population,
        variables=[VariableDefinition(**v) for v in variables],
        relationships=[Relationship(**r) for r in (relationships or [])],
    )
    return schema.model_dump()
