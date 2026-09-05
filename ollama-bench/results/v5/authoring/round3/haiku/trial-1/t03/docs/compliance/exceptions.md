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

## Exceptions and emergency request

Repository role: makes the negative trap explicit while preserving the baseline question

## Evidence ledger

### Record 01 — 2034-06-10 — Ishan Reed

Subject: surge scenario

MR-42 imagined a delivery surge and requested a 90-day primary archive, a 50000-dollar route, and a 0.90 alert line. The scenario was intentionally aggressive.

Implication: All three are tempting alternatives, not baseline values.

### Record 02 — 2034-06-12 — Nadia Holt

Subject: scope objection

Compliance objected that MR-42 mixed legal-hold behavior with ordinary retention and did not define deletion evidence.

Implication: The request was not ready for approval.

### Record 03 — 2034-06-14 — Carmen Wu

Subject: finance objection

Finance said the 50000-dollar emergency route belongs to incident purchasing and cannot be folded into the ordinary cap without a new approval.

Implication: Emergency authority is not ordinary budget.

### Record 04 — 2034-06-16 — Jon Bell

Subject: alert objection

Alerting rejected 0.90 as the policy threshold because it was a dashboard red band, not the normalized trigger chosen for AP-17.

Implication: Visual severity is not policy authority.

### Record 05 — 2034-06-25 — Mara Chen

Subject: disposition

The review board marked MR-42 rejected. No field in AP-17 was changed, and no effective emergency override exists in the release candidate.

Implication: The proposition about approval is negative.

### Record 06 — 2034-06-26 — Nora Vale

Subject: recording rule

A rejected request stays in the archive so an auditor can explain why its values do not appear in production configuration.

Implication: Presence in the tree does not mean adoption.

### Record 07 — 2034-06-28 — Release bot

Subject: branch exclusion

The override-simulation branch fails the effective-packet check and is excluded from relay-7.3.

Implication: Branch material is a decoy.

### Record 08 — 2034-07-02 — Mara Chen

Subject: future change

A real surge would require a new scoped request, named owner, evidence plan, and approval. The current task asks for the baseline in force.

Implication: Do not treat a hypothetical as a change.

## Reading rule

Use the record's status and scope together. A historical value can explain a test fixture, a migration branch, or a rejected request without being an instruction for the current rollout. A display label can be useful to an operator while still being the wrong representation for the policy schema. If two records disagree, follow the later effective approval for this policy and preserve the stated unit.
