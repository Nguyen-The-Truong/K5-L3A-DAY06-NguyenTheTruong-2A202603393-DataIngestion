"""Builds the sheets for manual audit (coherence, metadata, grounding).

Sample selection rules were fixed before looking at any label:
  * coherence: 10 content units at indices i*N//10 (i=0..9) of the units sorted by (page, section);
    for each strategy the chunk that covers the midpoint character of that unit. C uses B's chunks.
  * metadata + grounding: the first five test questions by id (t01..t05) x top-3 x strategy.
Labels are written by a person (or proposed by an AI assistant and flagged as such) into the CSVs.
"""
from __future__ import annotations

import csv
import json
import re

import pymupdf

from .chunking import by_paragraph, fixed_size
from .corpus import PDF, REPO, build_corpus

OUT = REPO / "results" / "audit"
ws = lambda s: re.sub(r"\s+", " ", s).strip()  # noqa: E731


def coherence_sample(units):
    order = sorted(units, key=lambda u: (u.page, u.metadata["section"]))
    n = len(order)
    picks = [order[i * n // 10] for i in range(10)]
    rows = []
    for u in picks:
        flat = ws(u.text)
        mid = len(flat) // 2
        for strategy, chunks in (("A", fixed_size(u, 500, 50)), ("B", by_paragraph(u, 1000))):
            chosen = None
            for c in chunks:
                start = flat.find(ws(c.text)[:80])
                if start != -1 and start <= mid < start + len(ws(c.text)):
                    chosen = c
                    break
            chosen = chosen or chunks[0]
            rows.append({"position": u.metadata["unit_id"], "page": u.page, "section": u.metadata["section"],
                         "strategy": strategy, "chunk_id": chosen.chunk_id, "n_chars": len(chosen.text),
                         "chunk_text": chosen.text.replace("\n", " ⏎ "), "score_0_2": "", "reason": "",
                         "labeler": ""})
    return rows


def metadata_and_grounding(traces):
    doc = pymupdf.open(PDF)
    page_text_cache: dict[int, str] = {}
    meta_rows, ground_rows = [], []
    for t in traces:
        if t["question_id"] not in {"t01", "t02", "t03", "t04", "t05"}:
            continue
        for h in t["top3"]:
            m = h["metadata"]
            page = m["page"]
            if page not in page_text_cache:
                from .ingestion import _page_paragraphs
                page_text_cache[page] = ws(" ".join(_page_paragraphs(doc[page - 1])))
            # A chunk's text must literally occur on the page it claims (first 60 chars is enough to anchor).
            on_page = ws(h["text"])[:60] in page_text_cache[page]
            filt_ok = None
            if t["applied_filter"]:
                filt_ok = all(m.get(k) == v for k, v in t["applied_filter"].items())
            meta_rows.append({
                "strategy": t["strategy"], "question_id": t["question_id"], "rank": h["rank"],
                "chunk_id": h["chunk_id"], "source": m["source"], "page": page, "chapter": m["chapter"],
                "section": m["section"], "section_title": m["section_title"],
                "auto_text_found_on_claimed_page": on_page, "auto_filter_ok": filt_ok,
                "manual_metadata_ok": "", "note": "", "labeler": ""})
        ground_rows.append({"strategy": t["strategy"], "question_id": t["question_id"],
                            "question": t["question"], "evidence_quote": t["evidence_quote"],
                            "top3_chunk_ids": " | ".join(h["chunk_id"] for h in t["top3"]),
                            "top3_texts": "\n---\n".join(f"[{h['rank']}] p{h['metadata']['page']}: {h['text']}"
                                                         for h in t["top3"]),
                            "score_0_2": "", "reason": "", "labeler": ""})
    return meta_rows, ground_rows


def _write(path, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    units, _ = build_corpus()
    traces = [json.loads(line) for line in (REPO / "results" / "traces.jsonl").read_text(encoding="utf-8").splitlines()]
    _write(OUT / "coherence_samples.csv", coherence_sample(units))
    meta, ground = metadata_and_grounding(traces)
    _write(OUT / "metadata_audit.csv", meta)
    _write(OUT / "grounding_audit.csv", ground)
    print("coherence rows:", 20, "| metadata rows:", len(meta), "| grounding rows:", len(ground))


if __name__ == "__main__":
    main()
