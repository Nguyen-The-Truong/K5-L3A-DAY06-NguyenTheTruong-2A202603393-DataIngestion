"""Corpus definition: which pages count as content, and how units are built."""
from __future__ import annotations

from pathlib import Path

from .ingestion import build_content_units, load_pdf, read_toc_sections
from .models import DocumentPage

REPO = Path(__file__).resolve().parents[2]
PDF = REPO / "data" / "raw" / "principles-of-data-science.pdf"
DOCUMENT_ID = "pds-openstax-2025"
SOURCE = "data/raw/principles-of-data-science.pdf"
CHAPTERS = (2, 3)


def build_corpus(pdf: Path = PDF) -> tuple[list[DocumentPage], dict]:
    """Content = from chapter start up to (not including) its 'Key Terms' page."""
    toc = read_toc_sections(pdf)
    units: list[DocumentPage] = []
    info_out = {}
    for ch in CHAPTERS:
        info = toc[ch]
        first, last = info["start"], info["key_terms_page"] - 1
        pages = load_pdf(pdf, DOCUMENT_ID, SOURCE, first, last)
        units += build_content_units(pages, ch, info)
        info_out[ch] = {"title": info["title"], "first_page": first, "last_page": last,
                        "pages_extracted": len(pages), "sections": info["sections"]}
    return units, info_out
