from __future__ import annotations


def validate_sample_size(n: int) -> dict:
    if n < 1:
        return {"ok": False, "message": "Sample size must be at least 1."}
    if n < 30:
        return {"ok": True, "message": "Small sample. Many statistical tests may be underpowered."}
    if n > 100000:
        return {"ok": True, "message": "Large sample. Generation/export may take longer."}
    return {"ok": True, "message": "Sample size accepted."}
