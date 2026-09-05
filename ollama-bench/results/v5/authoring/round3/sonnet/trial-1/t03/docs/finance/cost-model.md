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

## Finance cost model

Repository role: separates cap, forecast, reserve, and emergency purchasing controls

## Evidence ledger

### Record 01 — 2034-04-04 — Carmen Wu

Subject: forecast A

Storage-only forecast was 45000 dollars. It omitted validation labor and was never an ordinary cap.

Implication: This is a plausible but stale number.

### Record 02 — 2034-05-13 — Carmen Wu

Subject: forecast B

A rounded planning estimate of 48000 dollars included uncertainty reserve. The reserve is not automatically authorized ordinary spend.

Implication: Do not return the rounded estimate.

### Record 03 — 2034-06-18 — Carmen Wu

Subject: validation addendum

Validation for consumer alpha and consumer beta added 2200 dollars to the ordinary implementation package, producing 47200 dollars.

Implication: The approved cap includes this work.

### Record 04 — 2034-06-20 — Mara Chen

Subject: cap vote

The finance component of AP-17 approved a whole-dollar ordinary cap of 47200. The vote excluded emergency incident spending.

Implication: Use integer 47200.

### Record 05 — 2034-06-20 — Procurement

Subject: emergency route

The company-wide purchasing policy can authorize 50000 dollars for an incident. That authority is not the Meridian ordinary cap.

Implication: Scope is the trap.

### Record 06 — 2034-06-27 — Release bot

Subject: config emission

The production manifest contains ordinary_cap_usd: 47200 and source_packet: AP-17. The simulation manifest contains 50000 and is not shipped.

Implication: Build lineage corroborates the approval.

### Record 07 — 2034-06-29 — Carmen Wu

Subject: variance

A forecast may exceed the cap as estimates change; variance reporting does not increase the approved cap.

Implication: Forecast and authorization are different concepts.

### Record 08 — 2034-07-02 — Nora Vale

Subject: audit

The finance audit checks that the cap is whole dollars and that validation labor is included. It does not check the retention or cadence values.

Implication: Use each source for its scope.

## Reading rule

Use the record's status and scope together. A historical value can explain a test fixture, a migration branch, or a rejected request without being an instruction for the current rollout. A display label can be useful to an operator while still being the wrong representation for the policy schema. If two records disagree, follow the later effective approval for this policy and preserve the stated unit.
