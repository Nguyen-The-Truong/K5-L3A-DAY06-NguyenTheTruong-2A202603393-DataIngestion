"""Recompute the audit numbers from results/audit/*.csv (run after editing any score)."""
import collections
import csv
from pathlib import Path

AUDIT = Path(__file__).resolve().parents[2] / "results" / "audit"
rd = lambda n: list(csv.DictReader(open(AUDIT / n, encoding="utf-8-sig")))  # noqa: E731

coh = rd("coherence_samples.csv")
for s in "AB":
    v = [int(r["score_0_2"]) for r in coh if r["strategy"] == s]
    print(f"coherence {s}: sum {sum(v)} / n {len(v)} = {sum(v) / len(v):.2f}  counts {dict(collections.Counter(v))}  (C uses B's chunks)")
meta = rd("metadata_audit.csv")
for s in "ABC":
    r = [x for x in meta if x["strategy"] == s]
    print(f"metadata {s}: {sum(x['manual_metadata_ok'] == 'True' for x in r)}/{len(r)}")
g = rd("grounding_audit.csv")
for s in "ABC":
    v = [int(x["score_0_2"]) for x in g if x["strategy"] == s]
    c = collections.Counter(v)
    print(f"grounding {s}: 0/1/2 = {c[0]}/{c[1]}/{c[2]}  mean {sum(v) / len(v):.2f}")
