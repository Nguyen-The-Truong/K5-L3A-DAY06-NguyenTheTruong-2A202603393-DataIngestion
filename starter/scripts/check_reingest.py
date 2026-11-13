"""Store-mechanics check on a throw-away Chroma directory (real embeddings, 3 short texts).

1. ingest 3 chunks            -> count 3
2. ingest the same 3 again    -> count 3 (no duplicates)
3. ingest a 'changed' document (one chunk edited, one dropped) -> stale ids removed, count 2
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.embeddings import MyEmbedder  # noqa: E402
from src.models import Chunk  # noqa: E402
from src.store import ChromaStore  # noqa: E402


def mk(i, text):
    return Chunk(f"doc:c{i}", "doc", "x.pdf", 1, text, {"chapter": 2, "section": "2.1"})


emb = MyEmbedder()
with tempfile.TemporaryDirectory() as tmp:
    store = ChromaStore(Path(tmp), emb.dimensions, prefix="check")
    v1 = [mk(0, "Stratified sampling splits a population into strata."),
          mk(1, "Lossy compression permanently removes data."),
          mk(2, "A probability cannot be greater than 1.")]
    store.upsert("T", v1, emb.embed_documents([c.text for c in v1]))
    print("after first ingest   :", store.count("T"))
    store.upsert("T", v1, emb.embed_documents([c.text for c in v1]))
    print("after identical rerun:", store.count("T"))
    v2 = [mk(0, "Stratified sampling splits a population into strata (edited)."), v1[1]]
    r = store.upsert("T", v2, emb.embed_documents([c.text for c in v2]))
    print("after changed version:", store.count("T"), "removed:", r["removed"])
    hit = store.search("T", emb.embed_query("what removes data permanently"), 1, {"chapter": 2})
    print("filter+search works  :", hit[0]["chunk_id"], hit[0]["metadata"]["section"])
