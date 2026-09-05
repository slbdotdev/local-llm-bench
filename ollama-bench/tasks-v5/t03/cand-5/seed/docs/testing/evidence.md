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

## Evidence and validation plan

Repository role: shows how the current release proves each field without making a single answer file

## Evidence ledger

### Record 01 — 2034-06-21 — Ishan Reed

Subject: policy test

The policy test loads the effective packet and asserts biweekly cadence plus 45 ordinary primary-archive days. It also loads old P-16 fixtures to test rejection of stale values.

Implication: Both current and stale material must be distinguished.

### Record 02 — 2034-06-21 — Carmen Wu

Subject: finance test

The finance test asserts integer 47200 and checks that validation labor is included. It separately exercises the 50000 emergency route without importing it.

Implication: Scope and type are both tested.

### Record 03 — 2034-06-21 — Jon Bell

Subject: alert test

The alert test compares decimal 0.82 to the normalized fraction and expects MERIDIAN-9 for policy escalation. It rejects percent-form configuration.

Implication: The string representation is deliberate.

### Record 04 — 2034-06-21 — Mara Chen

Subject: governance test

The governance test requires a named owner and ISO deadline. It rejects a team alias and the 2034-10-31 discussion date.

Implication: Plausible replacements are known failures.

### Record 05 — 2034-06-21 — Facilities

Subject: location test

The location test requires Juniper-2 for the physical verification appointment and ignores remote bridge metadata.

Implication: Room normalization is checkable.

### Record 06 — 2034-06-22 — Nora Vale

Subject: negative test

The suite asserts that MR-42 has no effective approval and that its 90-day, 50000-dollar, and 0.90 values cannot enter the production manifest.

Implication: The emergency proposition is negative.

### Record 07 — 2034-06-23 — Release bot

Subject: lineage test

The evidence job checks that all current modules cite AP-17.1 and that no later effective packet exists in the snapshot.

Implication: Lexical file order is not the authority.

### Record 08 — 2034-06-24 — Nora Vale

Subject: format test

JSON consumers compare parsed objects, so valid whitespace, line endings, and member order do not affect semantics.

Implication: A robust checker should accept formatting variants.

## Reading rule

Use the record's status and scope together. A historical value can explain a test fixture, a migration branch, or a rejected request without being an instruction for the current rollout. A display label can be useful to an operator while still being the wrong representation for the policy schema. If two records disagree, follow the later effective approval for this policy and preserve the stated unit.
