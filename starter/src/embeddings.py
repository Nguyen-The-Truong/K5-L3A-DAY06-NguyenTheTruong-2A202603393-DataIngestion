"""Real local embedding model: intfloat/multilingual-e5-small (Sentence Transformers).

e5 models expect a 'passage: ' prefix on documents and 'query: ' on questions.
Vectors are L2-normalised so cosine similarity == dot product. Any load error
propagates; there is no mock/random fallback.
"""
from __future__ import annotations

from typing import Protocol


class Embedder(Protocol):
    model_name: str
    dimensions: int

    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...

    def embed_query(self, question: str) -> list[float]: ...


class MyEmbedder:
    def __init__(self, model_name: str = "intfloat/multilingual-e5-small", batch_size: int = 32) -> None:
        from sentence_transformers import SentenceTransformer  # imported lazily: heavy

        self.model_name = model_name
        self.batch_size = batch_size
        self._model = SentenceTransformer(model_name)
        self.dimensions = int(self._model.get_sentence_embedding_dimension())
        self.max_seq_length = int(self._model.max_seq_length)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vecs = self._model.encode([f"passage: {t}" for t in texts], batch_size=self.batch_size,
                                  normalize_embeddings=True, show_progress_bar=False)
        return vecs.tolist()

    def embed_query(self, question: str) -> list[float]:
        return self._model.encode(f"query: {question}", normalize_embeddings=True).tolist()
