"""Fixed-size (strategy A) and paragraph-aware (strategies B/C) chunking.

Both functions work on one content unit (a physical page, already split at
section boundaries), so a chunk never crosses a page or a section boundary and
always has a single, correct page number and section.
"""
from __future__ import annotations

import re

from .models import Chunk, DocumentPage

_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


def _meta(page: DocumentPage, index: int, text: str) -> dict:
    return {**page.metadata, "chunk_index": index, "n_chars": len(text)}


def _make(page: DocumentPage, tag: str, index: int, text: str) -> Chunk:
    uid = page.metadata.get("unit_id", f"p{page.page:03d}")
    return Chunk(chunk_id=f"{page.document_id}:{uid}:{tag}{index:02d}", document_id=page.document_id,
                 source=page.source, page=page.page, text=text, metadata=_meta(page, index, text))


def fixed_size(page: DocumentPage, size: int, overlap: int) -> list[Chunk]:
    """Sliding character window; paragraph breaks are flattened to single spaces."""
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")
    text = re.sub(r"\s+", " ", page.text).strip()
    chunks: list[Chunk] = []
    step = size - overlap
    start = 0
    while start < len(text):
        piece = text[start:start + size].strip()
        if piece:
            chunks.append(_make(page, "fx", len(chunks), piece))
        if start + size >= len(text):
            break
        start += step
    return chunks


def _split_oversized(paragraph: str, max_size: int) -> list[str]:
    """Break one long paragraph at sentence ends; hard-cut only if a sentence is too long."""
    pieces: list[str] = []
    current = ""
    for sentence in _SENTENCE_END.split(paragraph):
        while len(sentence) > max_size:  # pathological sentence (e.g. a table row)
            if current:
                pieces.append(current)
                current = ""
            pieces.append(sentence[:max_size])
            sentence = sentence[max_size:]
        if current and len(current) + 1 + len(sentence) > max_size:
            pieces.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
    if current:
        pieces.append(current)
    return pieces


def by_paragraph(page: DocumentPage, max_size: int) -> list[Chunk]:
    """Greedily pack whole paragraphs up to max_size; split oversized ones by sentence.

    Short heading-like paragraphs are naturally packed together with the
    paragraph that follows them.
    """
    paragraphs = [p.strip() for p in page.text.split("\n\n") if p.strip()]
    units: list[str] = []
    for p in paragraphs:
        units.extend(_split_oversized(p, max_size) if len(p) > max_size else [p])
    chunks: list[Chunk] = []
    current = ""
    for u in units:
        if current and len(current) + 2 + len(u) > max_size:
            chunks.append(_make(page, "pg", len(chunks), current))
            current = u
        else:
            current = f"{current}\n\n{u}" if current else u
    if current:
        chunks.append(_make(page, "pg", len(chunks), current))
    return chunks
