from __future__ import annotations

from collections import OrderedDict

import config
from literature.models import LiteraturePaper
from literature import pubmed_client, crossref_client


def search_literature(
    topic: str,
    sources: list[str] | None = None,
    max_results: int | None = None,
) -> list[dict]:
    sources = sources or ["Crossref", "PubMed"]
    max_results = max_results or config.LITERATURE_MAX_RESULTS

    papers: list[LiteraturePaper] = []
    errors: list[str] = []

    if "PubMed" in sources:
        if pubmed_client.enabled():
            try:
                papers.extend(pubmed_client.search(topic, max_results=max_results))
            except Exception as exc:
                errors.append(f"PubMed error: {exc}")
        else:
            errors.append("PubMed skipped: NCBI_EMAIL is missing.")

    if "Crossref" in sources:
        try:
            papers.extend(crossref_client.search(topic, max_results=max_results))
        except Exception as exc:
            errors.append(f"Crossref error: {exc}")

    unique: OrderedDict[str, LiteraturePaper] = OrderedDict()
    for paper in papers:
        key = (paper.doi or paper.url or paper.id or paper.title).lower()
        if key and key not in unique:
            unique[key] = paper

    result = [paper.to_dict() for paper in unique.values()]
    if errors:
        result.append({
            "source": "system",
            "id": "search_warnings",
            "title": "Search warnings",
            "authors": "",
            "year": "",
            "journal": "",
            "abstract": " | ".join(errors),
            "doi": "",
            "url": "",
        })
    return result
