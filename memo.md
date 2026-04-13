# Non-Safety Opportunity Analysis: Voxel Customer Calls
**To:** Voxel Product & GTM  
**From:** Candidate submission  
**Date:** April 2026  
**Dataset:** 99 anonymized call JSONs, 471 safety UCs, 231 non-safety UCs

---

## Bottom Line Up Front

Three non-safety themes surface repeatedly across the call corpus with real customer urgency:
**operational efficiency**, **security and access control**, and **loss prevention/shrink**.
The extraction pipeline has meaningful quality problems — roughly 12% of non-safety labels
are duplicates of safety labels, and ~6% are admin or commercial items, not product use cases.
Neither finding invalidates the signal, but both require cleaning before any prioritization
work should be taken at face value.

---

## What's Actually Showing Up in Calls

After normalizing 231 non-safety use-case instances into a working taxonomy, the distribution
breaks down as follows:

| Theme | Instances | Distinct Calls |
|---|---|---|
| Operational Efficiency & Flow | 66 | 42 |
| Analytics, Reporting & Workflow | 49 | — |
| Platform Adoption & Actions | 24 | — |
| Security & Access Control | 21 | 19 |
| Loss Prevention & Shrink | 7 | 7 |
| Customer / Retail Analytics | 7 | — |
| Quality Control / Food Safety | 6 | — |
| Energy & Facility Mgmt | 4 | — |

"Operational Efficiency" and "Analytics/Reporting" are large partly because the pipeline
over-captures anything mentioning workflows, actions, or heatmaps — tools that also
appear in the safety bucket. That said, there is genuine signal inside both.

---

## Top 3 Opportunities

### 1. Operational Efficiency & Flow (strongest signal, 42 calls)

Customers want to use Voxel's existing detection capabilities to answer throughput questions,
not just safety questions. The same PIT-proximity and zone-detection infrastructure that
catches near-misses can answer: How long is a dock door sitting open? Are forklifts parking
in aisles and killing flow? Is there a conveyor backlog building at shift change?

Representative customer quotes:
- *"Trailer detention time and turnaround time — from the time we get an inbound load to
  when our last truck leaves — that's 12 to 13 hours. Is there a way to see that?"*
  (Grit Stack Operations)
- *"Why are we moving around the entire bay when what he's going after is a moderate distance
  away? We've got some efficiency gains hiding here."* (Mason Line Supply)
- *"Is there anything where you guys can see where boxes are starting to back up on a
  conveyor?"* (Cobalt Ridge Fabrication)

**Why it matters:** This is the clearest path to expanding Voxel's value proposition beyond
safety buyers. Operations leaders who don't own the safety budget will pay for uptime and
throughput data. The detection work is largely already done.

---

### 2. Security & Access Control (19 calls, unprompted in almost every case)

Customers independently raise access control and after-hours monitoring without being
prompted. This comes up across verticals — warehouses, retail, manufacturing, and port
facilities. The specific asks cluster around: time-based no-pedestrian zones (employees
who shouldn't be in a zone after lights-out), perimeter breach detection, and — more
controversially — facial recognition for incident investigation.

Representative quotes:
- *"There's times super late at night — nobody should be back there. Could you flip
  on an alert if someone is?"* (Kodiak Point Fabrication)
- *"Their special project is building out use cases slanted more to the security side
  of the house."* (Mason Line Supply)
- *"You have an employee who's no longer with the company — we can do recognition for
  that."* (Pioneer Peak Manufacturing — Voxel rep describing capability)

**Why it matters:** Security is already a stated use case in several contracts.
The opportunity is to formalize it as a distinct product tier or add-on rather than
letting it fall through as an ad-hoc customer ask. Facial recognition is a landmine
(privacy regulation, BIPA exposure) and should be explicitly scoped out of any
security offering until legal review is complete.

---

### 3. Loss Prevention & Shrink (7 calls, but concentrated ROI)

Smaller in raw count, but every instance comes with a dollar figure attached or a
clear link to P&L. Customers are asking Voxel to detect PIT impacts on product and
racking (infrastructure damage), connect near-miss data to AP claims investigations,
and alert staff when high-shrink items are picked up in retail. This is a different
buyer than the safety manager — it's the head of operations or the LP director.

Representative quotes:
- *"I may have property damage. The door might be broken. Equipment repair needed on
  the PIT. That's all money."* (Trail Lift Works)
- *"They had to replace the door three different times — cost them up to [REDACTED]."*
  (Mesa Span Solutions)
- *"That product could have fell off — that could have been a loss for us. We can now
  show that on camera."* (Orion Forge Industrial)

**Why it matters:** LP is a natural expansion buyer who can be sold on existing
detection (PIT monitoring, zone monitoring) reframed around financial loss rather than
injury rate. The evidence is thin relative to the other two themes, which is partly a
data artifact — LP buyers may not be on the training and onboarding calls captured here.

---

## Extraction Quality Issues

The pipeline has four identifiable problems, in rough order of severity:

**1. Cross-bucket duplication (most serious).** 28 labels appear verbatim in both
`safety_use_cases` and `nonsafety_use_cases`. An additional set of concepts appears in
both with slight wording differences: heatmaps, ergonomics detection, PIT parking
duration, and the Actions workflow. This creates double-counting and makes the non-safety
list appear larger and more diverse than it really is.

**2. Thin evidence.** 34 of 231 non-safety use cases (15%) have only one supporting
quote. One quote is often a passing mention or an open question, not a genuine customer
expression of need. These items should be flagged, not discarded, but they carry
substantially less weight than items with two or more independent quotes.

**3. Admin and commercial items.** Eight items in the non-safety bucket are about
contract renewals, scheduling, vendor evaluations, and stakeholder alignment — not
product use cases at all. Examples: "Contract renewal language clarification" and
"Longer-term commercial options" (Summit Span Solutions). These inflate counts and
dilute focus.

**4. Label inflation / overspecificity.** Labels like "Reduce Chipotle dry dock
congestion by splitting shifts" or "Per-user language localization to Spanish" are
customer-specific implementation notes that got promoted to use cases. They're useful
as raw evidence but shouldn't be treated as generalizable product opportunities without
verification across multiple accounts.

---

## One Practical Improvement

**Add an embedding-based dedup pass after extraction.**

The pipeline currently produces labels independently per call, with no cross-document
deduplication or bucket-consistency check. A lightweight fix:

1. Embed every extracted label with a small sentence encoder (sentence-transformers
   `all-MiniLM-L6-v2` runs in seconds on this corpus).
2. For any label whose cosine similarity to a label in the *opposite* bucket exceeds
   ~0.90, flag it for a 10-second human review rather than allowing the auto-assignment
   to stand.
3. Maintain a blocklist of admin phrases ("contract renewal", "vendor evaluation",
   "scheduling") that are always excluded from both use-case lists at extraction time.

This is roughly a day of engineering work. On this corpus it would surface and
resolve most of the 28 cross-bucket duplicates and the 8 admin items automatically.
It would not fix the underlying LLM tendency to over-classify — that requires
prompt-side work — but it meaningfully improves output trustworthiness before
that work is done.
