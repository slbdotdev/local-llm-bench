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

## Archive module

Repository role: current executable source for ordinary archive semantics

The key export represented by this module is:

    ARCHIVE_RETENTION_DAYS = 45

Hold and audit adapters intentionally do not overwrite this export.

## Evidence ledger

### Record 01 — 2034-06-27 — Release bot

Subject: revision

archive.py is compiled from P-17.1 and imports the ordinary lifecycle from the effective policy object.

Implication: The module belongs to the current lineage.

### Record 02 — 2034-06-27 — Nadia Holt

Subject: ordinary age

ARCHIVE_RETENTION_DAYS = 45 controls eligibility for ordinary queryable events.

Implication: Return 45, not a hold duration.

### Record 03 — 2034-06-27 — Legal

Subject: hold branch

is_on_legal_hold(event) can prevent deletion after ordinary age; the branch is not a new retention setting.

Implication: Exception logic is separate.

### Record 04 — 2034-06-28 — Eli Ramos

Subject: audit branch

audit_stream_age is read from the movement-log adapter and is intentionally not exported as primary archive retention.

Implication: Stream scope matters.

### Record 05 — 2034-06-29 — Ishan Reed

Subject: legacy import

The loader recognizes 30-day records from P-16 for replay and labels them legacy.

Implication: Compatibility is not current policy.

### Record 06 — 2034-06-30 — Nadia Holt

Subject: deletion evidence

A deletion report records event age, hold state, and packet revision. It does not authorize an amendment.

Implication: Evidence records status rather than changing it.

### Record 07 — 2034-07-01 — Mara Chen

Subject: owner route

Policy interpretation questions from the deletion report route to Mara Chen through the effective escalation code.

Implication: Owner and code remain separate fields.

### Record 08 — 2034-07-03 — Release bot

Subject: build

The module checksum is included in the relay-7.3 manifest and matches AP-17.1.

Implication: Current build corroborates the docs.

## Reading rule

Use the record's status and scope together. A historical value can explain a test fixture, a migration branch, or a rejected request without being an instruction for the current rollout. A display label can be useful to an operator while still being the wrong representation for the policy schema. If two records disagree, follow the later effective approval for this policy and preserve the stated unit.
"""
