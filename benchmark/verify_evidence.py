"""Check every evidence quote really exists on its gold page (after normalization)
and that every filter value matches the section/chapter of that evidence."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "starter"))
from src.corpus import build_corpus  # noqa: E402

ws = lambda s: re.sub(r"\s+", " ", s)  # noqa: E731


def main() -> int:
    units, _ = build_corpus()
    by_page: dict[int, list] = {}
    for u in units:
        by_page.setdefault(u.page, []).append(u)
    questions = json.loads((Path(__file__).with_name("questions.json")).read_text(encoding="utf-8"))
    problems = 0
    for q in questions:
        hits = [u for u in by_page.get(q["gold_page"], []) if ws(q["evidence_quote"]) in ws(u.text)]
        if not hits:
            problems += 1
            print("EVIDENCE NOT FOUND:", q["id"], "page", q["gold_page"])
            continue
        f = q["filter"] or {}
        if "section" in f and f["section"] not in {u.metadata["section"] for u in hits}:
            problems += 1
            print("FILTER/SECTION MISMATCH:", q["id"])
        if "chapter" in f and f["chapter"] not in {u.metadata["chapter"] for u in hits}:
            problems += 1
            print("FILTER/CHAPTER MISMATCH:", q["id"])
    print(f"checked {len(questions)} questions, problems: {problems}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
