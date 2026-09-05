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

## Configuration assembly

Repository role: assembles current fields from separate approved components

The assembly is conceptually:

    current = policy + finance + alerting + scheduler + governance + location

Every component must be from the same effective packet; the assembly does not merge
draft or rejected values.

## Evidence ledger

### Record 01 — 2034-06-27 — Release bot

Subject: assembly

The production configuration assembles policy, finance, alerting, scheduler, governance, and location components only when all cite AP-17.1.

Implication: Reconciliation across modules is required.

### Record 02 — 2034-06-27 — Nora Vale

Subject: cadence and retention

The policy component contributes biweekly and 45 days for ordinary ledger operation.

Implication: These are current fields.

### Record 03 — 2034-06-27 — Carmen Wu

Subject: cap

The finance component contributes ordinary_cap_usd 47200 as an integer and excludes emergency purchasing.

Implication: Use ordinary scope.

### Record 04 — 2034-06-27 — Jon Bell

Subject: alert

The alert component contributes threshold 0.82 and route MERIDIAN-9; the UI's 82% label is derived later.

Implication: Keep fraction representation.

### Record 05 — 2034-06-27 — Mara Chen

Subject: governance

The governance component contributes Mara Chen and 2034-11-18 after the dependency gate.

Implication: Use named owner and committed ISO date.

### Record 06 — 2034-06-27 — Facilities

Subject: location

The location component contributes Juniper-2 for the verification review.

Implication: Use physical room.

### Record 07 — 2034-06-27 — Release bot

Subject: excluded assembly

The override-simulation object contains MR-42 values but fails the effective-packet requirement and is not merged.

Implication: A plausible complete object can still be excluded.

### Record 08 — 2034-07-03 — Nora Vale

Subject: no mutation

No post-assembly calendar, dashboard, or forecast update changes the effective configuration without a new packet.

Implication: Do not infer changes from later-looking notes.

## Reading rule

Use the record's status and scope together. A historical value can explain a test fixture, a migration branch, or a rejected request without being an instruction for the current rollout. A display label can be useful to an operator while still being the wrong representation for the policy schema. If two records disagree, follow the later effective approval for this policy and preserve the stated unit.
"""
