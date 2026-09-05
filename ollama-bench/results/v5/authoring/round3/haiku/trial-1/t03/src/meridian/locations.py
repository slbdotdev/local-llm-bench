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

## Verification location module

Repository role: current executable source for the physical review room

The runtime export represented here is:

    VERIFICATION_ROOM = "Juniper-2"

Building and bridge metadata remain separate from the physical-room field.

## Evidence ledger

### Record 01 — 2034-06-20 — Facilities

Subject: approval attachment

VERIFICATION_ROOM = 'Juniper-2' is the physical room in the AP-17 governance attachment.

Implication: Return Juniper-2.

### Record 02 — 2034-06-21 — Facilities

Subject: building labels

Juniper is the building zone, Juniper-1 was an earlier candidate, and Juniper-2 is the booked room.

Implication: The shortest label is incomplete.

### Record 03 — 2034-06-22 — Nora Vale

Subject: remote bridge

The bridge name is relay-review-17 and may be used by remote attendees. It is not the room field.

Implication: Do not return the bridge.

### Record 04 — 2034-06-27 — Release bot

Subject: effective export

The production schedule exports Juniper-2 and excludes the old agenda location.

Implication: Current build corroborates the attachment.

### Record 05 — 2034-06-28 — Facilities

Subject: capacity

Juniper-2 supports the validation review's expected attendance; the capacity note is logistics, not another policy field.

Implication: Only the normalized room is needed.

### Record 06 — 2034-06-29 — Mara Chen

Subject: appointment

The room belongs to the verification review, not to the routine biweekly meeting if that meeting is remote.

Implication: Scope of the room field is explicit.

### Record 07 — 2034-07-01 — Nora Vale

Subject: calendar sync

A calendar sync may display 'Juniper' for grouping, while the source appointment preserves Juniper-2.

Implication: Use source precision.

### Record 08 — 2034-07-03 — Release bot

Subject: checksum

The location export matches AP-17 and the effective schedule manifest.

Implication: Current record is consistent.

## Reading rule

Use the record's status and scope together. A historical value can explain a test fixture, a migration branch, or a rejected request without being an instruction for the current rollout. A display label can be useful to an operator while still being the wrong representation for the policy schema. If two records disagree, follow the later effective approval for this policy and preserve the stated unit.
"""
