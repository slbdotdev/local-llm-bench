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

## Runtime architecture

Repository role: describes modules whose configuration must agree with the approved policy

## Evidence ledger

### Record 01 — 2034-06-02 — Priya Shah

Subject: ledger path

Ingress normalizes delivery events, the archive writer persists queryable records, and the retention worker marks records eligible for deletion. The audit stream records movement but is not the customer event archive.

Implication: Retention evidence in audit-only tests cannot answer the primary archive field.

### Record 02 — 2034-06-07 — Eli Ramos

Subject: scheduler

The review scheduler consumes a policy cadence in calendar days and produces a review job; ingestion remains continuous. The scheduler's old weekly fixture is retained to test migration behavior.

Implication: Cadence must come from the effective policy, not the old fixture.

### Record 03 — 2034-06-11 — Priya Shah

Subject: alert path

The normalized late-event fraction is passed to the alert evaluator before any dashboard formatting. The evaluator compares a decimal in [0,1]; the dashboard may show a percent.

Implication: A display value such as 82% is not the canonical fraction string.

### Record 04 — 2034-06-15 — Jon Bell

Subject: configuration boundaries

Finance controls ordinary implementation spend separately from the general purchasing emergency threshold. Governance controls the named owner and committed date.

Implication: Cross-module values need their source and scope reconciled.

### Record 05 — 2034-06-19 — Mara Chen

Subject: verification

The verification review checks archive queryability, deletion eligibility, alert evaluation, scheduler cadence, and evidence ownership in that order. The room is a property of the review appointment.

Implication: A room label in a dashboard or a remote attendee note is not authoritative.

### Record 06 — 2034-06-23 — Eli Ramos

Subject: migration safety

Partition checkpoints carry source watermarks and checksums. Replaying a checkpoint must not duplicate a durable event, but checkpoint age is not an archive retention value.

Implication: Do not mistake operational test durations for retention days.

### Record 07 — 2034-06-27 — Nora Vale

Subject: release lineage

The implementation modules are generated from policy revision P-17.1. They include comments naming prior candidates so auditors can explain why the current constants differ.

Implication: Comments and code must be interpreted with revision status.

### Record 08 — 2034-07-01 — Release bot

Subject: dependency check

All runtime modules resolve the same approval packet identifier; the emergency branch is not imported by the production package.

Implication: The separate override request cannot silently change the baseline.

## Reading rule

Use the record's status and scope together. A historical value can explain a test fixture, a migration branch, or a rejected request without being an instruction for the current rollout. A display label can be useful to an operator while still being the wrong representation for the policy schema. If two records disagree, follow the later effective approval for this policy and preserve the stated unit.
