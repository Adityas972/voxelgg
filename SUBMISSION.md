# SUBMISSION.md

## What I Did

**Time spent:** ~2.5 hours

I loaded all 99 JSON files programmatically (`analysis.py`) and looked at the data
in two passes: first a raw inventory of all labels to understand the shape of the
extraction output, then a structured quality audit and theme-clustering pass to
build the cleaned taxonomy and identify the top opportunities.

I did not use an LLM to generate the memo or this file. I used Claude to help me
think through the clustering logic and spot-check edge cases in the quality audit,
then rewrote conclusions in my own words after verifying them against the data.

---

## Key Decisions and Assumptions

**Taxonomy approach:** I clustered non-safety use cases by hand using keyword rules
rather than a full embedding model. This is intentional — with 231 items and clear
thematic structure visible in a first read, a rule-based classifier is faster,
more auditable, and easier to explain than a black-box embedding. I flagged the
"Other / Unclassified" bucket (51 items) explicitly rather than forcing everything
into a theme.

**What I treated as signal vs. noise:** I kept admin/commercial items in the dataset
but flagged them separately rather than deleting them, so the counts are transparent.
"Loss Prevention & Shrink" shows only 7 instances but I ranked it #3 because the
evidence quotes are unusually specific and dollar-grounded — raw count undersells it,
probably because LP directors aren't on training calls.

**Cross-bucket duplicates:** I identified 28 exact-match cross-bucket labels and
several more fuzzy matches. For the opportunity analysis I used the non-safety
instances only (not the duplicates) to avoid double-counting. This means the
true non-safety signal is somewhat smaller than the raw 231 number suggests.

**What I didn't do:** I did not attempt to validate whether the extracted evidence
quotes actually support the label. Spot-checking ~15 items suggests roughly 85–90%
alignment, but a systematic evidence-label accuracy audit would take longer than the
2–3 hours the brief suggests.

---

## Files in This Submission

- `memo.md` — 1–2 page business memo answering the two core questions
- `analysis.py` — Python script with full data loading, quality audit, taxonomy,
  and evidence summary. No external dependencies beyond the standard library.
  Run from the repo root: `python3 submission/analysis.py`
- `SUBMISSION.md` — this file
