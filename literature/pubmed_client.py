from __future__ import annotations

import time

from Bio import Entrez

import config
from literature.models import LiteraturePaper


def enabled() -> bool:
    return bool(config.NCBI_EMAIL)


def configure_entrez() -> None:
    if not config.NCBI_EMAIL:
        raise ValueError("NCBI_EMAIL is required for PubMed search.")
    Entrez.email = config.NCBI_EMAIL
    if config.NCBI_API_KEY:
        Entrez.api_key = config.NCBI_API_KEY


def search_pubmed(query: str, max_results: int = 8) -> list[str]:
    configure_entrez()
    handle = Entrez.esearch(
        db="pubmed",
        term=query,
        retmax=max_results,
        sort="relevance",
    )
    record = Entrez.read(handle)
    handle.close()
    time.sleep(0.35)
    return list(record.get("IdList", []))


def fetch_pubmed(pmids: list[str]) -> list[LiteraturePaper]:
    configure_entrez()
    if not pmids:
        return []

    handle = Entrez.efetch(
        db="pubmed",
        id=",".join(pmids),
        retmode="xml",
    )
    records = Entrez.read(handle)
    handle.close()

    papers: list[LiteraturePaper] = []
    for article in records.get("PubmedArticle", []):
        medline = article.get("MedlineCitation", {})
        art = medline.get("Article", {})

        pmid = str(medline.get("PMID", ""))
        title = str(art.get("ArticleTitle", ""))

        journal_data = art.get("Journal", {})
        journal = str(journal_data.get("Title", ""))

        pub_date = journal_data.get("JournalIssue", {}).get("PubDate", {})
        year = str(pub_date.get("Year", "")) or str(pub_date.get("MedlineDate", ""))[:4]

        authors_list = art.get("AuthorList", [])
        author_names = []
        for author in authors_list[:4]:
            last = author.get("LastName", "")
            initials = author.get("Initials", "")
            if last:
                author_names.append(f"{last} {initials}".strip())
        authors = ", ".join(author_names)
        if len(authors_list) > 4:
            authors += " et al."

        abstract_parts = art.get("Abstract", {}).get("AbstractText", [])
        abstract = " ".join(str(part) for part in abstract_parts)

        doi = ""
        for item in art.get("ELocationID", []):
            if getattr(item, "attributes", {}).get("EIdType") == "doi":
                doi = str(item)
                break

        papers.append(
            LiteraturePaper(
                source="PubMed",
                id=pmid,
                title=title,
                authors=authors,
                year=year,
                journal=journal,
                abstract=abstract,
                doi=doi,
                url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            )
        )

    time.sleep(0.35)
    return papers


def search(topic: str, max_results: int = 8) -> list[LiteraturePaper]:
    query = f'({topic}) AND english[Language]'
    pmids = search_pubmed(query, max_results=max_results)
    return fetch_pubmed(pmids)
