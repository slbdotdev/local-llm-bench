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

## Draft P-17

Repository role: chronological history showing revisions, status verbs, and the effective boundary

This historical record is retained so the current packet can be distinguished from earlier and rejected branches.

## Evidence ledger

### Record 01 — 2034-05-20 — Nora Vale

Subject: consolidation

Draft P-17 combined archive, schedule, finance, and alert notes for a single baseline.

Implication: draft

### Record 02 — 2034-05-22 — Carmen Wu

Subject: revised estimate

A reserve-inclusive estimate of 48000 dollars was shown beside the ordinary cap discussion.

Implication: estimate

### Record 03 — 2034-05-24 — Nadia Holt

Subject: longer scenario

A 60-day option was discussed as a support compromise, but evidence did not yet settle the baseline.

Implication: discussion

### Record 04 — 2034-05-26 — Jon Bell

Subject: fraction notation

One note wrote 82% while the evaluator design required a normalized fraction.

Implication: unresolved representation

### Record 05 — 2034-05-28 — Mara Chen

Subject: owner review

Governance requested a named person instead of a group alias.

Implication: open requirement

### Record 06 — 2034-05-30 — Owen Park

Subject: date review

The agenda target remained 2034-10-31 pending migration and notice checks.

Implication: not committed

### Record 07 — 2034-06-01 — Facilities

Subject: room review

Juniper-1 was considered before the verification appointment was resolved.

Implication: candidate

### Record 08 — 2034-06-03 — Nora Vale

Subject: status

P-17 remained a draft until the vote and dependency gate; its values must not be read as effective.

Implication: draft

## Reading rule

Use the record's status and scope together. A historical value can explain a test fixture, a migration branch, or a rejected request without being an instruction for the current rollout. A display label can be useful to an operator while still being the wrong representation for the policy schema. If two records disagree, follow the later effective approval for this policy and preserve the stated unit.
