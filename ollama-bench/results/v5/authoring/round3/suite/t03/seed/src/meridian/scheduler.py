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

## Scheduler runtime module

Repository role: current executable source for date and cadence semantics

The runtime export represented here is:

    COMMITTED_DEADLINE = "2034-11-18"

The scheduler's interval arithmetic is an implementation of the cadence, not a replacement
for the normalized cadence label.

## Evidence ledger

### Record 01 — 2034-06-20 — Mara Chen

Subject: commitment

COMMITTED_DEADLINE = '2034-11-18' is the date after archive migration, customer notice, and validation dependencies.

Implication: Return the ISO date.

### Record 02 — 2034-06-20 — Nora Vale

Subject: cadence input

The scheduler reads the normalized biweekly label and expands it to a fourteen-day interval for job creation.

Implication: Do not output the expanded interval for the label field.

### Record 03 — 2034-06-27 — Release bot

Subject: effective schedule

The production manifest carries 2034-11-18; the old agenda export carries 2034-10-31 only as a discussion target.

Implication: Effective schedule outranks agenda material.

### Record 04 — 2034-06-28 — Eli Ramos

Subject: dry run

A dry run is expected to take 36 hours in the largest partition. This is an operational estimate, not a calendar deadline.

Implication: Do not put a duration in deadline.

### Record 05 — 2034-06-29 — Nora Vale

Subject: review date

The next fourteen-day policy review can occur before the committed implementation date. Review cadence and implementation deadline are distinct fields.

Implication: Keep the fields separate.

### Record 06 — 2034-07-01 — Mara Chen

Subject: date parsing

The parser requires ISO year-month-day and rejects locale-dependent forms from old meeting notes.

Implication: Use 2034-11-18 exactly.

### Record 07 — 2034-07-02 — Release bot

Subject: dependency gate

The deadline became effective only after the validation dependency check was green.

Implication: Status matters.

### Record 08 — 2034-07-04 — Nora Vale

Subject: amendment

Changing the date in a calendar does not amend the policy; a new effective packet is required.

Implication: Ignore unapproved edits.

## Reading rule

Use the record's status and scope together. A historical value can explain a test fixture, a migration branch, or a rejected request without being an instruction for the current rollout. A display label can be useful to an operator while still being the wrong representation for the policy schema. If two records disagree, follow the later effective approval for this policy and preserve the stated unit.
"""
