"""Automatic evidence-retrieval metrics (Hit@1, Evidence Hit@3) and trace summaries.

A hit = the chunk comes from the gold source AND gold page AND contains the whole
evidence quote (whitespace/case-normalised). `page_hit` (right source/page but the
quote is not fully inside the chunk, e.g. cut by a chunk boundary) is kept as a
diagnostic only; it never replaces the official hit. Manual labels (coherence,
metadata, grounding) are NOT inferred from string matching.
"""
from __future__ import annotations

import re
from typing import Any

_ws = lambda s: re.sub(r"\s+", " ", s).strip().lower()  # noqa: E731


def _gold_options(question: dict[str, Any]) -> list[dict[str, Any]]:
    """Primary gold plus any documented alternatives (any one of them counts)."""
    primary = {"source_id": question["gold_source_id"], "page": question["gold_page"],
               "quote": question["evidence_quote"]}
    return [primary] + list(question.get("alt_gold", []))


def evaluate_query(question: dict[str, Any], hits: list[dict[str, Any]]) -> dict[str, Any]:
    options = _gold_options(question)
    ranked = []
    for rank, hit in enumerate(hits, start=1):
        meta = hit["metadata"]
        page_ok = any(meta.get("document_id") == o["source_id"] and meta.get("page") == o["page"]
                      for o in options)
        evidence_ok = any(
            meta.get("document_id") == o["source_id"] and meta.get("page") == o["page"]
            and _ws(o["quote"]) in _ws(hit["text"]) for o in options)
        ranked.append({"rank": rank, "chunk_id": hit["chunk_id"], "score": round(hit["score"], 4),
                       "page_hit": page_ok, "evidence_hit": evidence_ok})
    return {
        "hit1": bool(ranked and ranked[0]["evidence_hit"]),
        "hit3": any(r["evidence_hit"] for r in ranked[:3]),
        "page_hit3": any(r["page_hit"] for r in ranked[:3]),
        "first_hit_rank": next((r["rank"] for r in ranked if r["evidence_hit"]), None),
        "ranked": ranked,
    }


def _filter_compliant(question: dict[str, Any], hits: list[dict[str, Any]]) -> bool | None:
    f = question.get("filter")
    if not f:
        return None
    return bool(hits) and all(all(h["metadata"].get(k) == v for k, v in f.items()) for h in hits)


def summarize(traces: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate by strategy and split: counts (n/N), never bare percentages."""
    out: dict[str, Any] = {}
    for strategy in sorted({t["strategy"] for t in traces}):
        out[strategy] = {}
        for split in ("dev", "test", "all"):
            rows = [t for t in traces if t["strategy"] == strategy and (split == "all" or t["split"] == split)]
            if not rows:
                continue
            filt = [t for t in rows if t["filter_compliant"] is not None]
            out[strategy][split] = {
                "N": len(rows),
                "hit1": sum(t["eval"]["hit1"] for t in rows),
                "hit3": sum(t["eval"]["hit3"] for t in rows),
                "page_hit3_diagnostic": sum(t["eval"]["page_hit3"] for t in rows),
                "filtered_questions": len(filt),
                "filter_compliant_top3": sum(bool(t["filter_compliant"]) for t in filt),
            }
    return out


def attach_filter_compliance(question: dict[str, Any], hits: list[dict[str, Any]]) -> bool | None:
    """Filter compliance of the retrieved top-3 for questions that carry a filter."""
    return _filter_compliant(question, hits)
