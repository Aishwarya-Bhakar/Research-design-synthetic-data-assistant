from step6_codebook import build_generation_schema
from step7_generator import generate_dataset
from step8_validator import mathematical_validation


def sample_variables():
    return [
        {
            "name": "age",
            "label": "Age",
            "role": "control",
            "variable_type": "integer",
            "definition": "Age in years",
            "unit": "years",
            "min_value": 18,
            "max_value": 65,
            "categories": [],
            "distribution": "normal",
            "mean": 35,
            "sd": 10,
            "missing_rate": 0.0,
            "coding": "",
            "notes": "",
        },
        {
            "name": "sleep_quality_score",
            "label": "Sleep quality score",
            "role": "dependent",
            "variable_type": "continuous",
            "definition": "Sleep quality scale",
            "unit": "score",
            "min_value": 0,
            "max_value": 100,
            "categories": [],
            "distribution": "normal",
            "mean": 55,
            "sd": 12,
            "missing_rate": 0.0,
            "coding": "",
            "notes": "",
        },
        {
            "name": "gender",
            "label": "Gender",
            "role": "control",
            "variable_type": "categorical",
            "definition": "Gender category",
            "unit": "",
            "min_value": None,
            "max_value": None,
            "categories": ["Female", "Male", "Other"],
            "distribution": "categorical",
            "mean": None,
            "sd": None,
            "missing_rate": 0.0,
            "coding": "Female/Male/Other",
            "notes": "",
        },
    ]


def test_generate_dataset_and_validate():
    schema = build_generation_schema(
        study_title="Test study",
        sample_size=50,
        study_design="cross-sectional",
        population="Adults",
        variables=sample_variables(),
        relationships=[
            {
                "source_variable": "age",
                "target_variable": "sleep_quality_score",
                "relationship_type": "negative_correlation",
                "strength": "moderate",
                "suggested_r": -0.4,
                "rationale": "Test relation",
            }
        ],
    )
    df = generate_dataset(schema, seed=1)
    assert df.shape == (50, 3)
    issues = mathematical_validation(df, schema)
    assert not any(issue.severity == "error" for issue in issues)
