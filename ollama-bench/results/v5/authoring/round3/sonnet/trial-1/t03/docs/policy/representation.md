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

## Representation and normalization

Repository role: prevents unit, case, and display-form mistakes

## Evidence ledger

### Record 01 — 2034-06-26 — Jon Bell

Subject: fraction storage

The evaluator reads threshold_fraction as the text 0.82, parses it as a decimal, and compares it to the normalized metric. The UI formatter multiplies by 100 only for display.

Implication: The answer's threshold string must retain 0.82.

### Record 02 — 2034-06-26 — Nora Vale

Subject: date storage

The scheduler stores the committed date as 2034-11-18. A release note's 'November 18' is explanatory prose, not a reason to change the ISO output.

Implication: Use the canonical ISO date.

### Record 03 — 2034-06-26 — Nora Vale

Subject: cadence storage

The policy parser accepts an interval during import but writes the normalized label biweekly into the release manifest.

Implication: Do not return '14 days' when the approved normalized field is a label.

### Record 04 — 2034-06-26 — Carmen Wu

Subject: money storage

The finance adapter stores 47200 as an integer. Currency formatting with a comma is presentation only, and the emergency threshold is a separate control.

Implication: Return a JSON integer.

### Record 05 — 2034-06-26 — Nadia Holt

Subject: retention storage

Primary archive lifecycle receives integer 45. The audit stream receives a shorter lifecycle and the legal-hold service can suspend deletion.

Implication: Select the primary ordinary lifecycle.

### Record 06 — 2034-06-26 — Mara Chen

Subject: identity storage

The owner field stores a person's display name, Mara Chen, while notification groups remain separate metadata.

Implication: Return the named person.

### Record 07 — 2034-06-26 — Facilities

Subject: room storage

The appointment record stores Juniper-2; Juniper is the building zone and Juniper-1 was an earlier draft location.

Implication: Return the exact room label.

### Record 08 — 2034-06-26 — Nora Vale

Subject: code storage

The tracker integration stores MERIDIAN-9 for policy escalations. AP-17 and RELAY-17 are packet and work identifiers, not this field.

Implication: Return the escalation code only.

## Reading rule

Use the record's status and scope together. A historical value can explain a test fixture, a migration branch, or a rejected request without being an instruction for the current rollout. A display label can be useful to an operator while still being the wrong representation for the policy schema. If two records disagree, follow the later effective approval for this policy and preserve the stated unit.
