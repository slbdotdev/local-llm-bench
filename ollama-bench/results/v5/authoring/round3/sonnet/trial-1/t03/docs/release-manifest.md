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

## Release manifest

Repository role: binds the current modules to effective packet and deployment scope

## Evidence ledger

### Record 01 — 2034-06-27 — Release bot

Subject: package

relay-7.3 packages policy.py, finance.py, alerts.py, scheduler.py, ownership.py, and locations.py from AP-17.1.

Implication: The code set is current.

### Record 02 — 2034-06-27 — Release bot

Subject: policy hashes

Each module checksum is recorded so a stale local copy can be detected during audit.

Implication: Source lineage matters.

### Record 03 — 2034-06-27 — Nora Vale

Subject: scope

The package serves ordinary normalized delivery events and excludes legal-hold tooling and override-simulation.

Implication: Do not merge special cases.

### Record 04 — 2034-06-27 — Carmen Wu

Subject: finance

The package exports the whole-dollar ordinary cap after validation costs.

Implication: Use finance source for amount.

### Record 05 — 2034-06-27 — Jon Bell

Subject: alert

The package exports the normalized fraction and policy escalation code.

Implication: Use alert source for threshold and code.

### Record 06 — 2034-06-27 — Mara Chen

Subject: governance

The package exports the named owner and effective deadline.

Implication: Use governance source for identity and date.

### Record 07 — 2034-06-27 — Facilities

Subject: location

The package exports the room for verification review.

Implication: Use the physical room.

### Record 08 — 2034-07-03 — Release bot

Subject: lineage

The manifest remains the latest effective release manifest in this snapshot.

Implication: No later amendment is present.

## Reading rule

Use the record's status and scope together. A historical value can explain a test fixture, a migration branch, or a rejected request without being an instruction for the current rollout. A display label can be useful to an operator while still being the wrong representation for the policy schema. If two records disagree, follow the later effective approval for this policy and preserve the stated unit.
