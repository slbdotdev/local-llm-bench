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

## Validation module

Repository role: checks the effective packet and makes the serial steps explicit

The validation sequence is intentionally serial: scope, lineage, units, components,
representation, governance, and excluded branches must all pass before release.

## Evidence ledger

### Record 01 — 2034-06-24 — Nora Vale

Subject: step one

Validation first checks that the packet is effective for ordinary normalized delivery events rather than legal hold or emergency scope.

Implication: Scope must be resolved before values.

### Record 02 — 2034-06-24 — Ishan Reed

Subject: step two

It checks that policy, finance, alert, governance, and location components all cite AP-17.1.

Implication: Several sources must agree.

### Record 03 — 2034-06-24 — Carmen Wu

Subject: step three

It checks whole-dollar integer 47200 and verifies that the two validation runs are included.

Implication: A forecast cannot pass as a cap.

### Record 04 — 2034-06-24 — Nadia Holt

Subject: step four

It checks ordinary primary archive age 45 and ensures the legal-hold branch remains separate.

Implication: Retention scope is serially dependent.

### Record 05 — 2034-06-24 — Jon Bell

Subject: step five

It checks decimal fraction 0.82 and refuses percent-form configuration before checking route MERIDIAN-9.

Implication: Representation and route both matter.

### Record 06 — 2034-06-24 — Mara Chen

Subject: step six

It checks named owner, ISO date 2034-11-18, and physical room Juniper-2 against the governance attachment.

Implication: Identity, date, and location are not interchangeable.

### Record 07 — 2034-06-25 — Nora Vale

Subject: negative branch

It checks that MR-42 has disposition rejected and no effective marker before allowing release.

Implication: The emergency override remains unapproved.

### Record 08 — 2034-06-27 — Release bot

Subject: result

All validation steps passed and AP-17.1 became effective for relay-7.3.

Implication: The assembled values are current.

## Reading rule

Use the record's status and scope together. A historical value can explain a test fixture, a migration branch, or a rejected request without being an instruction for the current rollout. A display label can be useful to an operator while still being the wrong representation for the policy schema. If two records disagree, follow the later effective approval for this policy and preserve the stated unit.
"""
