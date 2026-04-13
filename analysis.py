import json
import os
import glob
from collections import Counter, defaultdict

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "safety-nonsafety")
if not os.path.isdir(DATA_DIR):
    DATA_DIR = "safety-nonsafety"
files = sorted(glob.glob(os.path.join(DATA_DIR, "*.json")))

all_safety = []
all_nonsafety = []
meetings = []

for f in files:
    with open(f) as fh:
        d = json.load(fh)
    fid = os.path.basename(f)
    title = d.get("meeting_title", "")
    start = d.get("start_time", "")
    meetings.append({"file": fid, "title": title, "start": start})
    for uc in d.get("extraction", {}).get("safety_use_cases", []):
        all_safety.append(
            {"file": fid, "title": title, "label": uc.get("label", ""),
             "desc": uc.get("description", ""), "evidence": uc.get("evidence", [])}
        )
    for uc in d.get("extraction", {}).get("nonsafety_use_cases", []):
        all_nonsafety.append(
            {"file": fid, "title": title, "label": uc.get("label", ""),
             "desc": uc.get("description", ""), "evidence": uc.get("evidence", [])}
        )

print(f"Loaded {len(files)} files → {len(all_safety)} safety use cases, {len(all_nonsafety)} non-safety use cases\n")


safety_labels_lc    = {x["label"].lower() for x in all_safety}
nonsafety_labels_lc = {x["label"].lower() for x in all_nonsafety}
cross_bucket = safety_labels_lc & nonsafety_labels_lc

print(f"Issue 1 — {len(cross_bucket)} labels show up in both the safety and non-safety buckets (exact match):")
for lbl in sorted(cross_bucket):
    print(f"  · {lbl}")

thin_evidence = [x for x in all_nonsafety if len(x["evidence"]) == 1]
print(f"\nIssue 2 — {len(thin_evidence)} of {len(all_nonsafety)} non-safety use cases "
      f"({100*len(thin_evidence)//len(all_nonsafety)}%) are backed by only a single quote.")

ADMIN_KEYWORDS = [
    "contract", "renewal", "scheduling", "stakeholder alignment", "commercial",
    "vendor evaluation", "budget", "longer-term", "update contracts",
    "timing follow-up", "getting sites onto the same schedule",
]
admin_items = [
    x for x in all_nonsafety
    if any(kw in x["label"].lower() for kw in ADMIN_KEYWORDS)
]
print(f"\nIssue 3 — {len(admin_items)} items look like admin or commercial notes, not product use cases:")
for x in admin_items:
    print(f"  [{x['title']}] → {x['label']}")

FUZZY_PAIRS = [
    ("heatmap",     "heatmap",     "Heatmaps"),
    ("ergonomic",   "ergonomic",   "Ergonomics detection"),
    ("parking",     "parking",     "PIT parking duration"),
    ("food safety", "food safety", "Food-safety PPE"),
    ("action",      "action",      "Actions workflow"),
]
print("\nIssue 4 — Same concept, split across both buckets with slightly different wording:")
for kw_s, kw_ns, note in FUZZY_PAIRS:
    s_hits  = [x["label"] for x in all_safety    if kw_s  in x["label"].lower()]
    ns_hits = [x["label"] for x in all_nonsafety if kw_ns in x["label"].lower()]
    if s_hits and ns_hits:
        print(f"\n  {note}")
        print(f"    Safety side:     {s_hits[:2]}")
        print(f"    Non-safety side: {ns_hits[:2]}")


