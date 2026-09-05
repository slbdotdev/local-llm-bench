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

## Effective packet AP-17.1

Repository role: chronological history showing revisions, status verbs, and the effective boundary

This historical record is retained so the current packet can be distinguished from earlier and rejected branches.

## Evidence ledger

### Record 01 — 2034-06-27 — Release bot

Subject: gate

Schema, finance, alerting, governance, and dependency checks passed for AP-17.

Implication: effective

### Record 02 — 2034-06-27 — Release bot

Subject: policy export

The production export uses biweekly and 45 days for ordinary operation.

Implication: effective

### Record 03 — 2034-06-27 — Release bot

Subject: finance export

The production export uses 47200 whole dollars and keeps incident purchasing separate.

Implication: effective

### Record 04 — 2034-06-27 — Release bot

Subject: alert export

The production export uses 0.82 and MERIDIAN-9.

Implication: effective

### Record 05 — 2034-06-27 — Release bot

Subject: governance export

The production export names Mara Chen, 2034-11-18, and Juniper-2.

Implication: effective

### Record 06 — 2034-06-28 — Nora Vale

Subject: scope

The effective marker applies to the ordinary normalized delivery ledger only.

Implication: scoped

### Record 07 — 2034-06-29 — Mara Chen

Subject: amendment rule

A future amendment must be independently approved and made effective.

Implication: change control

### Record 08 — 2034-07-03 — Release bot

Subject: lineage

No later effective packet supersedes AP-17.1 in this snapshot.

Implication: current

## Reading rule

Use the record's status and scope together. A historical value can explain a test fixture, a migration branch, or a rejected request without being an instruction for the current rollout. A display label can be useful to an operator while still being the wrong representation for the policy schema. If two records disagree, follow the later effective approval for this policy and preserve the stated unit.
