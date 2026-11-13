"""Interactive demo: type a question, see the top-3 chunks of a strategy.

Usage (from starter/, after `python -X utf8 -m src.run` has built the index):
  python -X utf8 scripts/demo_query.py "What is stratified sampling?"
  python -X utf8 scripts/demo_query.py "How can outliers be identified?" --strategy C --section 2.4
  python -X utf8 scripts/demo_query.py            # interactive prompt, Ctrl+C to quit
Strategies: A (fixed 500/50), B (paragraph), C (B + optional --section/--chapter filter).
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.embeddings import MyEmbedder  # noqa: E402
from src.run import CHROMA_DIR, CONFIG, MODEL  # noqa: E402
from src.store import ChromaStore  # noqa: E402


def show(store, emb, question, strategy, flt):
    cfg = CONFIG[strategy]
    use = flt if (cfg["filter"] and flt) else None
    if flt and not cfg["filter"]:
        print(f"(strategy {strategy} ignores filters; use --strategy C)")
    hits = store.search(cfg["collection"], emb.embed_query(question), 3, use)
    print(f"\nQ: {question}   [strategy {strategy}, filter={use}]")
    for i, h in enumerate(hits, 1):
        m = h["metadata"]
        print(f"\n#{i} score={h['score']:.3f}  page {m['page']}  section {m['section']} ({m['section_title']})")
        print("   " + h["text"][:500].replace("\n", " "))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("question", nargs="?")
    ap.add_argument("--strategy", choices=["A", "B", "C"], default="C")
    ap.add_argument("--section")
    ap.add_argument("--chapter", type=int)
    a = ap.parse_args()
    flt = {}
    if a.section:
        flt["section"] = a.section
    if a.chapter:
        flt["chapter"] = a.chapter
    emb = MyEmbedder(MODEL)
    store = ChromaStore(CHROMA_DIR, emb.dimensions)
    if store.count("B") == 0:
        raise SystemExit("Index is empty. Run `python -X utf8 -m src.run` first.")
    if a.question:
        show(store, emb, a.question, a.strategy, flt)
        return
    while True:
        try:
            q = input("\nQuestion> ").strip()
        except (KeyboardInterrupt, EOFError):
            break
        if q:
            show(store, emb, q, a.strategy, flt)


if __name__ == "__main__":
    main()