TAXONOMY = {
    "Operational Efficiency & Flow": [
        "operational", "efficiency", "congestion", "flow", "idle", "dwell",
        "turn-time", "turnaround", "productivity", "bottleneck", "conveyor",
        "obstruction", "pallet", "aisle", "parking duration", "trailer detention",
        "door duration", "open door", "dock door",
    ],
    "Security & Access Control": [
        "security", "access", "restricted", "unauthorized", "intrusion",
        "perimeter", "after-hours", "facial recognition", "license plate",
        "identity", "no-parking zone", "no\u2011parking zone",
    ],
    "Loss Prevention & Shrink": [
        "shrink", "theft", "loss prevention", "lp/", "property damage",
        "product damage", "damage detect", "reduce shrink", "near-miss",
        "driver exoneration",
    ],
    "Analytics, Reporting & Workflow": [
        "reporting", "analytics", "dashboard", "export", "api", "integration",
        "heatmap", "benchmark", "snapshot", "summary", "email", "digest",
        "bi tool", "executive", "year-over-year",
    ],
    "Platform Adoption & Action Management": [
        "action", "assign", "track", "workflow", "accountability",
        "gamif", "leaderboard", "adoption", "engagement", "board",
        "role-based", "training", "coaching",
    ],
    "Customer / Retail Analytics": [
        "customer", "retail", "merchandising", "end-cap", "service alert",
        "front-of-store", "liability reduction",
    ],
    "Quality Control & Food Safety": [
        "quality", "food safety", "ppe compliance", "hair net",
        "hygiene", "controlled-environment", "quality inspection",
    ],
    "Energy & Facility Management": [
        "energy", "freezer", "cooler", "cold storage",
    ],
    "Other / Unclassified": [],
}

bucketed = defaultdict(list)
for uc in all_nonsafety:
    ll = (uc["label"] + " " + uc["desc"]).lower()
    placed = False
    for theme, kws in TAXONOMY.items():
        if theme == "Other / Unclassified":
            continue
        if any(kw in ll for kw in kws):
            bucketed[theme].append(uc)
            placed = True
            break
    if not placed:
        bucketed["Other / Unclassified"].append(uc)

print("\n\nNon-safety use cases grouped into themes:")
for theme, items in sorted(bucketed.items(), key=lambda x: -len(x[1])):
    print(f"\n  {theme} ({len(items)} use cases)")
    unique_labels = list(dict.fromkeys(x["label"] for x in items))
    for lbl in unique_labels[:6]:
        print(f"    \u2013 {lbl}")
    if len(unique_labels) > 6:
        print(f"    \u2026 and {len(unique_labels)-6} more")


TOP3 = [
    "Operational Efficiency & Flow",
    "Security & Access Control",
    "Loss Prevention & Shrink",
]

print("\n\nTop 3 non-safety opportunities:")
for theme in TOP3:
    items = bucketed[theme]
    calls = list(dict.fromkeys(x["title"] for x in items))
    print(f"\n{'\u2500'*60}")
    print(f"  {theme}")
    print(f"  {len(items)} instances across {len(calls)} calls")
    print(f"  Calls include: {', '.join(calls[:4])}")
    print(f"\n  What customers actually said:")
    shown = 0
    for uc in items:
        if shown >= 4:
            break
        for ev in uc["evidence"][:1]:
            print(f"    [{uc['title']}]\n    \"{ev['quote'][:120]}\"\n")
            shown += 1


print("""
\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
One practical improvement to the extraction pipeline
\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500

The biggest problem is bucket confusion \u2014 28 labels land in both safety and
non-safety, and many more share the same concept with slightly different wording.
The pipeline has no cross-document consistency check at all right now.

A fix that's roughly one day of engineering:

  1. After extraction, embed every label with a small sentence encoder
     (sentence-transformers/all-MiniLM-L6-v2 is fast enough for this corpus).
  2. Any label with cosine similarity > 0.90 to something in the opposite bucket
     gets flagged for a quick human review instead of auto-assigned.
  3. Keep a short blocklist of admin phrases ("contract renewal", "vendor evaluation",
     "scheduling") that get filtered from both lists at extraction time.

This won't fix the underlying LLM tendency to over-classify, but it catches most
of the cross-bucket duplicates and admin noise before they reach analysts.
""")
