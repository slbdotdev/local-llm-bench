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

## Changelog

Repository role: summarizes the long revision path without replacing the underlying records

## Evidence ledger

### Record 01 — 2034-04-15 — Nora Vale

Subject: P-16

Superseded weekly/45000/30-day draft after validation and ownership gaps were found.

Implication: historical

### Record 02 — 2034-06-03 — Nora Vale

Subject: P-17

Consolidated draft retained open representation and date questions.

Implication: draft

### Record 03 — 2034-06-20 — Mara Chen

Subject: AP-17

Approved the baseline components and attached governance values for correction review.

Implication: approved pending gate

### Record 04 — 2034-06-25 — Mara Chen

Subject: MR-42

Rejected the emergency override request; no baseline mutation.

Implication: rejected

### Record 05 — 2034-06-27 — Release bot

Subject: AP-17.1

Made the baseline effective after all dependency checks passed.

Implication: effective

### Record 06 — 2034-06-28 — Eli Ramos

Subject: runbook

Added checkpoint recovery instructions without changing policy fields.

Implication: implementation only

### Record 07 — 2034-06-29 — Jon Bell

Subject: alert test

Corrected fraction-versus-percent test semantics.

Implication: test only

### Record 08 — 2034-07-03 — Release bot

Subject: current

Confirmed no later effective amendment in the release candidate.

Implication: current

## Reading rule

Use the record's status and scope together. A historical value can explain a test fixture, a migration branch, or a rejected request without being an instruction for the current rollout. A display label can be useful to an operator while still being the wrong representation for the policy schema. If two records disagree, follow the later effective approval for this policy and preserve the stated unit.
