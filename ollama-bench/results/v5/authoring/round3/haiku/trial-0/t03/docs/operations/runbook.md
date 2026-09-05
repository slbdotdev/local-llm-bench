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

## Operations runbook

Repository role: explains how operators consume the approved settings

## Evidence ledger

### Record 01 — 2034-06-28 — Eli Ramos

Subject: review job

The review job is created every fourteen days after the rollout anchor. It is not an ingestion pause and does not change event processing.

Implication: The cadence field controls reviews only.

### Record 02 — 2034-06-28 — Nora Vale

Subject: archive query

Support may query ordinary records for 45 days. A legal hold changes deletion eligibility through a separate service and must be labelled as such in evidence.

Implication: Ordinary retention remains 45 days.

### Record 03 — 2034-06-28 — Jon Bell

Subject: alert evaluation

At normalized fraction 0.82 the policy alert enters the escalation path. A graph line at 0.90 is a visual red band and does not replace the trigger.

Implication: The policy threshold is 0.82.

### Record 04 — 2034-06-28 — Mara Chen

Subject: owner route

Cross-module disputes go to Mara Chen. The Relay Platform rotation executes the runbook but does not become the decision owner.

Implication: Execution and accountability differ.

### Record 05 — 2034-06-28 — Facilities

Subject: verification appointment

The evidence review is booked in Juniper-2. Remote attendees use the bridge; the bridge name is not the physical room.

Implication: Keep the room field physical and exact.

### Record 06 — 2034-06-28 — Nora Vale

Subject: deadline

The committed implementation date is 2034-11-18. The dry run has a target duration but that duration is not the deadline.

Implication: Use the committed date.

### Record 07 — 2034-06-28 — Jon Bell

Subject: tracker route

The alert integration opens the MERIDIAN-9 policy route. RELAY-17 remains the rollout work ticket.

Implication: Identifiers must not be conflated.

### Record 08 — 2034-06-28 — Eli Ramos

Subject: rollback

Rollback restores the previous lifecycle only if AP-17's evidence gate fails; it does not approve MR-42 or any unreviewed extension.

Implication: A rollback branch is not a new approved policy.

## Reading rule

Use the record's status and scope together. A historical value can explain a test fixture, a migration branch, or a rejected request without being an instruction for the current rollout. A display label can be useful to an operator while still being the wrong representation for the policy schema. If two records disagree, follow the later effective approval for this policy and preserve the stated unit.
