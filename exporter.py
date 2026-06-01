from __future__ import annotations

import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from datetime import datetime

import pandas as pd


def export_bundle(
    output_dir: str | Path,
    dataset: pd.DataFrame,
    literature_summary: dict,
    codebook: list[dict],
    generation_schema: dict,
    validation_report: dict,
) -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    dataset_csv = out / "synthetic_dataset.csv"
    dataset_xlsx = out / "synthetic_dataset.xlsx"
    literature_json = out / "literature_summary.json"
    codebook_json = out / "codebook.json"
    schema_json = out / "generation_schema.json"
    validation_json = out / "validation_report.json"

    dataset.to_csv(dataset_csv, index=False)
    with pd.ExcelWriter(dataset_xlsx, engine="openpyxl") as writer:
        dataset.to_excel(writer, index=False, sheet_name="Synthetic Data")
        pd.DataFrame(codebook).to_excel(writer, index=False, sheet_name="Codebook")

    for path, data in [
        (literature_json, literature_summary),
        (codebook_json, codebook),
        (schema_json, generation_schema),
        (validation_json, validation_report),
    ]:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    zip_path = out / f"research_assistant_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    with ZipFile(zip_path, "w", ZIP_DEFLATED) as z:
        for file in [dataset_csv, dataset_xlsx, literature_json, codebook_json, schema_json, validation_json]:
            z.write(file, arcname=file.name)

    return zip_path
