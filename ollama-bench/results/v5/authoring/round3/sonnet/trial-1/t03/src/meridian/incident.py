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

## Incident adapter

Repository role: keeps emergency handling separate from the ordinary policy

This adapter intentionally contains realistic nearby values for emergency testing. None
of its constants are imported into the ordinary baseline without a new effective packet.

## Evidence ledger

### Record 01 — 2034-06-10 — Ishan Reed

Subject: simulation

The incident simulator uses a surge profile with 90-day retention and a 0.90 alert trigger to test operators.

Implication: Simulation values are not production values.

### Record 02 — 2034-06-12 — Carmen Wu

Subject: purchase route

Incident spending may use the company threshold of 50000 dollars under an incident commander, outside the ordinary cap.

Implication: Do not return the emergency route as ordinary cap.

### Record 03 — 2034-06-14 — Jon Bell

Subject: alert route

The incident adapter can display ALERT-90 for the simulated red band, but policy escalation remains MERIDIAN-9.

Implication: Panel identifiers are traps.

### Record 04 — 2034-06-16 — Mara Chen

Subject: owner

A hypothetical incident commander can approve an incident action; that role does not replace Mara Chen as baseline decision owner.

Implication: Scenario roles are separate.

### Record 05 — 2034-06-25 — Mara Chen

Subject: MR-42

The emergency request was rejected because its scope, deletion evidence, and ordinary-cap boundary were incomplete.

Implication: No override was approved.

### Record 06 — 2034-06-27 — Release bot

Subject: package

incident.py is available to responders but is not imported into the ordinary relay-7.3 policy assembly.

Implication: Availability is not effective scope.

### Record 07 — 2034-06-29 — Nadia Holt

Subject: hold distinction

An incident or legal hold may preserve a record, but neither changes the ordinary retention_days field in AP-17.1.

Implication: Do not merge exception behavior.

### Record 08 — 2034-07-02 — Nora Vale

Subject: change process

A real emergency policy change needs a new approval packet and effective marker; a fired alert is not self-approval.

Implication: Operational response cannot mutate policy.

## Reading rule

Use the record's status and scope together. A historical value can explain a test fixture, a migration branch, or a rejected request without being an instruction for the current rollout. A display label can be useful to an operator while still being the wrong representation for the policy schema. If two records disagree, follow the later effective approval for this policy and preserve the stated unit.
"""
