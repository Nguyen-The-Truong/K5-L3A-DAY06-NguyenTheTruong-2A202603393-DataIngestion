"""Read and normalize the source PDF, then cut it into traceable content units.

Pipeline: physical PDF page -> text blocks (paragraphs) -> normalized text ->
"content units" (one physical page, split where a new numbered section begins).
A unit keeps the physical PDF page number plus chapter/section metadata taken
from the book's own table of contents.
"""
from __future__ import annotations

import logging
import re
import unicodedata
from pathlib import Path

import pymupdf

from .models import DocumentPage

log = logging.getLogger("ingestion")

_FOOTER_ACCESS = re.compile(r"^Access for free at openstax\.org$", re.I)
_SECTION_TOC = re.compile(r"^(\d)\.(\d)\s+(.+)$")
# Running headers/footers: "58 2 • Chapter title" or "2.1 • Section title 59" or "2 • Chapter title 61".
_RUNNING = re.compile(r"^(\d+\s+\d\s+•\s+.+|\d(\.\d)?\s+•\s+.+\s\d+)$")


def normalize_text(text: str) -> str:
    """NFKC-normalize, drop private-use glyphs, unwrap line breaks, tidy spaces."""
    text = unicodedata.normalize("NFKC", text)
    # Bullets in this PDF come out as private-use / replacement glyphs.
    text = "".join("•" if unicodedata.category(c) == "Co" or c == "�" else c for c in text)
    text = text.replace("­", "")
    text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)  # de-hyphenate across lines
    text = re.sub(r"[ \t\r\f\v]*\n[ \t\r\f\v]*", " ", text)  # soft-wrap -> space
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def _page_paragraphs(page: "pymupdf.Page") -> list[str]:
    """Return normalized text blocks for a page, minus running header/footer."""
    blocks = [b for b in page.get_text("blocks", sort=True) if b[6] == 0]
    texts = [normalize_text(b[4]) for b in blocks]
    texts = [t for t in texts if t and not _RUNNING.match(t)]
    # Footer = running title/page number block followed by the 'Access for free' block.
    if texts and _FOOTER_ACCESS.match(texts[-1]):
        texts.pop()
        if texts and len(texts[-1]) <= 90 and re.search(r"(^\d+\s)|(\s\d+$)", texts[-1]):
            texts.pop()
    return texts


def load_pdf(path: Path, document_id: str, source: str,
             first_page: int | None = None, last_page: int | None = None) -> list[DocumentPage]:
    """Extract physical pages (1-based PDF page numbers). Empty pages are logged.

    Paragraphs are separated by a blank line so chunking can respect them.
    """
    doc = pymupdf.open(path)
    first = first_page or 1
    last = last_page or doc.page_count
    pages: list[DocumentPage] = []
    for n in range(first, last + 1):
        try:
            paragraphs = _page_paragraphs(doc[n - 1])
        except Exception as exc:  # keep going, but record the failure
            log.error("page %d failed to extract: %s", n, exc)
            continue
        text = "\n\n".join(paragraphs)
        if not text.strip():
            log.warning("page %d has no extractable text", n)
            continue
        pages.append(DocumentPage(document_id, source, n, text))
    return pages


def read_toc_sections(path: Path) -> dict:
    """Chapter/section structure from the PDF outline (not guessed).

    Returns {chapter: {"title", "start", "key_terms_page", "sections": [(id, title, start)]}}.
    """
    toc = pymupdf.open(path).get_toc()
    chapters: dict[int, dict] = {}
    current = None
    for level, title, page in toc:
        m = re.match(r"^Chapter (\d+)\s+(.*)$", title)
        if level == 1 and m:
            current = int(m.group(1))
            chapters[current] = {"title": m.group(2), "start": page, "key_terms_page": None, "sections": []}
        elif current is not None and level == 2:
            s = _SECTION_TOC.match(title)
            if s and int(s.group(1)) == current:
                chapters[current]["sections"].append((f"{s.group(1)}.{s.group(2)}", s.group(3), page))
            elif title == "Key Terms":
                chapters[current]["key_terms_page"] = page
    return chapters


def build_content_units(pages: list[DocumentPage], chapter: int, info: dict) -> list[DocumentPage]:
    """Split pages of one chapter into units carrying chapter/section metadata.

    A section changes only when a paragraph equals the section heading from the
    TOC *and* the next paragraph starts with 'Learning Outcomes' (this skips the
    chapter-outline list on the opening page).
    """
    headings = {f"{sid} {title}": (sid, title) for sid, title, _ in info["sections"]}
    section_id, section_title = f"{chapter}.0", "Chapter introduction"
    units: list[DocumentPage] = []
    for pg in pages:
        paras = pg.text.split("\n\n")
        buf: list[str] = []

        def flush() -> None:
            text = "\n\n".join(buf).strip()
            if text:
                units.append(DocumentPage(
                    pg.document_id, pg.source, pg.page, text,
                    {"chapter": chapter, "section": section_id, "section_title": section_title,
                     "unit_id": f"p{pg.page:03d}-s{section_id}"}))
            buf.clear()

        for i, p in enumerate(paras):
            if p in headings and i + 1 < len(paras) and paras[i + 1].startswith("Learning Outcomes"):
                flush()
                section_id, section_title = headings[p]
            buf.append(p)
        flush()
    return units
