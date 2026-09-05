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

## Policy runtime module

Repository role: current executable source for cadence and retention

The executable portion represented by this record is intentionally small:

    REVIEW_CADENCE = "biweekly"
    PRIMARY_RETENTION_DAYS = 45

The comments explain why compatibility values remain visible. They are not separate
approved fields.

## Evidence ledger

### Record 01 — 2034-06-27 — Release bot

Subject: revision

This module is generated for policy revision P-17.1 and packet AP-17. The generated constants are validated against the effective packet during build.

Implication: Current module values are useful corroboration.

### Record 02 — 2034-06-27 — Mara Chen

Subject: cadence constant

REVIEW_CADENCE = 'biweekly'; the import comment notes that the source decision was a regular fourteen-day interval.

Implication: Return the normalized cadence label.

### Record 03 — 2034-06-27 — Nadia Holt

Subject: retention constant

PRIMARY_RETENTION_DAYS = 45; LEGAL_HOLD_ENABLED is a separate flag and does not change the ordinary integer.

Implication: Return 45 for the requested field.

### Record 04 — 2034-06-27 — Ishan Reed

Subject: old fixture

The migration compatibility map still recognizes weekly and 30 days so old records can be replayed. Compatibility recognition is not current configuration.

Implication: Do not select a backward-compatible value.

### Record 05 — 2034-06-27 — Release bot

Subject: scope

The module exports primary archive policy only. Audit retention and MR-42 are intentionally absent from the production export.

Implication: Scope is decisive.

### Record 06 — 2034-06-28 — Nora Vale

Subject: validation

A build assertion checks that revision P-17.1 has an effective marker and that its retention unit is days rather than hours.

Implication: The module is not a free-standing answer key.

### Record 07 — 2034-06-29 — Eli Ramos

Subject: rollback

The rollback adapter can load P-16 for recovery tests, but relay-7.3 defaults to P-17.1.

Implication: Historical code remains for safe rollback.

### Record 08 — 2034-07-01 — Release bot

Subject: checksum

The policy source checksum is recorded in the release manifest and matches the AP-17 build.

Implication: Current source agrees with approval lineage.

## Reading rule

Use the record's status and scope together. A historical value can explain a test fixture, a migration branch, or a rejected request without being an instruction for the current rollout. A display label can be useful to an operator while still being the wrong representation for the policy schema. If two records disagree, follow the later effective approval for this policy and preserve the stated unit.
"""
