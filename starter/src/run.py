"""Day 06 pipeline: ingest -> chunk (A, B) -> embed -> store -> retrieve (A, B, C) -> evaluate.

Run from `starter/`:  python -X utf8 -m src.run
Outputs go to ../results (traces, metrics, ingest stats) and ../data/manifest.json.

Strategies (same corpus, same embedding model, same questions, cosine metric):
  A  fixed-size chunks (500 chars, overlap 50), no filter
  B  paragraph-aware chunks (max 1000 chars), no filter
  C  identical index to B; metadata filter applied only for questions that carry a filter
"""
from __future__ import annotations

import json
import logging
import statistics
import time
from datetime import datetime, timezone
from importlib import metadata as importlib_metadata
from pathlib import Path

from .chunking import by_paragraph, fixed_size
from .corpus import CHAPTERS, DOCUMENT_ID, PDF, REPO, SOURCE, build_corpus
from .embeddings import MyEmbedder
from .evaluation import attach_filter_compliance, evaluate_query, summarize
from .store import ChromaStore

MODEL = "intfloat/multilingual-e5-small"
CHROMA_DIR = REPO / "starter" / "chroma_db"
RESULTS = REPO / "results"
QUESTIONS = REPO / "benchmark" / "questions.json"
CONFIG = {
    "A": {"chunking": "fixed_size", "chunk_size": 500, "overlap": 50, "collection": "A", "filter": False},
    "B": {"chunking": "by_paragraph", "max_size": 1000, "collection": "B", "filter": False},
    "C": {"chunking": "by_paragraph", "max_size": 1000, "collection": "B", "filter": True},
}
TOP_K = 3


def _length_stats(chunks) -> dict:
    sizes = [len(c.text) for c in chunks]
    return {"chunks": len(sizes), "total_chars": sum(sizes), "min": min(sizes), "max": max(sizes),
            "mean": round(statistics.mean(sizes), 1), "median": statistics.median(sizes),
            "stdev": round(statistics.pstdev(sizes), 1)}


def _versions() -> dict:
    return {p: importlib_metadata.version(p) for p in
            ("chromadb", "sentence-transformers", "torch", "pymupdf")}


