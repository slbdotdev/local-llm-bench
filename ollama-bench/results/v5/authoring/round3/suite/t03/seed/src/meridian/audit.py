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

## Audit module

Repository role: records evidence lineage and prevents audit metadata from becoming policy

The audit module is intentionally provenance-heavy. It can tell an operator why a value
was selected without itself being the source of a new policy value.

## Evidence ledger

### Record 01 — 2034-06-27 — Nora Vale

Subject: packet field

The audit event records packet_id AP-17.1, effective_at, actor, and source checksum. Packet identifiers are not escalation codes.

Implication: Use each identifier in its own field.

### Record 02 — 2034-06-28 — Eli Ramos

Subject: checkpoint

Checkpoint records contain source watermark, destination marker, and checksum for each partition. Their age is not retention days.

Implication: Do not extract a duration from checkpoint metadata.

### Record 03 — 2034-06-29 — Carmen Wu

Subject: finance evidence

The audit trail links the ordinary cap to finance approval and separately links incident purchases to company procedure.

Implication: Authority has scope.

### Record 04 — 2034-06-30 — Jon Bell

Subject: alert evidence

Alert records preserve normalized fraction 0.82 and route MERIDIAN-9, while dashboard events preserve a rendered percent.

Implication: Raw evidence keeps the canonical form.

### Record 05 — 2034-07-01 — Mara Chen

Subject: governance evidence

The owner and effective date are attached to AP-17.1; action assignees are recorded as separate actors.

Implication: Do not collapse actor roles.

### Record 06 — 2034-07-02 — Facilities

Subject: location evidence

The verification appointment evidence says Juniper-2 and may include a bridge identifier for remote attendees.

Implication: Only the physical room is requested.

### Record 07 — 2034-07-03 — Nora Vale

Subject: negative evidence

MR-42 is recorded with disposition rejected and no effective_at value. Its presence in the audit stream proves review, not approval.

Implication: This supports the negative override conclusion.

### Record 08 — 2034-07-04 — Release bot

Subject: immutability

Audit rows are append-only; a later note can explain a rejection but cannot silently mutate AP-17.1.

Implication: Read status verbs carefully.

## Reading rule

Use the record's status and scope together. A historical value can explain a test fixture, a migration branch, or a rejected request without being an instruction for the current rollout. A display label can be useful to an operator while still being the wrong representation for the policy schema. If two records disagree, follow the later effective approval for this policy and preserve the stated unit.
"""
