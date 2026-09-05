"""
# Meridian Relay policy evidence

This file belongs to the Meridian Relay repository snapshot used for the 2034 archive
rollout. The repository contains proposals, implementation notes, test fixtures, and
approval history. A value is not current merely because it is precise, appears in code,
or was repeated by a participant. Status, scope, effective revision, and units matter.

The policy concerns the normalized delivery ledger: queryable event retention, the review
schedule, the ordinary implementation spending cap, the late-event alert trigger, the
accountable owner, the committed date, the verification room, and the escalation code.
The emergency override request is a separate change request. It may mention nearby
numbers, but it does not alter the baseline unless the approval history explicitly says
that it was approved and effective. The words draft, proposed, rejected, superseded,
approved, and effective are used deliberately throughout the archive.

When this file cites another record, the citation is a lead to reconcile, not a substitute
for reading the cited record. Dates are calendar dates in UTC. Fractions are stored between
zero and one; percentages in prose are display forms and must not silently replace a
fraction-valued policy field. Dollars are whole US dollars. A team may own an action while
only a named person owns the policy decision.

## Alert runtime module

Repository role: current executable source for threshold and escalation code

The runtime export represented here is:

    THRESHOLD_FRACTION = "0.82"
    ESCALATION_CODE = "MERIDIAN-9"

The dashboard formatter and emergency branch are separate consumers.

## Evidence ledger

### Record 01 — 2034-06-20 — Jon Bell

Subject: approval

THRESHOLD_FRACTION = '0.82' is the canonical policy representation selected by AP-17.

Implication: Return the string 0.82.

### Record 02 — 2034-06-20 — Nora Vale

Subject: route

ESCALATION_CODE = 'MERIDIAN-9' links the alert to the policy incident route.

Implication: Return MERIDIAN-9.

### Record 03 — 2034-06-22 — Jon Bell

Subject: dashboard conversion

The UI multiplies 0.82 by 100 for an 82% label. The conversion is presentation only and is not written back to policy storage.

Implication: Do not output 82%.

### Record 04 — 2034-06-27 — Release bot

Subject: production import

The production evaluator imports both constants from the AP-17 generated module. ALERT-90 remains a dashboard panel identifier.

Implication: The current route and trigger are corroborated.

### Record 05 — 2034-06-28 — Jon Bell

Subject: old route

RELAY-17 is the rollout work ticket and MERIDIAN-8 was used by a pre-approval test. Neither is the effective escalation code.

Implication: Plausible identifiers are stale.

### Record 06 — 2034-06-29 — Ishan Reed

Subject: comparison

The evaluator compares Decimal('0.82') with the normalized late-event fraction and refuses percent-form input in the policy layer.

Implication: Units are checkable.

### Record 07 — 2034-07-01 — Mara Chen

Subject: authority

An alert firing opens the policy route but cannot approve MR-42 or change retention automatically.

Implication: Operational response is not policy amendment.

### Record 08 — 2034-07-03 — Release bot

Subject: checksum

The alert module checksum matches AP-17 and relay-7.3.

Implication: Current module belongs to the effective lineage.

## Reading rule

Use the record's status and scope together. A historical value can explain a test fixture, a migration branch, or a rejected request without being an instruction for the current rollout. A display label can be useful to an operator while still being the wrong representation for the policy schema. If two records disagree, follow the later effective approval for this policy and preserve the stated unit.
"""