def write_manifest(units, info) -> dict:
    per_page: dict[int, int] = {}
    for u in units:
        per_page[u.page] = per_page.get(u.page, 0) + len(u.text)
    manifest = {
        "source_id": DOCUMENT_ID,
        "title": "Principles of Data Science (OpenStax)",
        "authors": "Dr. Shaun V. Ault, Dr. Soohyun Kim, Dr. Larry Musolino, Dr. Nikolaus Pesendorfer (OpenStax)",
        "source_path_or_url": SOURCE,
        "download_url": "https://assets.openstax.org/oscms-prodcms/media/documents/Principles-of-Data-Science-WEB.pdf",
        "landing_page": "https://openstax.org/details/books/principles-data-science",
        "license_or_permission": "CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/), per the OpenStax CMS API. "
                                 "Non-commercial use for this lab. The PDF is NOT committed to the repo.",
        "publish_date": "2025-01-24 (OpenStax CMS metadata)",
        "accessed_at": "2026-11-13",
        "pdf_physical_pages": 569,
        "page_numbering": "page = physical PDF page (1-based). Printed page number = physical page - 10.",
        "page_counting_rule": ("Content pages = every physical page from each chapter's first page up to, but "
                               "excluding, its 'Key Terms' page (per PDF outline). Chapters 2 and 3 only. "
                               "Excluded: Key Terms, Group Project, Critical Thinking, Quantitative Problems, "
                               "References, other chapters. Running headers/footers removed."),
        "chapters": {str(c): {k: v for k, v in info[c].items() if k != "sections"} | {
            "sections": [{"id": s, "title": t, "start_page": p} for s, t, p in info[c]["sections"]]}
            for c in CHAPTERS},
        "content_pages": len(per_page),
        "content_units": len(units),
        "total_normalized_chars": sum(per_page.values()),
        "chars_per_page": {str(p): n for p, n in sorted(per_page.items())},
        "metadata_fields": {
            "document_id": "str, constant source id", "source": "str, file path",
            "page": "int, physical PDF page (trace to source)",
            "chapter": "int, from PDF outline", "section": "str e.g. '3.3', section heading in effect (from PDF outline; '2.0'/'3.0' = chapter intro)",
            "section_title": "str", "unit_id": "str, page+section unit", "chunk_index": "int", "n_chars": "int"},
        "known_limits": ["Mathematical formulas and symbols are images/glyphs and are missing from the extracted text.",
                         "Figures are not extracted (text only); tables are linearised in reading order.",
                         "Line-end hyphen joins may merge a few real hyphenated compounds."],
    }
    (REPO / "data" / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    RESULTS.mkdir(exist_ok=True)
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # 1. corpus -------------------------------------------------------------
    t0 = time.perf_counter()
    units, info = build_corpus()
    content_pages = len({u.page for u in units})
    if content_pages < 30:
        raise SystemExit(f"Only {content_pages} content pages; need >= 30")
    manifest = write_manifest(units, info)
    load_seconds = round(time.perf_counter() - t0, 2)
    print(f"corpus: {content_pages} content pages, {len(units)} units, {manifest['total_normalized_chars']} chars")

    questions = json.loads(QUESTIONS.read_text(encoding="utf-8"))

    # 2. chunk, embed, store -----------------------------------------------
    embedder = MyEmbedder(MODEL)
    store = ChromaStore(CHROMA_DIR, embedder.dimensions)
    print(f"embedder: {embedder.model_name} dims={embedder.dimensions} max_seq={embedder.max_seq_length}")
    ingest = {}
    for name, builder in (("A", lambda u: fixed_size(u, 500, 50)), ("B", lambda u: by_paragraph(u, 1000))):
        t = time.perf_counter()
        chunks = [c for u in units for c in builder(u)]
        t_chunk = time.perf_counter() - t
        t = time.perf_counter()
        vectors = embedder.embed_documents([c.text for c in chunks])
        t_embed = time.perf_counter() - t
        t = time.perf_counter()
        first = store.upsert(name, chunks, vectors)
        count_after_first = store.count(name)
        second = store.upsert(name, chunks, vectors)  # re-ingest same version: must not duplicate
        count_after_second = store.count(name)
        t_store = time.perf_counter() - t
        ingest[name] = {**_length_stats(chunks), "chunk_seconds": round(t_chunk, 2),
                        "embed_seconds": round(t_embed, 2), "store_seconds_incl_reingest": round(t_store, 2),
                        "ingest_seconds": round(t_chunk + t_embed, 2), "cost_usd": 0.0,
                        "count_after_first_ingest": count_after_first,
                        "count_after_reingest": count_after_second, "reingest_removed": second["removed"],
                        "first_removed": first["removed"]}
        print(name, ingest[name])
        if count_after_first != count_after_second:
            raise SystemExit(f"re-ingest changed the chunk count for {name}")
    ingest["C"] = {"note": "C reuses B's collection (identical chunks/vectors); only the query filter differs.",
                   **{k: v for k, v in ingest["B"].items() if k in ("chunks",)}}

    # 3. retrieve + evaluate -------------------------------------------------
    traces = []
    t = time.perf_counter()
    qvecs = {q["id"]: embedder.embed_query(q["question"]) for q in questions}
    query_embed_seconds = round(time.perf_counter() - t, 2)
    timing = {}
    for strategy, cfg in CONFIG.items():
        t = time.perf_counter()
        for q in questions:
            flt = q["filter"] if (cfg["filter"] and q["filter"]) else None
            hits = store.search(cfg["collection"], qvecs[q["id"]], TOP_K, flt)
            traces.append({
                "strategy": strategy, "question_id": q["id"], "split": q["split"], "type": q["type"],
                "question": q["question"], "gold_page": q["gold_page"], "evidence_quote": q["evidence_quote"],
                "question_filter": q["filter"], "applied_filter": flt,
                "filter_compliant": attach_filter_compliance(q, hits) if flt else None,
                "eval": evaluate_query(q, hits),
                "top3": [{"rank": i + 1, "chunk_id": h["chunk_id"], "score": round(h["score"], 4),
                          "metadata": h["metadata"], "text": h["text"]} for i, h in enumerate(hits)],
            })
        timing[strategy] = round(time.perf_counter() - t, 3)

    # NOTE: filter compliance for strategies A/B is reported as N/A (they never apply a filter);
    # the question-level filter is still recorded so unfiltered top-3 can be audited against it.
    with (RESULTS / "traces.jsonl").open("w", encoding="utf-8") as f:
        for tr in traces:
            f.write(json.dumps(tr, ensure_ascii=False) + "\n")
    metrics = summarize(traces)
    run_info = {
        "started_utc": started, "model": MODEL, "dimensions": embedder.dimensions,
        "max_seq_length": embedder.max_seq_length, "document_prefix": "passage: ", "query_prefix": "query: ",
        "vector_store": "Chroma persistent client, HNSW (approximate), cosine", "chroma_dir": "starter/chroma_db",
        "versions": _versions(), "top_k": TOP_K, "config": CONFIG, "ingest": ingest,
        "load_corpus_seconds": load_seconds, "query_embed_seconds_all_questions": query_embed_seconds,
        "retrieval_seconds_per_strategy": timing, "metrics": metrics,
        "n_questions": len(questions), "cost_usd": 0.0,
    }
    (RESULTS / "run_summary.json").write_text(json.dumps(run_info, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\nMETRICS (n/N)")
    for s, by_split in metrics.items():
        for split, m in by_split.items():
            print(f"  {s} {split:4s} Hit@1 {m['hit1']}/{m['N']}  Hit@3 {m['hit3']}/{m['N']}  "
                  f"page_hit3(diag) {m['page_hit3_diagnostic']}/{m['N']}  "
                  f"filter_compliant {m['filter_compliant_top3']}/{m['filtered_questions']}")


if __name__ == "__main__":
    main()
