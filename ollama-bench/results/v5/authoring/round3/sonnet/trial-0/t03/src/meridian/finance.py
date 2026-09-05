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

## Finance runtime module

Repository role: current executable source for the ordinary cap

The runtime export represented here is:

    ORDINARY_CAP_USD = 47200

The emergency purchasing constant is deliberately kept in a separate adapter.

## Evidence ledger

### Record 01 — 2034-06-18 — Carmen Wu

Subject: calculation

Base storage and migration labor totalled 45000 dollars; two validation runs totalled 2200 dollars. The ordinary package therefore totals 47200 dollars.

Implication: Validation work is part of the approved cap.

### Record 02 — 2034-06-20 — Carmen Wu

Subject: approval

ORDINARY_CAP_USD = 47200 is emitted from AP-17. The type is int and the unit is whole US dollars.

Implication: Return integer 47200.

### Record 03 — 2034-06-20 — Procurement

Subject: separate threshold

INCIDENT_PURCHASE_THRESHOLD_USD = 50000 belongs to company incident procedure and is not imported into the ordinary policy object.

Implication: Do not confuse control scopes.

### Record 04 — 2034-06-27 — Release bot

Subject: build

The production package imports ordinary_cap_usd from this module and omits the override-simulation package.

Implication: Build inclusion provides current-status evidence.

### Record 05 — 2034-06-28 — Carmen Wu

Subject: rounding

The 48000 number in the planner is a rounded reserve-inclusive estimate. The checker for finance rejects it as a cap.

Implication: A nearby round number is a trap.

### Record 06 — 2034-06-29 — Nora Vale

Subject: audit label

The finance audit names the selected value 'ordinary cap' and separately labels forecasts, reserves, and emergency approvals.

Implication: Labels carry authority.

### Record 07 — 2034-07-01 — Mara Chen

Subject: variance

Actual spend may be below the cap; unused headroom does not create a new policy value.

Implication: Do not calculate a different amount.

### Record 08 — 2034-07-02 — Release bot

Subject: provenance

The source packet for the exported integer is AP-17, effective after dependency checks.

Implication: Current source is tied to the effective approval.

## Reading rule

Use the record's status and scope together. A historical value can explain a test fixture, a migration branch, or a rejected request without being an instruction for the current rollout. A display label can be useful to an operator while still being the wrong representation for the policy schema. If two records disagree, follow the later effective approval for this policy and preserve the stated unit.
"""
