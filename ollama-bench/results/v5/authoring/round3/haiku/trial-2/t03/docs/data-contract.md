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

## Ledger data contract

Repository role: defines the exact scope of the values consumed by the runtime

## Evidence ledger

### Record 01 — 2034-05-02 — Ishan Reed

Subject: event identity

A normalized delivery event has an immutable event_id, source watermark, delivery state, and diagnostic context. Retention policy applies to the event record, not to a checkpoint or a support ticket.

Implication: Do not use identifiers or checkpoint ages as policy values.

### Record 02 — 2034-05-04 — Nadia Holt

Subject: archive scope

The primary archive is queryable by support and analytics. The audit stream documents movement and is governed by a separate operational lifecycle.

Implication: The requested retention is for primary queryability.

### Record 03 — 2034-05-06 — Jon Bell

Subject: metric scope

late_event_fraction is computed after normalization and watermark reconciliation. Raw ingress counts and dashboard percentages are derived views.

Implication: The threshold source must identify the normalized fraction.

### Record 04 — 2034-05-08 — Eli Ramos

Subject: partitioning

Partitions are independently checkpointed. A partition checkpoint can be retried without re-authorizing the archive lifecycle or spending cap.

Implication: Implementation mechanics do not alter approval.

### Record 05 — 2034-05-10 — Carmen Wu

Subject: cost scope

The cost contract includes storage migration and validation work but excludes company incident purchasing and legal response costs.

Implication: Use the ordinary cap, not exception spending.

### Record 06 — 2034-05-12 — Mara Chen

Subject: owner scope

The policy owner can resolve a cross-module contract mismatch. The team that implements a serializer is an action assignee, not the policy owner.

Implication: Return the named accountable person.

### Record 07 — 2034-05-14 — Facilities

Subject: review scope

The verification review covers contract conformance in Juniper-2. The remote bridge and building zone are logistical metadata.

Implication: Return the physical room.

### Record 08 — 2034-05-16 — Nora Vale

Subject: effective schema

Contract version 17.1 is effective only when AP-17.1 is effective. A fixture with the same field names can belong to an older revision.

Implication: Schema shape alone is insufficient.

## Reading rule

Use the record's status and scope together. A historical value can explain a test fixture, a migration branch, or a rejected request without being an instruction for the current rollout. A display label can be useful to an operator while still being the wrong representation for the policy schema. If two records disagree, follow the later effective approval for this policy and preserve the stated unit.
