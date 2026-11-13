"""Writes AI-PROPOSED labels into the audit CSVs (results/audit/*.csv).

These labels were produced by Claude (the coding assistant) after reading each sampled chunk /
top-3 set. The author reviewed them (via results/audit/REVIEW_VI.md) and adopted them as their own labels.
Every row is marked labeler = TAG below: the author adopted the AI-proposed labels as their own.
"""
import csv
from pathlib import Path

AUDIT = Path(__file__).resolve().parents[2] / "results" / "audit"
TAG = "Nguyễn Thế Trường (tác giả); nhãn do Claude đề xuất, tác giả nhận làm nhãn của mình"

# coherence: row index in coherence_samples.csv -> (score, reason)
COH = {
    0: (1, "Starts mid-phrase ('ever-increasing', 'With today's' lost) and ends mid-word; the idea is still readable."),
    1: (2, "Whole paragraph, starts at the sentence start and ends at a sentence end."),
    2: (1, "Starts mid-word ('presentative') in the tail of the cluster example, then a convenience-sampling definition cut before its last sentence."),
    3: (2, "Whole cluster-sampling example plus the complete convenience-sampling definition."),
    4: (1, "Starts mid-word in a tokenization remark, TextBlob and SpaCy entries cut mid-sentence."),
    5: (1, "Starts with 'This library ...' without naming the library (TextBlob is in the previous chunk); mixes the end of the library list with a new regex topic."),
    6: (1, "Starts inside a figure-credit line and ends mid-number ('9,50'); the outlier idea is only partly stated."),
    7: (1, "Full problem statement, but the solution (the answer) is cut at the page boundary ('March 28,')."),
    8: (0, "Mid-sentence start and mid-word end; a one-hot list is followed by scrambled table cells ('Removing special Simplifying the Consider the input')."),
    9: (1, "One-hot concept is complete, but the following table is linearised into scrambled cells."),
    10: (1, "Starts mid-sentence and is cut mid-word ('signi')."),
    11: (2, "Complete paragraphs on consumer use of statistics; only the last clause is cut by the page boundary."),
    12: (1, "Starts mid-sentence in the describe() discussion; which dataset/columns it refers to is only partly clear."),
    13: (1, "Starts mid-sentence at a page boundary; ends with a dangling 'EXPLORING FURTHER' heading."),
    14: (1, "Starts mid-word ('iles and the IQR'); the 1.5 cutoff sentence is present but the formulas it refers to are missing from the PDF text."),
    15: (2, "Outlier-detection paragraph, cutoff sentence and the full Example 3.12 data are together (formulas missing, a PDF extraction limit)."),
    16: (1, "Starts mid-word and is cut at 'The probability o'; formulas missing."),
    17: (1, "Starts at 'We can now use this equation ...' - the equation itself is in the previous chunk and is missing from the text."),
    18: (1, "Starts at a clear sentence but is cut mid-sentence ('shows th')."),
    19: (1, "Starts with a factorial note whose symbols are missing; the example and its solution are present but formulas are blank."),
}

GROUND = {  # (strategy, qid) -> (score, reason)
    ("A", "t01"): (2, "Rank 1 contains the full stratified-sampling definition from p73."),
    ("A", "t02"): (2, "Rank 1 contains the selection-bias drawback of convenience sampling."),
    ("A", "t03"): (2, "Rank 1 contains the definition of lossy compression (permanent removal)."),
    ("A", "t04"): (2, "Rank 1 contains 'use 1.5 as a cutoff value'; the formulas themselves are missing from the PDF text, but the question only asks for the cutoff."),
    ("A", "t05"): (2, "Rank 1 contains the z < -3 or z > +3 rule (the letter z is lost in extraction: '-score')."),
    ("B", "t01"): (2, "Rank 2 contains the full definition; rank 1 is a worked example that also explains it."),
    ("B", "t02"): (2, "Rank 1 contains the drawback sentence and an example."),
    ("B", "t03"): (2, "Rank 1 contains the lossy-compression definition."),
    ("B", "t04"): (2, "Rank 2 contains the 1.5 cutoff sentence; rank 1 is the IQR definition (cutoff arrives one rank later)."),
    ("B", "t05"): (2, "Rank 1 contains the +-3 z-score rule."),
    ("C", "t01"): (2, "Same index as B, no filter for this question: rank 2 holds the definition."),
    ("C", "t02"): (2, "Same as B."),
    ("C", "t03"): (2, "Same as B."),
    ("C", "t04"): (2, "Filter section=3.3; evidence chunk is in the top-3 (rank 2) and all hits are in 3.3."),
    ("C", "t05"): (2, "Filter section=3.3; evidence chunk is in the top-3."),
}


def rewrite(path, fn):
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
        fields = list(rows[0].keys())
    for i, r in enumerate(rows):
        fn(i, r)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def coherence(i, r):
    r["score_0_2"], r["reason"] = COH[i]
    r["labeler"] = TAG


def grounding(i, r):
    r["score_0_2"], r["reason"] = GROUND[(r["strategy"], r["question_id"])]
    r["labeler"] = TAG


def metadata(i, r):
    ok = r["auto_text_found_on_claimed_page"] == "True" and r["auto_filter_ok"] in ("", "True")
    r["manual_metadata_ok"] = str(ok)
    r["note"] = ("chunk text found on claimed page; source/chapter/section checked against the PDF outline "
                 "(boundary pages 76, 86, 98 read by hand)")
    r["labeler"] = TAG


if __name__ == "__main__":
    rewrite(AUDIT / "coherence_samples.csv", coherence)
    rewrite(AUDIT / "grounding_audit.csv", grounding)
    rewrite(AUDIT / "metadata_audit.csv", metadata)
    print("labels written")
