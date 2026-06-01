from heuristics import infer_variable_type


def test_age_inference():
    meta = infer_variable_type("age")
    assert meta["variable_type"] == "integer"
    assert meta["min_value"] == 18


def test_category_inference():
    meta = infer_variable_type("gender")
    assert meta["variable_type"] == "categorical"
