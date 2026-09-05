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

## Policy glossary

Repository role: fixes the meaning and representation of each requested field

## Evidence ledger

### Record 01 — 2034-05-03 — Nora Vale

Subject: cadence

A cadence is the interval between policy reviews. The canonical normalized label for a fourteen-day interval is biweekly. Weekly and monthly describe other schedules.

Implication: Use the normalized lower-case label selected by the effective approval.

### Record 02 — 2034-05-04 — Carmen Wu

Subject: budget cap

A budget cap is the maximum ordinary implementation spend in whole US dollars. A forecast, reserve, or company purchasing threshold is not the policy cap.

Implication: Return an integer cap, not a forecast or a formatted amount.

### Record 03 — 2034-05-05 — Nora Vale

Subject: retention

Retention days means ordinary queryability in the primary archive. Legal holds can extend deletion, and the audit stream has its own lifecycle.

Implication: Neither exception should replace the baseline days.

### Record 04 — 2034-05-06 — Jon Bell

Subject: threshold

The alert threshold is a normalized late-event fraction. Its stored form is a decimal string such as 0.82, not a percent string such as 82%.

Implication: Preserve the fractional representation.

### Record 05 — 2034-05-07 — Nora Vale

Subject: decision owner

The decision owner is one named person accountable for cross-team policy decisions. A squad, rotation, or task assignee is not equivalent.

Implication: Return the person's full name from the effective record.

### Record 06 — 2034-05-08 — Nora Vale

Subject: deadline

The deadline is the committed implementation date after dependency review, not an agenda discussion target or a dry-run duration.

Implication: Use the ISO calendar date in the approval.

### Record 07 — 2034-05-09 — Jon Bell

Subject: room

Room is the physical location of the verification review. Remote participation does not change it, and a shortened display label is not canonical.

Implication: Use the exact normalized room label.

### Record 08 — 2034-05-10 — Nora Vale

Subject: escalation code

The escalation code joins the policy alert to the incident tracker. It is not a dashboard name, ticket number, or purchasing route.

Implication: Return the code assigned by the effective approval.

## Reading rule

Use the record's status and scope together. A historical value can explain a test fixture, a migration branch, or a rejected request without being an instruction for the current rollout. A display label can be useful to an operator while still being the wrong representation for the policy schema. If two records disagree, follow the later effective approval for this policy and preserve the stated unit.
