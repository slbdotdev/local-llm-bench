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

## Rollout brief and discarded alternatives

Repository role: records what was considered before approval

## Evidence ledger

### Record 01 — 2034-04-02 — Owen Park

Subject: cadence draft

The first draft proposed weekly review during the migration, arguing that early growth should be caught quickly. The draft was circulated for comment and had no approval marker.

Implication: A supported proposal is not an approved cadence.

### Record 02 — 2034-04-04 — Carmen Wu

Subject: finance draft

The first ordinary cap estimate was 45000 dollars, excluding validation work for the two legacy consumers. It was labelled forecast, not cap.

Implication: Do not use the rounded forecast.

### Record 03 — 2034-04-06 — Nadia Holt

Subject: retention draft

Compliance initially modelled 30 days for cost comparison and separately discussed 90 days for a legal-hold scenario. Neither number was adopted as ordinary retention in this brief.

Implication: Scope and status distinguish the candidates.

### Record 04 — 2034-04-08 — Jon Bell

Subject: alert draft

The dashboard mock used an amber warning at 0.70 and a red line at 0.90. The policy trigger was still open.

Implication: Dashboard lines are not the approved trigger.

### Record 05 — 2034-04-10 — Nora Vale

Subject: owner draft

The on-call rotation and the Relay Platform team were listed as operational contacts. Governance requested a named decision owner before approval.

Implication: A group alias is not the requested owner field.

### Record 06 — 2034-04-12 — Owen Park

Subject: date draft

The agenda placed a discussion target on 2034-10-31 so dependencies could be reviewed. It was explicitly not a committed delivery date.

Implication: Do not copy the agenda target.

### Record 07 — 2034-04-14 — Jon Bell

Subject: location draft

The agenda export shortened the location to Juniper. Facilities later resolved the room number for the verification review.

Implication: The abbreviated label is incomplete.

### Record 08 — 2034-04-16 — Ishan Reed

Subject: code draft

A ticket reference RELAY-17 appeared in the rollout checklist. It links the work item but is not the escalation code.

Implication: Identifiers have different purposes.

## Reading rule

Use the record's status and scope together. A historical value can explain a test fixture, a migration branch, or a rejected request without being an instruction for the current rollout. A display label can be useful to an operator while still being the wrong representation for the policy schema. If two records disagree, follow the later effective approval for this policy and preserve the stated unit.
