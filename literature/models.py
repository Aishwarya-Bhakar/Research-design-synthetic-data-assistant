from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class LiteraturePaper:
    source: str
    id: str
    title: str
    authors: str = ""
    year: str = ""
    journal: str = ""
    abstract: str = ""
    doi: str = ""
    url: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
