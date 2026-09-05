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

## Governance runtime module

Repository role: current executable source for owner and decision boundaries

The runtime export represented here is:

    DECISION_OWNER = "Mara Chen"

The assignee list is intentionally not an owner list.

## Evidence ledger

### Record 01 — 2034-06-20 — Nora Vale

Subject: named owner

DECISION_OWNER = 'Mara Chen' is recorded in the governance attachment to AP-17.

Implication: Return the named person.

### Record 02 — 2034-06-20 — Mara Chen

Subject: team contacts

Relay Platform and the on-call rotation are notification and execution contacts. They are not the decision-owner value.

Implication: Do not return an alias or rotation.

### Record 03 — 2034-06-21 — Mara Chen

Subject: accountability

The owner coordinates evidence, approves dependency interpretation, and requests an amendment when required.

Implication: This is policy accountability, not a task assignee.

### Record 04 — 2034-06-27 — Release bot

Subject: effective export

The production governance object names Mara Chen and references AP-17. The simulation object names an incident commander for hypothetical use.

Implication: Exclude simulation data.

### Record 05 — 2034-06-28 — Nora Vale

Subject: action item

Eli Ramos owns the checkpoint test and Nadia Holt owns the compliance note. Their action ownership does not replace the accountable owner.

Implication: Distinguish roles.

### Record 06 — 2034-06-29 — Mara Chen

Subject: stability

The decision-owner field remains stable if the implementation team changes; team membership is mutable metadata.

Implication: Return the person's name.

### Record 07 — 2034-07-01 — Nora Vale

Subject: escalation

Cross-module disagreement is escalated to Mara Chen through MERIDIAN-9, but the code and the owner are separate fields.

Implication: Do not merge fields.

### Record 08 — 2034-07-03 — Release bot

Subject: checksum

The governance export checksum matches the effective approval packet.

Implication: Current source is authoritative within scope.

## Reading rule

Use the record's status and scope together. A historical value can explain a test fixture, a migration branch, or a rejected request without being an instruction for the current rollout. A display label can be useful to an operator while still being the wrong representation for the policy schema. If two records disagree, follow the later effective approval for this policy and preserve the stated unit.
"""
