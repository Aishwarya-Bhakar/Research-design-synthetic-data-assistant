from json_utils import extract_json


def test_extract_plain_json():
    assert extract_json('{"a": 1}') == {"a": 1}


def test_extract_fenced_json():
    assert extract_json('```json\n{"a": 1}\n```') == {"a": 1}


def test_extract_embedded_json():
    assert extract_json('Here:\n{"a": 1}\nDone') == {"a": 1}
