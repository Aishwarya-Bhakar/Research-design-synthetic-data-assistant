from __future__ import annotations

import re
from html import unescape
from typing import Any

import requests

import config
from literature.models import LiteraturePaper


CROSSREF_WORKS_URL = "https://api.crossref.org/works"


def _first(value: Any, default: str = "") -> str:
    if isinstance(value, list) and value:
        return str(value[0])
    if isinstance(value, str):
        return value
    return default


def _strip_html(text: str) -> str:
    text = unescape(text or "")
    return re.sub(r"<[^>]+>", " ", text).strip()


def _authors(authors: list[dict[str, Any]]) -> str:
    names = []
    for author in authors[:4]:
        given = author.get("given", "")
        family = author.get("family", "")
        name = f"{given} {family}".strip()
        if name:
            names.append(name)
    if len(authors) > 4:
        names.append("et al.")
    return ", ".join(names)


def _year(item: dict[str, Any]) -> str:
    for key in ["published-print", "published-online", "issued", "created"]:
        parts = item.get(key, {}).get("date-parts", [])
        if parts and parts[0]:
            return str(parts[0][0])
    return ""


def search(topic: str, max_results: int = 8) -> list[LiteraturePaper]:
    params = {
        "query": topic,
        "rows": max_results,
        "select": "DOI,title,author,published-print,published-online,issued,created,container-title,abstract,URL",
    }
    if config.CROSSREF_MAILTO:
        params["mailto"] = config.CROSSREF_MAILTO

    response = requests.get(CROSSREF_WORKS_URL, params=params, timeout=20)
    response.raise_for_status()
    items = response.json().get("message", {}).get("items", [])

    papers: list[LiteraturePaper] = []
    for item in items:
        doi = item.get("DOI", "")
        title = _first(item.get("title", []))
        journal = _first(item.get("container-title", []))
        url = item.get("URL", "")
        abstract = _strip_html(item.get("abstract", ""))
        authors = _authors(item.get("author", []))
        year = _year(item)

        if not title:
            continue

        papers.append(
            LiteraturePaper(
                source="Crossref",
                id=doi or url,
                title=title,
                authors=authors,
                year=year,
                journal=journal,
                abstract=abstract,
                doi=doi,
                url=url,
            )
        )
    return papers
