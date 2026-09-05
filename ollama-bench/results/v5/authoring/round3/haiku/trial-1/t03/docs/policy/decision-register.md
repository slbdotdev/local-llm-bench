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

## Decision register

Repository role: indexes the approval packets and their status

## Evidence ledger

### Record 01 — 2034-05-20 — Nora Vale

Subject: P-16

Policy P-16 recorded weekly review, 45000 dollars, 30 days, and a 0.70 warning line as candidates. Status: superseded before production.

Implication: P-16 explains stale fixtures only.

### Record 02 — 2034-06-03 — Mara Chen

Subject: P-17 draft

P-17 draft consolidated the retention and alert proposals and carried placeholders for owner, date, room, and code. Status: draft.

Implication: A draft is not enough to populate the answer.

### Record 03 — 2034-06-24 — Nora Vale

Subject: AP-17

Approval packet AP-17 contains the effective baseline decision for ordinary operation. Its component approvals are cross-referenced by policy, finance, alerting, and governance records.

Implication: This packet is the authority to reconcile, but its fields are intentionally distributed.

### Record 04 — 2034-06-25 — Carmen Wu

Subject: MR-42

Emergency override request MR-42 asks to alter ordinary retention and spend routing during a hypothetical surge. Status: rejected; no effective change.

Implication: The correct proposition about the override is negative.

### Record 05 — 2034-06-27 — Release bot

Subject: relay-7.3

The release candidate pins P-17.1 and AP-17. The branch named override-simulation is excluded from the production build.

Implication: Branch names do not establish authority.

### Record 06 — 2034-06-29 — Nora Vale

Subject: audit rule

A packet can be final in a meeting transcript but not effective until its implementation dependencies and scope are recorded. AP-17 is marked effective for ordinary ledger operation.

Implication: Use effective status and scope.

### Record 07 — 2034-07-01 — Mara Chen

Subject: no amendment

No later approved amendment appears after AP-17 in the current release lineage. The next review is scheduled to evaluate evidence, not to pre-authorize a change.

Implication: Do not invent a later override.

### Record 08 — 2034-07-02 — Nora Vale

Subject: field map

The register maps cadence and retention to the policy module, budget to finance approval, threshold and code to alert approval, and identity/date/location to governance records.

Implication: The map is a navigation aid, not a duplicated answer.

## Reading rule

Use the record's status and scope together. A historical value can explain a test fixture, a migration branch, or a rejected request without being an instruction for the current rollout. A display label can be useful to an operator while still being the wrong representation for the policy schema. If two records disagree, follow the later effective approval for this policy and preserve the stated unit.
