"""Persistent vector store: Chroma (on-disk, HNSW, cosine) with metadata filtering.

One Chroma collection per chunking strategy. Strategy C reuses B's collection
and only adds a metadata filter at query time.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import chromadb

from .models import Chunk


class ChromaStore:
    def __init__(self, path: Path, dimensions: int, prefix: str = "day06") -> None:
        self.dimensions = dimensions
        self.prefix = prefix
        self._client = chromadb.PersistentClient(path=str(path))

    def _collection(self, strategy: str):
        return self._client.get_or_create_collection(
            f"{self.prefix}_{strategy}", metadata={"hnsw:space": "cosine"})

    def count(self, strategy: str) -> int:
        return self._collection(strategy).count()

    def upsert(self, strategy: str, chunks: list[Chunk], vectors: list[list[float]]) -> dict[str, int]:
        """Write chunks idempotently; remove stale chunks of the same documents.

        Returns {"written", "removed"}. Re-running with identical input keeps the
        count unchanged; if a document's chunks change, old IDs are deleted.
        """
        if len(chunks) != len(vectors):
            raise ValueError("chunks and vectors differ in length")
        if any(len(v) != self.dimensions for v in vectors):
            raise ValueError(f"vector dimension != {self.dimensions}")
        col = self._collection(strategy)
        new_ids = {c.chunk_id for c in chunks}
        removed = 0
        for doc_id in {c.document_id for c in chunks}:
            old = set(col.get(where={"document_id": doc_id}, include=[])["ids"])
            stale = sorted(old - new_ids)
            if stale:
                col.delete(ids=stale)
                removed += len(stale)
        for i in range(0, len(chunks), 500):
            batch = chunks[i:i + 500]
            col.upsert(
                ids=[c.chunk_id for c in batch],
                embeddings=vectors[i:i + 500],
                documents=[c.text for c in batch],
                metadatas=[{"document_id": c.document_id, "source": c.source, "page": c.page, **c.metadata}
                           for c in batch])
        return {"written": len(chunks), "removed": removed}

    def search(self, strategy: str, query_vector: list[float], top_k: int = 3,
               filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        where = None
        if filters:
            items = [{k: {"$eq": v}} for k, v in filters.items()]
            where = items[0] if len(items) == 1 else {"$and": items}
        res = self._collection(strategy).query(
            query_embeddings=[query_vector], n_results=top_k, where=where,
            include=["documents", "metadatas", "distances"])
        return [{"chunk_id": cid, "text": doc, "score": 1.0 - dist, "metadata": meta}
                for cid, doc, meta, dist in zip(res["ids"][0], res["documents"][0],
                                                res["metadatas"][0], res["distances"][0])]
