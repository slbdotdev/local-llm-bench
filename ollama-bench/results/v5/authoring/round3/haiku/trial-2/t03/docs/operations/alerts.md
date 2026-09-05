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

## Alerting module notes

Repository role: distinguishes policy triggers, dashboard bands, and incident routes

## Evidence ledger

### Record 01 — 2034-05-11 — Jon Bell

Subject: prototype

The prototype paged at 0.75 but called it a warning. This was an experiment and was removed from the production evaluator.

Implication: A historical match is not authority by itself.

### Record 02 — 2034-05-19 — Jon Bell

Subject: dashboard

The dashboard displayed 75%, 82%, and 90% bands in different panels while the policy review was open. Panel color and label do not determine the trigger.

Implication: Read the policy evaluator source and approval.

### Record 03 — 2034-06-20 — Jon Bell

Subject: approved trigger

AP-17 selects threshold_fraction 0.82 for normalized late events. The on-call route is selected separately.

Implication: The requested field is the fraction string.

### Record 04 — 2034-06-27 — Release bot

Subject: compiled config

The release build emits late_event_fraction: '0.82' and escalation_route: MERIDIAN-9. It does not emit the emergency branch's 0.90.

Implication: Current compiled settings corroborate the approval.

### Record 05 — 2034-06-30 — Ishan Reed

Subject: false positive review

A test that compares 82 to a fraction of 0.82 is invalid because it mixes percent and fraction scales. The test was corrected to parse the canonical decimal.

Implication: Do not normalize by guesswork.

### Record 06 — 2034-07-01 — Jon Bell

Subject: route naming

MERIDIAN-9 is the policy escalation code; ALERT-90 is a dashboard panel identifier and INC-204 is an incident example.

Implication: Nearby identifiers are traps.

### Record 07 — 2034-07-02 — Nora Vale

Subject: severity

The threshold opens the policy route but does not by itself authorize emergency retention or emergency spending.

Implication: Alert semantics do not change policy scope.

### Record 08 — 2034-07-03 — Mara Chen

Subject: review

The next cadence review evaluates noise and freshness; it is not an amendment unless a new packet is approved and made effective.

Implication: Do not infer a future change.

## Reading rule

Use the record's status and scope together. A historical value can explain a test fixture, a migration branch, or a rejected request without being an instruction for the current rollout. A display label can be useful to an operator while still being the wrong representation for the policy schema. If two records disagree, follow the later effective approval for this policy and preserve the stated unit.
