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

## Migration plan

Repository role: connects implementation steps to the approved baseline and exposes duration traps

## Evidence ledger

### Record 01 — 2034-06-05 — Eli Ramos

Subject: inventory

The team inventories twelve source partitions and two legacy consumers before starting the archive migration. Inventory count is not the retention count.

Implication: Numbers in a plan have different meanings.

### Record 02 — 2034-06-07 — Eli Ramos

Subject: dry run

The largest dry run is expected to take 36 hours, with a checkpoint after each partition. This estimate may change without changing the committed date.

Implication: Do not turn a duration into a deadline or retention value.

### Record 03 — 2034-06-09 — Nadia Holt

Subject: deletion rehearsal

Deletion rehearsal verifies eligibility at ordinary age 45 and separately tests that a legal hold blocks deletion.

Implication: The ordinary baseline remains distinct from holds.

### Record 04 — 2034-06-11 — Ishan Reed

Subject: duplicate suppression

A replayed source watermark must not create a second durable event. Duplicate suppression is a correctness property, not an escalation trigger.

Implication: Do not use checkpoint behavior for alert threshold.

### Record 05 — 2034-06-13 — Carmen Wu

Subject: validation budget

Validation for both legacy consumers is included in the 47200-dollar ordinary package. The reserve-inclusive planner number is not authorization.

Implication: Validation explains the selected cap.

### Record 06 — 2034-06-15 — Mara Chen

Subject: gate owner

Mara Chen coordinates the dependency gate and is the person to contact if a validation result changes the policy interpretation.

Implication: Gate ownership agrees with governance evidence.

### Record 07 — 2034-06-17 — Facilities

Subject: review booking

The final evidence review is booked for Juniper-2. Calendar reminders may use a shortened building label.

Implication: Use the room, not the calendar grouping.

### Record 08 — 2034-06-19 — Nora Vale

Subject: date

The plan's committed completion date is 2034-11-18 after customer notice and validation. The earlier agenda target was never a commitment.

Implication: Date semantics are explicit.

## Reading rule

Use the record's status and scope together. A historical value can explain a test fixture, a migration branch, or a rejected request without being an instruction for the current rollout. A display label can be useful to an operator while still being the wrong representation for the policy schema. If two records disagree, follow the later effective approval for this policy and preserve the stated unit.
