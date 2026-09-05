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

## Compliance interpretation

Repository role: defines ordinary retention versus holds and special streams

## Evidence ledger

### Record 01 — 2034-04-06 — Nadia Holt

Subject: cost comparison

The 30-day scenario was a cost comparison. It was not approved because support investigations frequently begin after the second weekly report.

Implication: A precise scenario can still be rejected.

### Record 02 — 2034-05-17 — Nadia Holt

Subject: ordinary baseline

The compliance recommendation for the primary archive became 45 days after the investigation evidence was reviewed.

Implication: This is the baseline scope.

### Record 03 — 2034-05-18 — Legal

Subject: hold

A legal hold can preserve records beyond ordinary retention. Hold duration is case-specific and not the retention_days field.

Implication: Do not return an indefinite or 90-day hold.

### Record 04 — 2034-06-20 — Mara Chen

Subject: approval

AP-17 approves 45 days of ordinary queryability in the primary archive. It does not modify legal controls.

Implication: The approved value is 45.

### Record 05 — 2034-06-25 — Carmen Wu

Subject: MR-42

Emergency request MR-42 proposed 90 days during a surge. Compliance rejected the request because it lacked a scope, owner, and deletion review.

Implication: The emergency proposal is negative, not a second baseline.

### Record 06 — 2034-06-27 — Release bot

Subject: lifecycle

The current primary lifecycle is 45 days; audit movement logs are deleted sooner under their own control.

Implication: Select primary archive, not audit lifecycle.

### Record 07 — 2034-06-29 — Support

Subject: investigation guide

The guide now says ordinary investigations use queryable records and legal requests use holds. The two paths must not be merged.

Implication: Terminology encodes scope.

### Record 08 — 2034-07-03 — Nadia Holt

Subject: review condition

Future evidence may motivate an amendment, but no amendment is effective in this snapshot.

Implication: Do not predict or invent a change.

## Reading rule

Use the record's status and scope together. A historical value can explain a test fixture, a migration branch, or a rejected request without being an instruction for the current rollout. A display label can be useful to an operator while still being the wrong representation for the policy schema. If two records disagree, follow the later effective approval for this policy and preserve the stated unit.
