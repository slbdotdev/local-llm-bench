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

## Approval minutes

Repository role: captures the vote and the boundaries around it

## Evidence ledger

### Record 01 — 2034-06-20 — Mara Chen

Subject: motion

The chair moved approval of a regular fourteen-day policy review, with ordinary implementation spending capped after validation costs were included. The motion was for the baseline, not the emergency request.

Implication: Read the motion with the later component records.

### Record 02 — 2034-06-20 — Carmen Wu

Subject: cost correction

Finance corrected the ordinary cap from 45000 to 47200 dollars after adding two legacy-consumer validation runs. The corrected amount was accepted into AP-17.

Implication: The correction is authoritative for the cap.

### Record 03 — 2034-06-20 — Nadia Holt

Subject: retention motion

The group selected 45 days for ordinary primary-archive queryability. The 90-day legal-hold scenario remains under legal controls and is not ordinary retention.

Implication: Scope prevents the plausible 90-day substitution.

### Record 04 — 2034-06-20 — Jon Bell

Subject: fraction motion

The alert motion selected 0.82 of the normalized late-event fraction. The display may render 82 percent, but the policy record keeps 0.82.

Implication: Use the stored scale.

### Record 05 — 2034-06-20 — Nora Vale

Subject: vote

The baseline motion passed and was assigned packet AP-17. The minutes record the vote; they do not authorize the separately tabled MR-42 request.

Implication: A passed baseline and a rejected override coexist.

### Record 06 — 2034-06-21 — Mara Chen

Subject: correction window

A 24-hour correction window was offered. No correction changed the approved values. The implementation location and owner were confirmed in the governance attachment.

Implication: Later confirmation beats informal earlier wording.

### Record 07 — 2034-06-22 — Nora Vale

Subject: effective condition

The chair required schema, runbook, and dependency checks before AP-17 became effective. The release bot recorded those checks as complete on June 27.

Implication: Meeting approval alone is not the whole status trail.

### Record 08 — 2034-06-23 — Carmen Wu

Subject: exception boundary

Emergency spending follows company incident procedure and does not increase the ordinary cap. MR-42 was left rejected after the surge scenario was reviewed.

Implication: Do not turn an exception route into a baseline value.

## Reading rule

Use the record's status and scope together. A historical value can explain a test fixture, a migration branch, or a rejected request without being an instruction for the current rollout. A display label can be useful to an operator while still being the wrong representation for the policy schema. If two records disagree, follow the later effective approval for this policy and preserve the stated unit.
