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

## Schedule and locations

Repository role: records date and room decisions with their stale alternatives

## Evidence ledger

### Record 01 — 2034-04-12 — Owen Park

Subject: agenda

The agenda proposed 2034-10-31 for a dependency discussion and listed Juniper as a building zone. Both were provisional.

Implication: Agenda material is not the committed schedule.

### Record 02 — 2034-06-20 — Mara Chen

Subject: governance attachment

The approved governance attachment names 2034-11-18 as the committed implementation deadline and Juniper-2 as the verification room.

Implication: These fields are part of AP-17's effective baseline.

### Record 03 — 2034-06-21 — Facilities

Subject: room resolution

Facilities confirmed that Juniper-2 is a room, Juniper is a building zone, and Juniper-1 was unavailable after the earlier planning pass.

Implication: The normalized room includes the number.

### Record 04 — 2034-06-22 — Nora Vale

Subject: dependency check

Archive migration, customer notice, and validation dependencies were all checked before the date was committed.

Implication: The later date is deliberate, not a typo.

### Record 05 — 2034-06-27 — Release bot

Subject: effective marker

The schedule manifest marked 2034-11-18 and Juniper-2 effective with AP-17. A historical calendar export still shows the agenda target.

Implication: Effective marker controls.

### Record 06 — 2034-06-29 — Facilities

Subject: remote attendance

The bridge URI and remote attendee list do not replace the physical review room. They are logistics metadata.

Implication: Do not return a bridge name.

### Record 07 — 2034-07-01 — Mara Chen

Subject: deadline semantics

The date is the implementation commitment, not the date of the next biweekly review and not the date a dry run finishes.

Implication: The field has a precise meaning.

### Record 08 — 2034-07-04 — Nora Vale

Subject: change control

Moving the appointment would require an approved amendment; a calendar edit alone has no policy authority.

Implication: Do not use an unapproved calendar edit.

## Reading rule

Use the record's status and scope together. A historical value can explain a test fixture, a migration branch, or a rejected request without being an instruction for the current rollout. A display label can be useful to an operator while still being the wrong representation for the policy schema. If two records disagree, follow the later effective approval for this policy and preserve the stated unit.
